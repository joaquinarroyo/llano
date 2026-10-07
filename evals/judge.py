"""Judges for eval v2, run through the same isolated Claude Code sessions as run.py.

Per response:
  analysis  - each key fact as present / partial / absent with a verbatim quote (checked
              in code), wrong claims with quotes, whether the first sentence answers, and
              whether a diagram is correct, incorrect or redundant.
  reader    - a reader model answers multiple-choice questions using only the response
              (self-sufficiency: can the user act without asking again?). Option E is
              "the text does not say". A knowledge floor runs the same questions with no
              text, to spot questions the reader answers from its own knowledge.
Per pair:
  pairwise  - blind comparison in both A/B orders. A split verdict counts as a tie.
              llano vs baseline everywhere; llano vs llano_nodiag on structured prompts.

Usage:
  uv run judge.py --run-id v2 --judge-model sonnet --reader-model haiku
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import random
import re
import tempfile
import time
from pathlib import Path

from run import ROOT, SNAPSHOTS, anonymize_session, claude, load_prompts, session_env

JUDGE = ROOT / "judge"
LETTERS = "ABCD"
NOT_SAID = "El texto no lo dice"

ANALYSIS = """Eres un evaluador técnico. Recibes una pregunta de un desarrollador, una lista numerada de hechos clave y la respuesta de un asistente.

Para cada hecho clave, decide:
- "present": la respuesta lo dice o lo implica sin ambigüedad.
- "partial": lo menciona de forma incompleta o vaga.
- "absent": no lo dice.
Para "present" y "partial", copia en "quote" un fragmento literal y corto de la respuesta que lo respalde (copiado exacto, sin cambiar nada). Para "absent", deja "quote" vacío.

Además:
- "incorrect_claims": lista las afirmaciones técnicamente incorrectas de la respuesta, cada una con su fragmento literal.
- "answer_first": true si la primera frase de la respuesta ya responde la pregunta o da el resultado principal.
- "diagram": si la respuesta tiene un diagrama (ASCII, Mermaid o similar), evalúalo:
  "correct" si todas sus relaciones son correctas y están en el texto, "incorrect" si muestra alguna relación falsa, "redundant" si es correcto pero no agrega nada al texto. Si no hay diagrama, "none".

Devuelve SOLO un objeto JSON, sin texto adicional:
{{"facts": [{{"status": "present|partial|absent", "quote": "..."}}], "incorrect_claims": [{{"claim": "...", "quote": "..."}}], "answer_first": true, "diagram": "none|correct|incorrect|redundant"}}

## Pregunta
{prompt}

## Hechos clave
{facts}

## Respuesta
{response}
"""

ANALYSIS_CONV = """Eres un evaluador técnico. Recibes una conversación entre un desarrollador y un asistente. Cada turno del asistente tiene su propia lista numerada de hechos clave.

Para cada turno y cada hecho clave, decide:
- "present": la respuesta de ese turno lo dice o lo implica sin ambigüedad.
- "partial": lo menciona de forma incompleta o vaga.
- "absent": no lo dice.
Para "present" y "partial", copia en "quote" un fragmento literal y corto de la respuesta de ese turno (copiado exacto). Para "absent", deja "quote" vacío.

Para cada turno, además:
- "answer_first": true si la primera frase de la respuesta ya responde o da el resultado principal.
- "diagram": "none" si no hay diagrama; si hay, "correct", "incorrect" (alguna relación falsa) o "redundant" (correcto pero no agrega nada).
Y para toda la conversación, "incorrect_claims": las afirmaciones técnicamente incorrectas del asistente, cada una con su fragmento literal.

Devuelve SOLO un objeto JSON, sin texto adicional:
{{"turns": [{{"facts": [{{"status": "...", "quote": "..."}}], "answer_first": true, "diagram": "none"}}], "incorrect_claims": [{{"claim": "...", "quote": "..."}}]}}

{transcript}
"""

READER = """Lee el texto y responde las preguntas usando SOLO lo que dice el texto.
Si el texto no responde una pregunta, elige E, aunque sepas la respuesta por tu cuenta.

Devuelve SOLO un objeto JSON, sin texto adicional: {{"answers": ["A", "E", ...]}} con una letra por pregunta, en orden.

## Texto
{text}

## Preguntas
{questions}
"""

PAIRWISE = """Eres un evaluador. Un desarrollador hispanohablante hizo una pregunta y recibió dos respuestas, A y B.

Elige la respuesta que el desarrollador entiende mejor en una sola lectura, sin necesidad de repreguntar: clara, directa y fácil de leer, SIN perder información técnica relevante. Si una es más corta pero omite algo importante, eso cuenta en contra. Ignora el largo por sí mismo. Si son equivalentes, responde "empate".

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

Elige el asistente cuyas respuestas el desarrollador entiende mejor en una sola lectura, sin necesidad de repreguntar, a lo largo de toda la conversación: claras, directas y fáciles de leer, SIN perder información técnica relevante. Ignora el largo por sí mismo. Si son equivalentes, responde "empate".

