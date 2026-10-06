"""Aggregate a run into results/<run-id>/summary.json and summary.md.

Statistics are clustered by prompt: runs (and models, in the pooled view) of the same
prompt are averaged first, so each prompt counts once in tests and intervals.

Usage:
  uv run measure.py --run-id full
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics as st
from collections import defaultdict
from pathlib import Path

from lint import lint

ROOT = Path(__file__).resolve().parent
ARMS = ["baseline", "llano"]
VIOLATIONS = ["long_sentence", "semicolon", "long_paragraph", "banned_filler", "avoid_word", "stacked_hedges", "gerund_chain"]


# ---------- statistics ----------

def sign_test(wins: int, losses: int) -> float:
    """Two-sided exact sign test, ties excluded."""
    n = wins + losses
    if n == 0:
        return 1.0
    k = max(wins, losses)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n)


def bootstrap(values: list[float], stat=st.mean, n: int = 5000, seed: int = 7) -> tuple[float, float]:
    """95% percentile CI, resampling clusters (one value per prompt)."""
    if len(values) < 2:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    xs = sorted(stat(rng.choices(values, k=len(values))) for _ in range(n))
    return xs[int(0.025 * n)], xs[int(0.975 * n)]


# ---------- loading ----------

def load(run_id: str):
    snaps = [json.loads(p.read_text()) for p in sorted((ROOT / "snapshots" / run_id).glob("*/*/*.json"))]
    judge = ROOT / "judge" / run_id
    fid = {(d["model_alias"], d["arm"], d["prompt_id"], d["run"]): d
           for d in (json.loads(p.read_text()) for p in (judge / "fidelity").glob("*/*/*.json"))}
    pw = [json.loads(p.read_text()) for p in (judge / "pairwise").glob("*/*.json")]
    meta = json.loads((ROOT / "snapshots" / run_id / "meta.json").read_text())
    return snaps, fid, pw, meta


def text_metrics(text: str) -> dict:
    rep = lint(text)
    return {"words": rep.words, "per100": rep.per_100, "inflesz": rep.inflesz, "violations": rep.violations}


def rows_single(snaps, fid):
    rows = []
    for s in snaps:
        if s.get("kind", "single") != "single":
            continue
        f = fid.get((s["model_alias"], s["arm"], s["prompt_id"], s["run"]))
        rows.append({
            **{k: s[k] for k in ("model_alias", "arm", "prompt_id", "category", "run", "input_tokens")},
            "visible_tokens": (s["output_tokens"] or 0) - (s["thinking_tokens"] or 0),
            "output_tokens": s["output_tokens"] or 0, "thinking_tokens": s["thinking_tokens"] or 0,
            **text_metrics(s["text"]),
            "fidelity": sum(f["facts"]) / f["n_facts"] if f else None,
            "incorrect": f["incorrect_claims"] if f else None,
        })
    return rows


def rows_turns(snaps, fid):
    rows = []
    for s in snaps:
        if s.get("kind") != "conversation":
            continue
        f = fid.get((s["model_alias"], s["arm"], s["prompt_id"], s["run"]))
        for i, t in enumerate(s["turns"]):
            kept = f["facts_by_turn"][i] if f and i < len(f["facts_by_turn"]) else None
            n = f["n_facts_by_turn"][i] if f else None
            rows.append({
                **{k: s[k] for k in ("model_alias", "arm", "prompt_id", "run")}, "turn": i + 1,
                "visible_tokens": (t["output_tokens"] or 0) - (t["thinking_tokens"] or 0),
                "output_tokens": t["output_tokens"] or 0, "thinking_tokens": t["thinking_tokens"] or 0,
                **text_metrics(t["text"]),
                "fidelity": sum(kept) / n if kept is not None and n else None,
            })
    return rows


# ---------- aggregation ----------

def arm_stats(rows):
    if not rows:
        return None
    fids = [r["fidelity"] for r in rows if r["fidelity"] is not None]
    words_total = sum(r["words"] for r in rows) or 1
    return {
        "n": len(rows),
        "words_median": st.median(r["words"] for r in rows),
        "visible_tokens_median": st.median(r["visible_tokens"] for r in rows),
        "output_tokens_median": st.median(r["output_tokens"] for r in rows),
        "thinking_share": sum(r["thinking_tokens"] for r in rows) / max(sum(r["output_tokens"] for r in rows), 1),
        "per100_mean": st.mean(r["per100"] for r in rows),
        "inflesz_mean": st.mean(r["inflesz"] for r in rows if r["inflesz"] is not None),
        "fidelity_mean": st.mean(fids) if fids else None,
        "incorrect_total": sum(r.get("incorrect") or 0 for r in rows),
        "input_tokens_median": st.median(r["input_tokens"] for r in rows) if "input_tokens" in rows[0] else None,
        "violations_per100": {v: 100 * sum(r["violations"][v] for r in rows) / words_total for v in VIOLATIONS},
    }


def by_prompt(rows, key):
    """prompt -> arm -> mean of key over runs (and models)."""
    acc = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r[key] is not None:
            acc[r["prompt_id"]][r["arm"]].append(r[key])
    return {p: {a: st.mean(v) for a, v in d.items()} for p, d in acc.items() if all(a in d for a in ARMS)}


def paired(rows, key, lower_is_better=True):
    """Clustered comparison of llano vs baseline on a numeric metric."""
    bp = by_prompt(rows, key)
    better = sum((d["llano"] < d["baseline"]) if lower_is_better else (d["llano"] > d["baseline"]) for d in bp.values())
    worse = sum((d["llano"] > d["baseline"]) if lower_is_better else (d["llano"] < d["baseline"]) for d in bp.values())
    diffs = [d["llano"] - d["baseline"] for d in bp.values()]
    ratios = [d["llano"] / d["baseline"] - 1 for d in bp.values() if d["baseline"]]
    return {
        "prompts": len(bp), "better": better, "equal": len(bp) - better - worse, "worse": worse,
        "p_sign": sign_test(better, worse),
        "mean_diff": st.mean(diffs) if diffs else None, "mean_diff_ci95": list(bootstrap(diffs)),
        "median_ratio": st.median(ratios) if ratios else None, "median_ratio_ci95": list(bootstrap(ratios, st.median)),
    }


def preference(pw):
    """Clustered blind preference: each prompt's win share over its runs (and models)."""
    acc = defaultdict(lambda: [0, 0, 0])  # llano, tie, baseline
    for p in pw:
        acc[p["prompt_id"]][{"llano": 0, "tie": 1, "baseline": 2}[p["winner"]]] += 1
    shares = [w / (w + l) for w, _, l in acc.values() if w + l]
    prompt_wins = sum(s > 0.5 for s in shares)
    prompt_losses = sum(s < 0.5 for s in shares)
    total = [sum(x[i] for x in acc.values()) for i in range(3)]
    return {
        "comparisons": len(pw), "llano": total[0], "tie": total[1], "baseline": total[2],
        "win_rate": total[0] / (total[0] + total[2]) if total[0] + total[2] else None,
        "win_rate_ci95_clustered": list(bootstrap(shares)),
        "prompts": len(acc), "prompts_llano": prompt_wins, "prompts_baseline": prompt_losses,
        "prompts_even": len(shares) - prompt_wins - prompt_losses,
        "p_sign_clustered": sign_test(prompt_wins, prompt_losses),
    }


