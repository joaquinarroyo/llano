"""Aggregate a run into summary.json, LaTeX tables/macros and PDF figures.

Usage:
  uv run measure.py --run-id pilot
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics as st
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from lint import lint  # noqa: E402

ROOT = Path(__file__).resolve().parent
ARMS = ["baseline", "terse", "llano", "caveman"]
ARM_LABEL = {"baseline": "Sin instrucción", "terse": "Concisa", "llano": "Llano", "caveman": "Caveman"}
# Validated categorical slots 1-4 (dataviz reference palette, light mode), fixed per arm.
COLOR = {"baseline": "#2a78d6", "terse": "#eb6834", "llano": "#1baf7a", "caveman": "#eda100"}
WIN, TIE, LOSS = "#2a78d6", "#c9c8c2", "#e34948"
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
CATEGORY_LABEL = {"explicacion": "Explicación", "error": "Error", "resumen": "Resumen",
                  "procedimiento": "Procedimiento", "comparacion": "Comparación", "conceptual": "Conceptual"}
VIOLATIONS = ["long_sentence", "semicolon", "long_paragraph", "banned_filler", "avoid_word", "stacked_hedges", "gerund_chain"]
VIOLATION_LABEL = {
    "long_sentence": "Frases largas", "semicolon": "Punto y coma", "long_paragraph": "Párrafos largos",
    "banned_filler": "Muletillas", "avoid_word": "Palabras a evitar", "stacked_hedges": "Dudas apiladas",
    "gerund_chain": "Gerundios en cadena",
}


def load(run_id: str):
    snaps = [json.loads(p.read_text()) for p in sorted((ROOT / "snapshots" / run_id).glob("*/*/*.json"))]
    fid = {(d["model_alias"], d["arm"], d["prompt_id"], d["run"]): d
           for d in (json.loads(p.read_text()) for p in (ROOT / "judge" / run_id / "fidelity").glob("*/*/*.json"))}
    pw = [json.loads(p.read_text()) for p in (ROOT / "judge" / run_id / "pairwise").glob("*/*/*.json")]
    meta = json.loads((ROOT / "snapshots" / run_id / "meta.json").read_text())
    return snaps, fid, pw, meta


def bootstrap_ci(values: list[float], n: int = 5000, seed: int = 7) -> tuple[float, float]:
    """95% percentile CI of the median."""
    if len(values) < 2:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    meds = sorted(st.median(rng.choices(values, k=len(values))) for _ in range(n))
    return meds[int(0.025 * n)], meds[int(0.975 * n)]


def sign_test(wins: int, losses: int) -> float:
    """Two-sided exact sign test, ties excluded."""
    n = wins + losses
    if n == 0:
        return 1.0
    k = max(wins, losses)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n)


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def enrich(snaps, fid):
    rows = []
    for s in snaps:
        rep = lint(s["text"])
        f = fid.get((s["model_alias"], s["arm"], s["prompt_id"], s["run"]))
        rows.append({
            **s,
            "visible_tokens": (s["output_tokens"] or 0) - (s["thinking_tokens"] or 0),
            "words": rep.words, "per100": rep.per_100, "inflesz": rep.inflesz,
            "violations": rep.violations,
            "fidelity": (sum(f["facts"]) / f["n_facts"]) if f else None,
            "incorrect": f["incorrect_claims"] if f else None,
        })
    return rows


def paired_delta(rows, model, arm, ref, key):
    """Per prompt: arm/ref - 1, averaged over runs. Returns the list over prompts."""
    by = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r["model_alias"] == model and r["arm"] in (arm, ref):
            by[r["prompt_id"]][r["arm"]].append(r[key])
    out = []
    for d in by.values():
        if d.get(arm) and d.get(ref) and st.mean(d[ref]) > 0:
            out.append(st.mean(d[arm]) / st.mean(d[ref]) - 1)
    return out


def summarize(rows, pw, meta):
    models = sorted({r["model_alias"] for r in rows})
    summary = {"meta": meta, "models": {},
               "model_ids": {r["model_alias"]: r["model"] for r in rows if r.get("model")}}
    for m in models:
        ms = {"arms": {}, "deltas": {}, "pairwise": {}, "categories": {}}
        for a in ARMS:
            rs = [r for r in rows if r["model_alias"] == m and r["arm"] == a]
            if not rs:
                continue
            fids = [r["fidelity"] for r in rs if r["fidelity"] is not None]
            ms["arms"][a] = {
                "n": len(rs),
                "visible_tokens_median": st.median(r["visible_tokens"] for r in rs),
                "output_tokens_median": st.median(r["output_tokens"] for r in rs),
                "words_median": st.median(r["words"] for r in rs),
                "input_tokens_median": st.median(r["input_tokens"] for r in rs),
                "per100_mean": st.mean(r["per100"] for r in rs),
                "inflesz_mean": st.mean(r["inflesz"] for r in rs if r["inflesz"] is not None),
                "fidelity_mean": st.mean(fids) if fids else None,
                "incorrect_total": sum(r["incorrect"] or 0 for r in rs),
                "violations": {v: sum(r["violations"][v] for r in rs) for v in VIOLATIONS},
                "words_total": sum(r["words"] for r in rs),
            }
        for ref in ("baseline", "terse", "caveman"):
            for key in ("visible_tokens", "words"):
                d = paired_delta(rows, m, "llano", ref, key)
                if d:
                    lo, hi = bootstrap_ci(d)
                    ms["deltas"][f"{key}_vs_{ref}"] = {"median": st.median(d), "ci95": [lo, hi], "n": len(d)}
        for ref in ("baseline", "terse", "caveman"):
            by = defaultdict(dict)
            for r in rows:
                if r["model_alias"] == m and r["arm"] in ("llano", ref):
                    by[(r["prompt_id"], r["run"])][r["arm"]] = r["per100"]
            pairs = [d for d in by.values() if len(d) == 2]
            better = sum(d["llano"] < d[ref] for d in pairs)
            worse = sum(d["llano"] > d[ref] for d in pairs)
            ms["deltas"][f"violations_vs_{ref}"] = {"better": better, "equal": len(pairs) - better - worse,
                                                    "worse": worse, "p_sign": sign_test(better, worse)}
        for other in ("baseline", "terse", "caveman"):
            ps = [p for p in pw if p["model_alias"] == m and p["other"] == other]
            if ps:
                w, l = sum(p["winner"] == "llano" for p in ps), sum(p["winner"] == other for p in ps)
                ms["pairwise"][other] = {
                    "llano": w, "tie": sum(p["winner"] == "tie" for p in ps), "other": l, "n": len(ps),
                    "p_sign": sign_test(w, l), "win_rate_ci95": list(wilson(w, w + l)),
                }
        for c in sorted({r["category"] for r in rows}):
            ms["categories"][c] = {
                a: {
                    "words_median": st.median([r["words"] for r in rows if r["model_alias"] == m and r["arm"] == a and r["category"] == c] or [0]),
                    "per100_mean": st.mean([r["per100"] for r in rows if r["model_alias"] == m and r["arm"] == a and r["category"] == c] or [0]),
                } for a in ARMS
            }
        summary["models"][m] = ms
    return summary


# ---------- LaTeX ----------

def pct(x: float | None, signed: bool = True) -> str:
    if x is None or x != x:
        return "--"
    s = f"{x * 100:+.0f}" if signed else f"{x * 100:.0f}"
    return s.replace("-", "$-$") + r"\%"


def write_latex(summary, out: Path, model: str):
    ms = summary["models"][model]
    A = ms["arms"]
    lines = [r"\begin{tabular}{lrrrrrr}", r"\toprule",
             r"Grupo & Tokens visibles & Palabras & Viol./100 pal. & INFLESZ & Fidelidad & Errores \\", r"\midrule"]
    for a in ARMS:
        if a in A:
            x = A[a]
            lines.append(f"{ARM_LABEL[a]} & {x['visible_tokens_median']:.0f} & {x['words_median']:.0f} & "
                         f"{x['per100_mean']:.2f} & {x['inflesz_mean']:.1f} & {pct(x['fidelity_mean'], False)} & {x['incorrect_total']} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (out / "table_main.tex").write_text("\n".join(lines) + "\n")

    lines = [r"\begin{tabular}{l" + "r" * len(A) + "}", r"\toprule",
             "Tipo & " + " & ".join(ARM_LABEL[a] for a in ARMS if a in A) + r" \\", r"\midrule"]
    for v in VIOLATIONS:
        cells = [f"{100 * A[a]['violations'][v] / max(A[a]['words_total'], 1):.2f}" for a in ARMS if a in A]
        lines.append(f"{VIOLATION_LABEL[v]} & " + " & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (out / "table_violations.tex").write_text("\n".join(lines) + "\n")

    lines = [r"\begin{tabular}{lrrrrrr}", r"\toprule",
             r"Llano contra & Gana llano & Empate & Gana el otro & $n$ & IC 95\% victorias & $p$ \\", r"\midrule"]
    for other, p in ms["pairwise"].items():
        lo, hi = p["win_rate_ci95"]
        lines.append(f"{ARM_LABEL[other]} & {p['llano']} & {p['tie']} & {p['other']} & {p['n']} & "
                     f"{100 * lo:.0f}--{100 * hi:.0f}\\% & {p['p_sign']:.3f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (out / "table_pairwise.tex").write_text("\n".join(lines) + "\n")

    cats = ms["categories"]
    lines = [r"\begin{tabular}{l" + "rr" * 2 + "}", r"\toprule",
             r" & \multicolumn{2}{c}{Palabras (mediana)} & \multicolumn{2}{c}{Viol./100 pal.} \\",
             r"Categoría & Concisa & Llano & Concisa & Llano \\", r"\midrule"]
    for c, d in cats.items():
        lines.append(f"{CATEGORY_LABEL.get(c, c)} & {d['terse']['words_median']:.0f} & {d['llano']['words_median']:.0f} & "
                     f"{d['terse']['per100_mean']:.2f} & {d['llano']['per100_mean']:.2f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (out / "table_category.tex").write_text("\n".join(lines) + "\n")

    def delta(k):
        d = ms["deltas"].get(k)
        if d and "median" not in d:
            return ("--", "--", "--")
        return (pct(d["median"]), pct(d["ci95"][0]), pct(d["ci95"][1])) if d else ("--", "--", "--")

    meta = summary["meta"]
    macros = {
        "evalModel": model.capitalize(), "evalModelId": summary.get("model_ids", {}).get(model, model), "evalPrompts": str(meta["prompts"]), "evalRuns": str(meta["runs"]),
        "evalCli": meta["claude_cli"].split(" (")[0],
        "evalDate": meta["started_at"][:10],
        "llanoInputTokens": f"{A['llano']['input_tokens_median']:.0f}",
        "terseInputTokens": f"{A['terse']['input_tokens_median']:.0f}",
        "llanoPerHundred": f"{A['llano']['per100_mean']:.2f}", "tersePerHundred": f"{A['terse']['per100_mean']:.2f}",
        "baselinePerHundred": f"{A['baseline']['per100_mean']:.2f}",
        "llanoFidelity": pct(A["llano"]["fidelity_mean"], False), "terseFidelity": pct(A["terse"]["fidelity_mean"], False),
        "baselineFidelity": pct(A["baseline"]["fidelity_mean"], False),
        "llanoInflesz": f"{A['llano']['inflesz_mean']:.1f}", "terseInflesz": f"{A['terse']['inflesz_mean']:.1f}",
        "baselineInflesz": f"{A['baseline']['inflesz_mean']:.1f}",
    }
    if "caveman" in A:
        macros.update({"cavemanPerHundred": f"{A['caveman']['per100_mean']:.2f}",
                       "cavemanFidelity": pct(A["caveman"]["fidelity_mean"], False),
                       "cavemanInflesz": f"{A['caveman']['inflesz_mean']:.1f}"})
    for ref, name in (("terse", "Terse"), ("baseline", "Baseline"), ("caveman", "Caveman")):
        for key, kn in (("words", "Words"), ("visible_tokens", "Tokens")):
            m_, lo, hi = delta(f"{key}_vs_{ref}")
            macros[f"delta{kn}{name}"], macros[f"delta{kn}{name}Lo"], macros[f"delta{kn}{name}Hi"] = m_, lo, hi
        v = ms["deltas"].get(f"violations_vs_{ref}")
        if v:
            macros[f"violBetter{name}"], macros[f"violEqual{name}"], macros[f"violWorse{name}"] = str(v["better"]), str(v["equal"]), str(v["worse"])
            macros[f"violP{name}"] = f"{v['p_sign']:.4f}" if v["p_sign"] >= 0.0001 else "$<$0.0001"
        p = ms["pairwise"].get(ref)
        if p:
            macros[f"wins{name}"], macros[f"ties{name}"], macros[f"losses{name}"] = str(p["llano"]), str(p["tie"]), str(p["other"])
            macros[f"pSign{name}"] = f"{p['p_sign']:.3f}"
    (out / "macros.tex").write_text("".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in macros.items()))


# ---------- figures ----------

def style(ax, title):
    ax.set_facecolor(SURFACE)
    ax.set_title(title, loc="left", fontsize=10, color=INK, pad=10)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=8, length=0)
    ax.yaxis.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def bar(ax, arms, values, fmt):
    xs = range(len(arms))
    bars = ax.bar(xs, values, width=0.6, color=[COLOR[a] for a in arms], edgecolor=SURFACE, linewidth=2)
    ax.set_xticks(list(xs), [ARM_LABEL[a] for a in arms])
    for b, v in zip(bars, values):  # direct labels: the contrast relief for aqua/yellow
        ax.annotate(fmt(v), (b.get_x() + b.get_width() / 2, b.get_height()), xytext=(0, 3),
                    textcoords="offset points", ha="center", fontsize=8, color=INK)


def figures(summary, out: Path, model: str):
    plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": SURFACE})
    A = summary["models"][model]["arms"]
    arms = [a for a in ARMS if a in A]

    fig, axes = plt.subplots(1, 3, figsize=(10, 3.2))
    style(axes[0], "Palabras por respuesta (mediana)")
    bar(axes[0], arms, [A[a]["words_median"] for a in arms], lambda v: f"{v:.0f}")
    style(axes[1], "Violaciones cada 100 palabras")
    bar(axes[1], arms, [A[a]["per100_mean"] for a in arms], lambda v: f"{v:.1f}")
    style(axes[2], "Hechos clave conservados")
    bar(axes[2], arms, [100 * (A[a]["fidelity_mean"] or 0) for a in arms], lambda v: f"{v:.0f}%")
    axes[2].set_ylim(0, 105)
    for ax in axes:
        ax.tick_params(axis="x", labelrotation=0)
    fig.tight_layout()
    fig.savefig(out / "fig_overview.pdf")
    plt.close(fig)

    P = summary["models"][model]["pairwise"]
    if P:
        others = list(P)
        fig, ax = plt.subplots(figsize=(7, 0.6 + 0.55 * len(others)))
        style(ax, "Comparación a ciegas: llano contra cada grupo")
        ax.yaxis.grid(False)
        ax.xaxis.grid(True, color=GRID, linewidth=0.6)
        for i, o in enumerate(others):
            p, left = P[o], 0
            for key, color, label in (("llano", WIN, "Gana llano"), ("tie", TIE, "Empate"), ("other", LOSS, "Gana el otro")):
                w = 100 * p[key] / p["n"]
                ax.barh(i, w, left=left, color=color, edgecolor=SURFACE, linewidth=2, label=label if i == 0 else None)
                if w >= 8:
                    ax.text(left + w / 2, i, f"{p[key]}", ha="center", va="center", fontsize=8,
                            color="#ffffff" if key != "tie" else INK)
                left += w
        ax.set_yticks(range(len(others)), [ARM_LABEL[o] for o in others])
        ax.set_xlim(0, 100)
        ax.set_xlabel("% de comparaciones", fontsize=8, color=INK2)
        ax.invert_yaxis()
        ax.legend(ncol=3, fontsize=8, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.35))
        fig.tight_layout()
        fig.savefig(out / "fig_pairwise.pdf")
        plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--model", help="model alias for tables and figures (default: first)")
    args = ap.parse_args()
    snaps, fid, pw, meta = load(args.run_id)
    rows = enrich(snaps, fid)
    summary = summarize(rows, pw, meta)
    out = ROOT / "results" / args.run_id
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    model = args.model or sorted(summary["models"])[0]
    write_latex(summary, out, model)
    figures(summary, out, model)
    (ROOT / "report" / "run.tex").write_text(f"\\newcommand{{\\resdir}}{{../results/{args.run_id}}}\n")

    ms = summary["models"][model]
    print(f"model={model}")
    for a, x in ms["arms"].items():
        fid_ = f"{100 * x['fidelity_mean']:.0f}%" if x["fidelity_mean"] is not None else "--"
        print(f"  {a:9s} tokens={x['visible_tokens_median']:.0f} words={x['words_median']:.0f} "
              f"viol/100={x['per100_mean']:.2f} inflesz={x['inflesz_mean']:.1f} fidelity={fid_} wrong={x['incorrect_total']} in={x['input_tokens_median']:.0f}")
    for k, d in ms["deltas"].items():
        if "median" not in d:
            print(f"  {k}: better {d['better']} equal {d['equal']} worse {d['worse']} p={d['p_sign']:.4f}")
            continue
        print(f"  {k}: {100 * d['median']:+.0f}% [{100 * d['ci95'][0]:+.0f}, {100 * d['ci95'][1]:+.0f}] n={d['n']}")
    for o, p in ms["pairwise"].items():
        print(f"  llano vs {o}: win {p['llano']} tie {p['tie']} loss {p['other']} p={p['p_sign']:.3f} "
              f"win-rate CI [{100 * p['win_rate_ci95'][0]:.0f}, {100 * p['win_rate_ci95'][1]:.0f}]")


if __name__ == "__main__":
    main()
