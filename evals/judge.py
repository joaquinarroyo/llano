"""LLM judge, run through the same isolated Claude Code sessions as run.py.

Two judgments:
  fidelity  - which key facts each response keeps, and how many wrong claims it adds.
              For a conversation, one call covers all turns.
  pairwise  - blind A/B between llano and baseline for the same prompt and run.
              The order is randomized with a fixed seed.

Usage:
  uv run judge.py --run-id full --judge-model sonnet
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

from run import ROOT, SNAPSHOTS, anonymize_session, claude, load_prompts, session_env

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

FIDELITY_CONV = """Eres un evaluador técnico. Recibes una conversación entre un desarrollador y un asistente. Cada turno del asistente tiene su propia lista numerada de hechos clave.

Para cada turno, decide qué hechos clave expresa la respuesta del asistente en ese turno (aunque use otras palabras). Un hecho cuenta solo si la respuesta lo dice o lo implica sin ambigüedad.
Además, cuenta cuántas afirmaciones técnicamente incorrectas hay en todas las respuestas del asistente.

Devuelve SOLO un objeto JSON, sin texto adicional:
{{"turns": [[true/false por cada hecho del turno 1], [... turno 2], ...], "incorrect_claims": <entero>, "notes": "<una frase>"}}

{transcript}
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

PAIRWISE_CONV = """Eres un evaluador. Un desarrollador hispanohablante tuvo la misma conversación con dos asistentes, A y B. Los mensajes del desarrollador son idénticos. Solo cambian las respuestas.

Elige el asistente cuyas respuestas el desarrollador entiende mejor en una sola lectura, a lo largo de toda la conversación: claras, directas y fáciles de leer, SIN perder información técnica relevante. Si un asistente es más breve pero omite algo importante, eso cuenta en contra. Ignora el largo por sí mismo.

Devuelve SOLO un objeto JSON, sin texto adicional:
{{"winner": "A" | "B" | "empate", "reason": "<una frase>"}}

# Conversación con el asistente A
{a}

# Conversación con el asistente B
{b}
"""


def transcript(prompt: dict, rec: dict, facts: bool = False) -> str:
    parts = []
    for i, (turn, out) in enumerate(zip(prompt["turns"], rec["turns"]), 1):
        parts.append(f"## Turno {i}\n### Desarrollador\n{turn['prompt']}")
        if facts:
            parts.append("### Hechos clave del turno\n" + "\n".join(f"{j + 1}. {f}" for j, f in enumerate(turn["key_facts"])))
        parts.append(f"### Asistente\n{out['text']}")
    return "\n\n".join(parts)


def parse_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError(f"no JSON in judge output: {text[:200]}")
    return json.loads(m.group(0))


def ask(prompt: str, model: str, cwd: str, env: dict) -> dict:
    last = None
    for attempt in range(3):
        try:
            return parse_json(claude(prompt, model, None, cwd, env)["result"])
        except Exception as e:  # noqa: BLE001 - retry CLI and parse failures
            last = e
            time.sleep(15 * (attempt + 1))
    raise RuntimeError(last)


def fidelity_task(snap: Path, prompts: dict, model: str, cwd: str, env: dict, out: Path) -> str:
    if out.exists():
        return "skip"
    rec = json.loads(snap.read_text())
    p = prompts[rec["prompt_id"]]
    base = {k: rec[k] for k in ("prompt_id", "category", "arm", "model_alias", "run", "kind")}
    if rec["kind"] == "conversation":
        res = ask(FIDELITY_CONV.format(transcript=transcript(p, rec, facts=True)), model, cwd, env)
        turns = res.get("turns", [])
        kept = [[bool(x) for x in (turns[i] if i < len(turns) else [])][: len(t["key_facts"])] for i, t in enumerate(p["turns"])]
        result = base | {"facts_by_turn": kept, "n_facts_by_turn": [len(t["key_facts"]) for t in p["turns"]]}
    else:
        facts = "\n".join(f"{i + 1}. {f}" for i, f in enumerate(p["key_facts"]))
        res = ask(FIDELITY.format(prompt=p["prompt"], facts=facts, response=rec["text"]), model, cwd, env)
        result = base | {"facts": [bool(x) for x in res.get("facts", [])][: len(p["key_facts"])], "n_facts": len(p["key_facts"])}
    result |= {"incorrect_claims": int(res.get("incorrect_claims", 0)), "notes": res.get("notes", ""), "judge_model": model}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    return "ok"


def pairwise_task(llano: Path, baseline: Path, prompts: dict, model: str, cwd: str, env: dict, out: Path) -> str:
    if out.exists():
        return "skip"
    l_rec, b_rec = json.loads(llano.read_text()), json.loads(baseline.read_text())
    p = prompts[l_rec["prompt_id"]]
    swap = int(hashlib.sha1(str(out.relative_to(JUDGE)).encode()).hexdigest(), 16) % 2 == 1  # llano is B when swapped
    a, b = (b_rec, l_rec) if swap else (l_rec, b_rec)
    if l_rec["kind"] == "conversation":
        res = ask(PAIRWISE_CONV.format(a=transcript(p, a), b=transcript(p, b)), model, cwd, env)
    else:
        res = ask(PAIRWISE.format(prompt=p["prompt"], a=a["text"], b=b["text"]), model, cwd, env)
    w = str(res.get("winner", "")).strip().lower()
    if w not in {"a", "b"} and not w.startswith("emp"):
        raise ValueError(f"unexpected winner: {w!r}")
    winner = "tie" if w.startswith("emp") else ("llano" if (w == "a") != swap else "baseline")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        **{k: l_rec[k] for k in ("prompt_id", "category", "model_alias", "run", "kind")},
        "llano_position": "B" if swap else "A", "winner": winner, "reason": res.get("reason", ""), "judge_model": model,
    }, ensure_ascii=False, indent=2))
    return "ok"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--judge-model", default="sonnet")
    ap.add_argument("--prompts", nargs="+", default=[str(ROOT / "prompts" / "es.jsonl"), str(ROOT / "prompts" / "es_conversations.jsonl")])
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    prompts = {p["id"]: p for p in load_prompts(args.prompts)}
    src, dst = SNAPSHOTS / args.run_id, JUDGE / args.run_id
    jobs = []
    for s in sorted(src.glob("*/*/*.json")):
        model, arm = s.parts[-3], s.parts[-2]
        jobs.append(("fidelity", s, dst / "fidelity" / model / arm / s.name))
        b = src / model / "baseline" / s.name
        if arm == "llano" and b.exists():
            jobs.append(("pairwise", (s, b), dst / "pairwise" / model / s.name))

    with tempfile.TemporaryDirectory(prefix="cfg-") as config_dir, tempfile.TemporaryDirectory(prefix="judge-") as cwd:
        env = session_env(config_dir)
        anonymize_session(env, cwd)

        def run(job):
            kind, src_, out = job
            try:
                if kind == "fidelity":
                    return fidelity_task(src_, prompts, args.judge_model, cwd, env, out)
                return pairwise_task(*src_, prompts, args.judge_model, cwd, env, out)
            except Exception as e:  # noqa: BLE001 - report and continue
                return f"fail: {e}"

        with cf.ThreadPoolExecutor(args.workers) as pool:
            for i, (job, status) in enumerate(zip(jobs, pool.map(run, jobs)), 1):
                if status != "skip":
                    print(f"[{i}/{len(jobs)}] {job[0]} {job[2].relative_to(dst)}: {status}", flush=True)
    print(f"done: {dst}")


if __name__ == "__main__":
    main()
