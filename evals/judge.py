"""LLM judge, also run through isolated Claude Code sessions.

Two judgments per response:
  fidelity  - which key facts of the prompt the response keeps, and how many wrong claims it adds
  pairwise  - blind A/B: llano vs each other arm, order randomized with a fixed seed

Usage:
  uv run judge.py --run-id pilot --judge-model sonnet
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import re
import tempfile
import time
from pathlib import Path

from run import ISOLATION, ROOT, SNAPSHOTS, claude  # noqa: F401 - shared isolation

JUDGE = ROOT / "judge"

FIDELITY = """Eres un evaluador técnico. Recibes una pregunta, una lista numerada de hechos clave y una respuesta.

Para cada hecho clave, decide si la respuesta lo expresa (aunque use otras palabras). Un hecho cuenta solo si la respuesta lo dice o lo implica sin ambigüedad.
Además, cuenta cuántas afirmaciones técnicamente incorrectas contiene la respuesta.

Devuelve SOLO un objeto JSON, sin texto adicional:
{{"facts": [true/false por cada hecho, en orden], "incorrect_claims": <entero>, "notes": "<una frase>"}}

## Pregunta
{prompt}

## Hechos clave
{facts}

## Respuesta
{response}
"""

PAIRWISE = """Eres un evaluador. Un desarrollador hispanohablante hizo una pregunta y recibió dos respuestas, A y B.

Elige la respuesta que el desarrollador entiende mejor en una sola lectura: clara, directa y fácil de leer, SIN perder información técnica relevante. Si una es más corta pero omite algo importante, eso cuenta en contra. Ignora el largo por sí mismo.

Devuelve SOLO un objeto JSON, sin texto adicional:
{{"winner": "A" | "B" | "empate", "reason": "<una frase>"}}

## Pregunta
{prompt}

## Respuesta A
{a}

## Respuesta B
{b}
"""


def parse_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError(f"no JSON in judge output: {text[:200]}")
    return json.loads(m.group(0))


def ask(prompt: str, model: str, cwd: str) -> dict:
    last = None
    for attempt in range(3):
        try:
            return parse_json(claude(prompt, model, None, cwd)["result"])
        except Exception as e:  # noqa: BLE001 - retry CLI and parse failures
            last = e
            time.sleep(10 * (attempt + 1))
    raise RuntimeError(last)


def fidelity_task(snap: Path, prompts: dict, model: str, cwd: str, out: Path) -> str:
    if out.exists():
        return "skip"
    rec = json.loads(snap.read_text())
    p = prompts[rec["prompt_id"]]
    facts = "\n".join(f"{i + 1}. {f}" for i, f in enumerate(p["key_facts"]))
    res = ask(FIDELITY.format(prompt=p["prompt"], facts=facts, response=rec["text"]), model, cwd)
    kept = [bool(x) for x in res.get("facts", [])][: len(p["key_facts"])]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        **{k: rec[k] for k in ("prompt_id", "category", "arm", "model_alias", "run")},
        "facts": kept, "n_facts": len(p["key_facts"]),
        "incorrect_claims": int(res.get("incorrect_claims", 0)), "notes": res.get("notes", ""),
        "judge_model": model,
    }, ensure_ascii=False, indent=2))
    return "ok"


def pairwise_task(llano: Path, other: Path, prompts: dict, model: str, cwd: str, out: Path) -> str:
    if out.exists():
        return "skip"
    a_rec, b_rec = json.loads(llano.read_text()), json.loads(other.read_text())
    seed = int(hashlib.sha1(str(out).encode()).hexdigest(), 16)
    swap = seed % 2 == 1  # llano is B when swapped
    a, b = (b_rec, a_rec) if swap else (a_rec, b_rec)
    res = ask(PAIRWISE.format(prompt=prompts[a_rec["prompt_id"]]["prompt"], a=a["text"], b=b["text"]), model, cwd)
    w = str(res.get("winner", "")).strip().lower()
    if w not in {"a", "b"} and not w.startswith("emp"):
        raise ValueError(f"unexpected winner: {w!r}")
    winner = "tie" if w.startswith("emp") else ("llano" if (w == "a") != swap else b_rec["arm"])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "prompt_id": a_rec["prompt_id"], "category": a_rec["category"], "model_alias": a_rec["model_alias"],
        "run": a_rec["run"], "other": b_rec["arm"], "llano_position": "B" if swap else "A",
        "winner": winner, "reason": res.get("reason", ""), "judge_model": model,
    }, ensure_ascii=False, indent=2))
    return "ok"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--judge-model", default="sonnet")
    ap.add_argument("--prompts", default=str(ROOT / "prompts" / "es.jsonl"))
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    prompts = {p["id"]: p for p in map(json.loads, Path(args.prompts).read_text().splitlines()) if p}
    src, dst = SNAPSHOTS / args.run_id, JUDGE / args.run_id
    snaps = sorted(src.glob("*/*/*.json"))
    jobs = []
    for s in snaps:
        model, arm = s.parts[-3], s.parts[-2]
        jobs.append(("fidelity", s, dst / "fidelity" / model / arm / s.name))
        if arm == "llano":
            for other in sorted((src / model).iterdir()):
                o = other / s.name
                if other.name != "llano" and o.exists():
                    jobs.append(("pairwise", (s, o), dst / "pairwise" / model / other.name / s.name))

    with tempfile.TemporaryDirectory(prefix="judge-") as cwd:
        def run(job):
            kind, src_, out = job
            try:
                if kind == "fidelity":
                    return fidelity_task(src_, prompts, args.judge_model, cwd, out)
                return pairwise_task(*src_, prompts, args.judge_model, cwd, out)
            except Exception as e:  # noqa: BLE001 - report and continue
                return f"fail: {e}"

        with cf.ThreadPoolExecutor(args.workers) as pool:
            for i, (job, status) in enumerate(zip(jobs, pool.map(run, jobs)), 1):
                if status != "skip":
                    print(f"[{i}/{len(jobs)}] {job[0]} {job[2].relative_to(dst)}: {status}", flush=True)
    print(f"done: {dst}")


if __name__ == "__main__":
    main()