Devuelve SOLO un objeto JSON, sin texto adicional:
{{"winner": "A" | "B" | "empate", "reason": "<una frase>"}}

# Conversación con el asistente A
{a}

# Conversación con el asistente B
{b}
"""


# ---------- helpers ----------

def transcript(prompt: dict, rec: dict, facts: bool = False, user: bool = True) -> str:
    parts = []
    for i, (turn, out) in enumerate(zip(prompt["turns"], rec["turns"]), 1):
        parts.append(f"## Turno {i}")
        if user:
            parts.append(f"### Desarrollador\n{turn['prompt']}")
        if facts:
            parts.append("### Hechos clave del turno\n" + "\n".join(f"{j + 1}. {f}" for j, f in enumerate(turn["key_facts"])))
        parts.append(f"### Asistente\n{out['text']}")
    return "\n\n".join(parts)


def norm(s: str) -> str:
    s = re.sub(r"[*_`>#|]", "", s.lower())
    return re.sub(r"\s+", " ", s).strip(" .,;:")


def quote_ok(quote: str, text: str) -> bool:
    q = norm(quote)
    return bool(q) and q in norm(text)


def parse_json(text: str) -> dict:
    """First JSON object in the text. Ignores anything the judge writes after it."""
    start = text.find("{")
    if start < 0:
        raise ValueError(f"no JSON in judge output: {text[:200]}")
    obj, _ = json.JSONDecoder().raw_decode(text[start:])
    return obj


def ask(prompt: str, model: str, cwd: str, env: dict) -> dict:
    last = None
    for attempt in range(3):
        try:
            return parse_json(claude(prompt, model, None, cwd, env)["result"])
        except Exception as e:  # noqa: BLE001 - retry CLI and parse failures
            last = e
            time.sleep(15 * (attempt + 1))
    raise RuntimeError(last)


def write(out: Path, data: dict) -> str:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return "ok"


def checked_facts(raw: list, n: int, text: str) -> list[dict]:
    """Keep the judge's status only when its quote is really in the text."""
    facts = []
    for i in range(n):
        f = raw[i] if i < len(raw) and isinstance(raw[i], dict) else {}
        status = f.get("status", "absent")
        verified = status == "absent" or quote_ok(f.get("quote", ""), text)
        facts.append({"status": status, "quote": f.get("quote", ""), "verified": verified,
                      "score": {"present": 1.0, "partial": 0.5}.get(status, 0.0) if verified else 0.0})
    return facts


def checked_claims(raw: list, text: str) -> list[dict]:
    return [{"claim": c.get("claim", ""), "quote": c.get("quote", ""), "verified": quote_ok(c.get("quote", ""), text)}
            for c in raw if isinstance(c, dict)]


def mcq(questions: list[dict], key: str) -> tuple[str, list[str]]:
    """Shuffle options with a fixed seed. Returns the question block and the right letters."""
    blocks, answers = [], []
    for i, q in enumerate(questions):
        opts = [q["correct"], *q["wrong"]]
        random.Random(f"{key}-{i}").shuffle(opts)
        answers.append(LETTERS[opts.index(q["correct"])])
        lines = [f"{i + 1}. {q['q']}"] + [f"   {LETTERS[j]}) {o}" for j, o in enumerate(opts)] + [f"   E) {NOT_SAID}"]
        blocks.append("\n".join(lines))
    return "\n".join(blocks), answers


# ---------- tasks ----------

def analysis_task(snap: Path, prompts: dict, model: str, cwd: str, env: dict, out: Path) -> str:
    if out.exists():
        return "skip"
    rec = json.loads(snap.read_text())
    p = prompts[rec["prompt_id"]]
    base = {k: rec[k] for k in ("prompt_id", "category", "arm", "model_alias", "run", "kind")} | {"judge_model": model}
    if rec["kind"] == "conversation":
        res = ask(ANALYSIS_CONV.format(transcript=transcript(p, rec, facts=True)), model, cwd, env)
        turns_raw = res.get("turns", [])
        turns = []
        for i, (t, o) in enumerate(zip(p["turns"], rec["turns"])):
            tr = turns_raw[i] if i < len(turns_raw) else {}
            turns.append({"facts": checked_facts(tr.get("facts", []), len(t["key_facts"]), o["text"]),
                          "answer_first": bool(tr.get("answer_first")), "diagram": tr.get("diagram", "none")})
        all_text = "\n".join(o["text"] for o in rec["turns"])
        return write(out, base | {"turns": turns, "incorrect_claims": checked_claims(res.get("incorrect_claims", []), all_text)})
    facts = "\n".join(f"{i + 1}. {f}" for i, f in enumerate(p["key_facts"]))
    res = ask(ANALYSIS.format(prompt=p["prompt"], facts=facts, response=rec["text"]), model, cwd, env)
    return write(out, base | {
        "facts": checked_facts(res.get("facts", []), len(p["key_facts"]), rec["text"]),
        "incorrect_claims": checked_claims(res.get("incorrect_claims", []), rec["text"]),
        "answer_first": bool(res.get("answer_first")), "diagram": res.get("diagram", "none"),
    })