def summarize(single, turns, pw):
    s = {"single": {}, "conversation": {}}
    if single:
        s["single"] = {
            "arms": {a: arm_stats([r for r in single if r["arm"] == a]) for a in ARMS},
            "violations": paired(single, "per100"),
            "inflesz": paired(single, "inflesz", lower_is_better=False),
            "fidelity": paired(single, "fidelity", lower_is_better=False),
            "words": paired(single, "words"),
            "output_tokens": paired(single, "output_tokens"),
            "preference": preference([p for p in pw if p["kind"] == "single"]),
        }
    if turns:
        s["conversation"] = {
            "by_turn": {t: {a: arm_stats([r for r in turns if r["arm"] == a and r["turn"] == t]) for a in ARMS}
                        for t in sorted({r["turn"] for r in turns})},
            "violations": paired(turns, "per100"),
            "fidelity": paired(turns, "fidelity", lower_is_better=False),
            "preference": preference([p for p in pw if p["kind"] == "conversation"]),
        }
    return s


# ---------- output ----------

def pct(x, signed=True):
    if x is None or x != x:
        return "--"
    return f"{100 * x:+.0f}%" if signed else f"{100 * x:.0f}%"


def markdown(summary) -> str:
    meta = summary["meta"]
    out = [f"# Results: {meta['run_id']}", "",
           f"Claude Code {meta['claude_cli']}. Models: {', '.join(meta['models'])}. Runs: {meta['runs']}. "
           f"Judge: {summary['judge_model'] or '--'}.", ""]
    for scope, s in summary["scopes"].items():
        out.append(f"## {scope}")
        if s["single"]:
            A, sg, pref = s["single"]["arms"], s["single"], s["single"]["preference"]
            row = lambda label, f: f"| {label} | {f(A['baseline'])} | {f(A['llano'])} |"  # noqa: E731
            out += ["", "### Single turn", "", "| | Baseline | Llano |", "|---|---:|---:|",
                    row("Words (median)", lambda a: f"{a['words_median']:.0f}"),
                    row("Visible tokens (median)", lambda a: f"{a['visible_tokens_median']:.0f}"),
                    row("Output tokens incl. thinking (median)", lambda a: f"{a['output_tokens_median']:.0f}"),
                    row("Thinking share of output", lambda a: pct(a["thinking_share"], False)),
                    row("Violations / 100 words", lambda a: f"{a['per100_mean']:.2f}"),
                    row("INFLESZ", lambda a: f"{a['inflesz_mean']:.1f}"),
                    row("Key facts kept", lambda a: pct(a["fidelity_mean"], False)),
                    row("Wrong claims (total)", lambda a: f"{a['incorrect_total']}"),
                    row("Input tokens (median)", lambda a: f"{a['input_tokens_median']:.0f}"),
                    "",
                    f"- **Blind preference:** llano {pref['llano']}, tie {pref['tie']}, baseline {pref['baseline']}. "
                    f"Win rate {pct(pref['win_rate'], False)} (clustered CI {pct(pref['win_rate_ci95_clustered'][0], False)}"
                    f"–{pct(pref['win_rate_ci95_clustered'][1], False)}). By prompt: {pref['prompts_llano']} llano, "
                    f"{pref['prompts_baseline']} baseline, {pref['prompts_even']} even, p = {pref['p_sign_clustered']:.4f}.",
                    f"- **Violations:** lower with llano in {sg['violations']['better']} of {sg['violations']['prompts']} "
                    f"prompts, higher in {sg['violations']['worse']} (p = {sg['violations']['p_sign']:.4f}).",
                    f"- **Fidelity:** llano − baseline = {pct(sg['fidelity']['mean_diff'])} "
                    f"[{pct(sg['fidelity']['mean_diff_ci95'][0])}, {pct(sg['fidelity']['mean_diff_ci95'][1])}].",
                    f"- **Words:** {pct(sg['words']['median_ratio'])} "
                    f"[{pct(sg['words']['median_ratio_ci95'][0])}, {pct(sg['words']['median_ratio_ci95'][1])}].",
                    f"- **Output tokens incl. thinking:** {pct(sg['output_tokens']['median_ratio'])} "
                    f"[{pct(sg['output_tokens']['median_ratio_ci95'][0])}, {pct(sg['output_tokens']['median_ratio_ci95'][1])}]."]
        if s["conversation"]:
            c, pref = s["conversation"], s["conversation"]["preference"]
            out += ["", "### Conversations", "",
                    "| Turn | Viol./100 baseline | Viol./100 llano | Facts baseline | Facts llano |", "|---:|---:|---:|---:|---:|"]
            for t, d in c["by_turn"].items():
                out.append(f"| {t} | {d['baseline']['per100_mean']:.2f} | {d['llano']['per100_mean']:.2f} | "
                           f"{pct(d['baseline']['fidelity_mean'], False)} | {pct(d['llano']['fidelity_mean'], False)} |")
            out += ["", f"- **Blind preference (whole conversation):** llano {pref['llano']}, tie {pref['tie']}, "
                        f"baseline {pref['baseline']}. By conversation: {pref['prompts_llano']} llano, "
                        f"{pref['prompts_baseline']} baseline, p = {pref['p_sign_clustered']:.4f}."]
        out.append("")
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args()
    snaps, fid, pw, meta = load(args.run_id)
    single, turns = rows_single(snaps, fid), rows_turns(snaps, fid)
    models = sorted({r["model_alias"] for r in single + turns})
    scopes = {"All models": summarize(single, turns, pw)}
    for m in models:
        scopes[m] = summarize([r for r in single if r["model_alias"] == m], [r for r in turns if r["model_alias"] == m],
                              [p for p in pw if p["model_alias"] == m])
    judge_models = sorted(({p.get("judge_model") for p in pw} | {f.get("judge_model") for f in fid.values()}) - {None})
    summary = {"meta": meta, "judge_model": ", ".join(judge_models), "scopes": scopes}
    out = ROOT / "results" / args.run_id
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    md = markdown(summary)
    (out / "summary.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
