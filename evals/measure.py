"""Aggregate an eval v2 run into results/<run-id>/summary.json and summary.md.

Metrics follow llano's promises: concise, not verbose, direct, self-sufficient (no need
to ask again), no information lost, and diagrams that pay for their tokens.
Statistics are clustered by prompt: runs (and models, in the pooled view) of the same
prompt are averaged first, so each prompt counts once in tests and intervals.

Usage:
  uv run measure.py --run-id v2
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import statistics as st
from collections import defaultdict
from pathlib import Path

from lint import lint

ROOT = Path(__file__).resolve().parent
DIAGRAM = re.compile(r"```(?:mermaid)?[^\n]*\n(?:(?!```).)*?(?:[─│┌┐└┘├┤┬┴┼▶◀▼▲]|-->|->|<-|\|\s*\n\s*v\b|==>)(?:(?!```).)*?```", re.S)


# ---------- statistics ----------

def sign_test(wins: int, losses: int) -> float:
    n = wins + losses
    if n == 0:
        return 1.0
    k = max(wins, losses)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n)


def bootstrap(values: list[float], stat=st.mean, n: int = 5000, seed: int = 7) -> list[float]:
    if len(values) < 2:
        return [float("nan"), float("nan")]
    rng = random.Random(seed)
    xs = sorted(stat(rng.choices(values, k=len(values))) for _ in range(n))
    return [xs[int(0.025 * n)], xs[int(0.975 * n)]]


def mean(xs):
    xs = [x for x in xs if x is not None]
    return st.mean(xs) if xs else None


# ---------- per-response metrics ----------

def diagram_share(text: str) -> tuple[bool, float]:
    blocks = DIAGRAM.findall(text)
    return bool(blocks), sum(len(b) for b in blocks) / max(len(text), 1)


def text_metrics(text: str) -> dict:
    rep = lint(text)
    has_diag, diag_share = diagram_share(text)
    return {"words": rep.words, "per100": rep.per_100, "inflesz": rep.inflesz,
            "filler": rep.violations["banned_filler"], "has_diagram": has_diag, "diagram_share": diag_share}


def token_metrics(out: int | None, think: int | None) -> dict:
    out, think = out or 0, think or 0
    return {"output_tokens": out, "thinking_tokens": think, "visible_tokens": out - think}


def fidelity(facts: list[dict]) -> tuple[float, float, float]:
    """(score 0..1, kept facts, share of quotes that failed verification)."""
    if not facts:
        return None, None, None
    kept = sum(f["score"] for f in facts)
    unverified = sum(1 for f in facts if not f["verified"]) / len(facts)
    return kept / len(facts), kept, unverified


def load(run_id: str):
    j = ROOT / "judge" / run_id
    rd = lambda p: [json.loads(x.read_text()) for x in sorted(p.glob("**/*.json"))] if p.exists() else []  # noqa: E731
    snaps = rd(ROOT / "snapshots" / run_id)
    snaps = [s for s in snaps if "kind" in s]  # skip meta.json
    key = lambda d: (d["model_alias"], d["arm"], d["prompt_id"], d["run"])  # noqa: E731
    analysis = {key(d): d for d in rd(j / "analysis")}
    reader = {key(d): d for d in rd(j / "reader")}
    floor = {d["prompt_id"]: d for d in rd(j / "floor")}
    pairwise = rd(j / "pairwise")
    meta = json.loads((ROOT / "snapshots" / run_id / "meta.json").read_text())
    return snaps, analysis, reader, floor, pairwise, meta


def build_rows(snaps, analysis, reader, floor):
    single, turns = [], []
    for s in snaps:
        k = (s["model_alias"], s["arm"], s["prompt_id"], s["run"])
        a, r = analysis.get(k), reader.get(k)
        base = {"model": s["model_alias"], "arm": s["arm"], "prompt_id": s["prompt_id"], "run": s["run"]}
        fl = floor.get(s["prompt_id"])
        valid = [not c for c in fl["correct"]] if fl else None  # questions the reader cannot answer without the text
        reader_m = {}
        if r:
            reader_m = {"self_sufficiency": mean([1.0 if c else 0.0 for c in r["correct"]]),
                        "self_sufficiency_valid": mean([1.0 if c else 0.0 for c, v in zip(r["correct"], valid or r["correct"]) if v]) if valid else None,
                        "not_said": mean([1.0 if n else 0.0 for n in r["not_said"]])}
        wrong = sum(1 for c in (a or {}).get("incorrect_claims", []) if c["verified"]) if a else None
        if s["kind"] == "single":
            fid, kept, unver = fidelity(a["facts"]) if a else (None, None, None)
            m = text_metrics(s["text"])
            single.append(base | m | token_metrics(s["output_tokens"], s["thinking_tokens"]) | reader_m | {
                "input_tokens": s["input_tokens"], "fidelity": fid, "unverified": unver, "wrong": wrong,
                "words_per_fact": m["words"] / kept if kept else None,
                "answer_first": (1.0 if a["answer_first"] else 0.0) if a else None,
                "diagram_verdict": a["diagram"] if a else None,
            })
        else:
            for i, t in enumerate(s["turns"]):
                at = a["turns"][i] if a and i < len(a["turns"]) else None
                fid, kept, unver = fidelity(at["facts"]) if at else (None, None, None)
                m = text_metrics(t["text"])
                turns.append(base | {"turn": i + 1} | m | token_metrics(t["output_tokens"], t["thinking_tokens"]) | {
                    "fidelity": fid, "unverified": unver, "words_per_fact": m["words"] / kept if kept else None,
                    "answer_first": (1.0 if at["answer_first"] else 0.0) if at else None,
                    "diagram_verdict": at["diagram"] if at else None,
                    # conversation-level values, repeated on each turn row
                    "conv_wrong": wrong, **{f"conv_{k}": v for k, v in reader_m.items()},
                })
    return single, turns


# ---------- aggregation ----------

METRICS = [  # (key, label, lower is better)
    ("words", "Words (median)", True),
    ("output_tokens", "Output tokens incl. thinking (median)", True),
    ("visible_tokens", "Visible tokens (median)", True),
    ("words_per_fact", "Words per kept fact (median)", True),
    ("filler", "Filler phrases per answer", True),
    ("answer_first", "First sentence answers", False),
    ("self_sufficiency", "Self-sufficiency (reader correct)", False),
    ("self_sufficiency_valid", "Self-sufficiency, questions not known without text", False),
    ("fidelity", "Key facts kept (verified)", False),
    ("wrong", "Wrong claims per answer (verified)", True),
    ("per100", "Rule violations / 100 words", True),
    ("inflesz", "INFLESZ", False),
]
MEDIAN_KEYS = {"words", "output_tokens", "visible_tokens", "words_per_fact"}


def arm_stats(rows):
    if not rows:
        return None
    out = {"n": len(rows)}
    for k, _, _ in METRICS:
        vals = [r.get(k) for r in rows if r.get(k) is not None]
        out[k] = (st.median(vals) if k in MEDIAN_KEYS else st.mean(vals)) if vals else None
    out["thinking_share"] = sum(r["thinking_tokens"] for r in rows) / max(sum(r["output_tokens"] for r in rows), 1)
    out["input_tokens"] = st.median(r["input_tokens"] for r in rows) if "input_tokens" in rows[0] else None
    out["diagram_rate"] = mean([1.0 if r["has_diagram"] else 0.0 for r in rows])
    with_d = [r for r in rows if r["has_diagram"]]
    out["diagram_token_share"] = mean([r["diagram_share"] for r in with_d])
    verdicts = [r["diagram_verdict"] for r in rows if r.get("diagram_verdict") not in (None, "none")]
    out["diagram_verdicts"] = {v: verdicts.count(v) for v in ("correct", "incorrect", "redundant")}
    out["unverified_quotes"] = mean([r.get("unverified") for r in rows])
    return out


def paired(rows, key, arm_a, arm_b, lower_is_better):
    acc = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r.get(key) is not None and r["arm"] in (arm_a, arm_b):
            acc[r["prompt_id"]][r["arm"]].append(r[key])
    bp = [{a: st.mean(v) for a, v in d.items()} for d in acc.values() if arm_a in d and arm_b in d]
    if not bp:
        return None
    better = sum((d[arm_a] < d[arm_b]) if lower_is_better else (d[arm_a] > d[arm_b]) for d in bp)
    worse = sum((d[arm_a] > d[arm_b]) if lower_is_better else (d[arm_a] < d[arm_b]) for d in bp)
    diffs = [d[arm_a] - d[arm_b] for d in bp]
    return {"prompts": len(bp), "better": better, "worse": worse, "equal": len(bp) - better - worse,
            "p_sign": sign_test(better, worse), "mean_diff": st.mean(diffs), "ci95": bootstrap(diffs)}


def preference(pw, other):
    acc = defaultdict(lambda: [0, 0, 0])  # llano, tie, other
    for p in pw:
        if p["other"] == other:
            acc[p["prompt_id"]][{"llano": 0, "tie": 1}.get(p["winner"], 2)] += 1
    if not acc:
        return None
    total = [sum(x[i] for x in acc.values()) for i in range(3)]
    scores = [(w + 0.5 * t) / (w + t + l) for w, t, l in acc.values()]  # ties count half
    wins = sum(s > 0.5 for s in scores)
    losses = sum(s < 0.5 for s in scores)
    return {"llano": total[0], "tie": total[1], "other": total[2], "score": mean(scores), "score_ci95": bootstrap(scores),
            "prompts_llano": wins, "prompts_other": losses, "prompts_even": len(scores) - wins - losses,
            "p_sign": sign_test(wins, losses)}


def summarize(single, turns, pw):
    s = {}
    if single:
        arms = sorted({r["arm"] for r in single})
        s["single"] = {"arms": {a: arm_stats([r for r in single if r["arm"] == a]) for a in arms},
                       "vs_baseline": {k: paired(single, k, "llano", "baseline", low) for k, _, low in METRICS},
                       "pref_baseline": preference([p for p in pw if p["kind"] == "single"], "baseline")}
        structured = {r["prompt_id"] for r in single if r["arm"] == "llano_nodiag"}
        if structured:
            sub = [r for r in single if r["prompt_id"] in structured]
            s["diagrams"] = {"arms": {a: arm_stats([r for r in sub if r["arm"] == a]) for a in ("llano", "llano_nodiag")},
                             "vs_nodiag": {k: paired(sub, k, "llano", "llano_nodiag", low) for k, _, low in METRICS},
                             "pref_nodiag": preference([p for p in pw if p["kind"] == "single"], "llano_nodiag")}
    if turns:
        s["conversation"] = {
            "by_turn": {t: {a: arm_stats([r for r in turns if r["arm"] == a and r["turn"] == t]) for a in ("baseline", "llano")}
                        for t in sorted({r["turn"] for r in turns})},
            "self_sufficiency": {a: mean([r["conv_self_sufficiency"] for r in turns if r["arm"] == a and r["turn"] == 1])
                                 for a in ("baseline", "llano")},
            "wrong_per_conv": {a: mean([r["conv_wrong"] for r in turns if r["arm"] == a and r["turn"] == 1])
                               for a in ("baseline", "llano")},
            "pref_baseline": preference([p for p in pw if p["kind"] == "conversation"], "baseline"),
        }
    return s


# ---------- output ----------

def fmt(k, v):
    if v is None or v != v:
        return "--"
    if k in {"answer_first", "self_sufficiency", "self_sufficiency_valid", "fidelity", "diagram_rate", "thinking_share",
             "diagram_token_share", "unverified_quotes"}:
        return f"{100 * v:.0f}%"
    if k in {"per100", "filler", "wrong"}:
        return f"{v:.2f}"
    if k == "inflesz":
        return f"{v:.1f}"
    return f"{v:.0f}"


def table(arms: dict, names: list[str]) -> list[str]:
    names = [n for n in names if arms.get(n)]
    out = ["| | " + " | ".join(names) + " |", "|---|" + "---:|" * len(names)]
    for k, label, _ in METRICS:
        out.append(f"| {label} | " + " | ".join(fmt(k, arms[n][k]) for n in names) + " |")
    for k, label in (("thinking_share", "Thinking share of output"), ("input_tokens", "Input tokens (median)"),
                     ("diagram_rate", "Answers with a diagram"), ("diagram_token_share", "Diagram share of the answer"),
                     ("unverified_quotes", "Judge quotes not found in text")):
        out.append(f"| {label} | " + " | ".join(fmt(k, arms[n][k]) for n in names) + " |")
    out.append("| Diagram verdicts (ok/wrong/redundant) | " + " | ".join(
        "{correct}/{incorrect}/{redundant}".format(**arms[n]["diagram_verdicts"]) for n in names) + " |")
    return out


def pref_line(label, p):
    if not p:
        return []
    return [f"- **{label}:** llano {p['llano']}, tie {p['tie']}, other {p['other']}. Score {100 * p['score']:.0f}% "
            f"(ties count half; CI {100 * p['score_ci95'][0]:.0f}–{100 * p['score_ci95'][1]:.0f}%). "
            f"By prompt: {p['prompts_llano']} llano, {p['prompts_other']} other, {p['prompts_even']} even, p = {p['p_sign']:.4f}."]


def deltas(d: dict) -> list[str]:
    out = []
    for k, label, _ in METRICS:
        x = d.get(k)
        if x:
            out.append(f"- {label}: better in {x['better']}, worse in {x['worse']}, equal in {x['equal']} of {x['prompts']} prompts "
                       f"(p = {x['p_sign']:.4f}).")
    return out


def markdown(summary) -> str:
    meta = summary["meta"]
    out = [f"# Results: {meta['run_id']}", "",
           f"Claude Code {meta['claude_cli']}. Models: {', '.join(meta['models'])}. Runs: {meta['runs']}. "
           f"Judge: {summary['judge']}. Reader: {summary['reader']}.", ""]
    if summary["floor"]:
        out += [f"Knowledge floor: the reader answers {summary['floor']['known']} of {summary['floor']['total']} questions "
                f"correctly with no text. 'Self-sufficiency, questions not known without text' excludes them.", ""]
    for scope, s in summary["scopes"].items():
        out.append(f"## {scope}")
        if "single" in s:
            out += ["", "### Single turn: baseline vs llano", ""] + table(s["single"]["arms"], ["baseline", "llano"]) + [""]
            out += pref_line("Blind preference vs baseline (both orders)", s["single"]["pref_baseline"])
            out += ["", "Paired by prompt, llano vs baseline:"] + deltas(s["single"]["vs_baseline"])
        if "diagrams" in s:
            out += ["", "### Diagrams: llano vs llano without diagrams (structured prompts)", ""]
            out += table(s["diagrams"]["arms"], ["llano", "llano_nodiag"]) + [""]
            out += pref_line("Blind preference vs no diagrams (both orders)", s["diagrams"]["pref_nodiag"])
            out += ["", "Paired by prompt, llano vs llano_nodiag:"] + deltas(s["diagrams"]["vs_nodiag"])
        if "conversation" in s:
            c = s["conversation"]
            out += ["", "### Conversations", "",
                    "| Turn | Viol./100 baseline | Viol./100 llano | Facts baseline | Facts llano | Words baseline | Words llano |",
                    "|---:|---:|---:|---:|---:|---:|---:|"]
            for t, d in c["by_turn"].items():
                b, l = d["baseline"], d["llano"]
                out.append(f"| {t} | {fmt('per100', b['per100'])} | {fmt('per100', l['per100'])} | {fmt('fidelity', b['fidelity'])} | "
                           f"{fmt('fidelity', l['fidelity'])} | {fmt('words', b['words'])} | {fmt('words', l['words'])} |")
            ss, w = c["self_sufficiency"], c["wrong_per_conv"]
            out += ["", f"- Self-sufficiency: baseline {fmt('self_sufficiency', ss['baseline'])}, llano {fmt('self_sufficiency', ss['llano'])}.",
                    f"- Wrong claims per conversation: baseline {fmt('wrong', w['baseline'])}, llano {fmt('wrong', w['llano'])}."]
            out += pref_line("Blind preference, whole conversation (both orders)", c["pref_baseline"])
        out.append("")
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args()
    snaps, analysis, reader, floor, pw, meta = load(args.run_id)
    single, turns = build_rows(snaps, analysis, reader, floor)
    models = sorted({r["model"] for r in single + turns})
    scopes = {"All models": summarize(single, turns, pw)}
    for m in models:
        scopes[m] = summarize([r for r in single if r["model"] == m], [r for r in turns if r["model"] == m],
                              [p for p in pw if p["model_alias"] == m])
    known = sum(sum(f["correct"]) for f in floor.values())
    summary = {
        "meta": meta, "scopes": scopes,
        "judge": ", ".join(sorted({d.get("judge_model") for d in analysis.values()} - {None})) or "--",
        "reader": ", ".join(sorted({d.get("reader_model") for d in reader.values()} - {None})) or "--",
        "floor": {"known": known, "total": sum(len(f["correct"]) for f in floor.values()),
                  "by_prompt": {k: f["correct"] for k, f in floor.items()}} if floor else None,
    }
    out = ROOT / "results" / args.run_id
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    md = markdown(summary)
    (out / "summary.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