def reader_task(snap: Path | None, prompt_id: str, questions: list, prompts: dict, model: str, cwd: str, env: dict, out: Path) -> str:
    if out.exists():
        return "skip"
    if snap is None:  # knowledge floor: no text at all
        text, base = "(no hay texto)", {"prompt_id": prompt_id, "kind": "floor"}
    else:
        rec = json.loads(snap.read_text())
        text = transcript(prompts[prompt_id], rec, user=False) if rec["kind"] == "conversation" else rec["text"]
        base = {k: rec[k] for k in ("prompt_id", "category", "arm", "model_alias", "run", "kind")}
    block, key = mcq(questions, prompt_id)
    res = ask(READER.format(text=text, questions=block), model, cwd, env)
    got = [str(a).strip().upper()[:1] for a in res.get("answers", [])][: len(key)]
    got += ["?"] * (len(key) - len(got))
    return write(out, base | {"key": key, "answers": got, "correct": [g == k for g, k in zip(got, key)],
                              "not_said": [g == "E" for g in got], "reader_model": model})


def pairwise_task(llano: Path, other: Path, prompts: dict, model: str, cwd: str, env: dict, out: Path) -> str:
    if out.exists():
        return "skip"
    l_rec, o_rec = json.loads(llano.read_text()), json.loads(other.read_text())
    p = prompts[l_rec["prompt_id"]]
    verdicts = []
    for llano_first in (True, False):  # both orders; a split verdict is a tie
        a, b = (l_rec, o_rec) if llano_first else (o_rec, l_rec)
        if l_rec["kind"] == "conversation":
            res = ask(PAIRWISE_CONV.format(a=transcript(p, a), b=transcript(p, b)), model, cwd, env)
        else:
            res = ask(PAIRWISE.format(prompt=p["prompt"], a=a["text"], b=b["text"]), model, cwd, env)
        w = str(res.get("winner", "")).strip().lower()
        if w not in {"a", "b"} and not w.startswith("emp"):
            raise ValueError(f"unexpected winner: {w!r}")
        verdicts.append({"winner": "tie" if w.startswith("emp") else ("llano" if (w == "a") == llano_first else o_rec["arm"]),
                         "reason": res.get("reason", "")})
    final = verdicts[0]["winner"] if verdicts[0]["winner"] == verdicts[1]["winner"] else "tie"
    return write(out, {**{k: l_rec[k] for k in ("prompt_id", "category", "model_alias", "run", "kind")},
                       "other": o_rec["arm"], "orders": verdicts, "winner": final, "judge_model": model})


# ---------- main ----------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--judge-model", default="sonnet")
    ap.add_argument("--reader-model", default="haiku")
    ap.add_argument("--prompts", nargs="+", default=[str(ROOT / "prompts" / "es.jsonl"), str(ROOT / "prompts" / "es_conversations.jsonl")])
    ap.add_argument("--reader-questions", default=str(ROOT / "prompts" / "reader_es.jsonl"))
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    prompts = {p["id"]: p for p in load_prompts(args.prompts)}
    questions = {q["id"]: q["questions"] for q in load_prompts([args.reader_questions])}
    src, dst = SNAPSHOTS / args.run_id, JUDGE / args.run_id
    snaps = sorted(src.glob("*/*/*.json"))
    jobs = []
    for pid in sorted({json.loads(s.read_text())["prompt_id"] for s in snaps} & set(questions)):
        jobs.append(("reader", (None, pid), dst / "floor" / f"{pid}.json"))
    for s in snaps:
        model, arm = s.parts[-3], s.parts[-2]
        pid = json.loads(s.read_text())["prompt_id"]
        jobs.append(("analysis", s, dst / "analysis" / model / arm / s.name))
        if pid in questions:
            jobs.append(("reader", (s, pid), dst / "reader" / model / arm / s.name))
        if arm == "llano":
            for other in ("baseline", "llano_nodiag"):
                o = src / model / other / s.name
                if o.exists():
                    jobs.append(("pairwise", (s, o), dst / "pairwise" / model / other / s.name))

    with tempfile.TemporaryDirectory(prefix="cfg-") as config_dir, tempfile.TemporaryDirectory(prefix="judge-") as cwd:
        env = session_env(config_dir)
        anonymize_session(env, cwd)

        def run(job):
            kind, src_, out = job
            try:
                if kind == "analysis":
                    return analysis_task(src_, prompts, args.judge_model, cwd, env, out)
                if kind == "reader":
                    snap, pid = src_
                    return reader_task(snap, pid, questions[pid], prompts, args.reader_model, cwd, env, out)
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
