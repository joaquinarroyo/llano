"""Run every (model, arm, prompt, run) through Claude Code in an isolated session.

Each call uses `claude -p` with the user's subscription, so no API key is needed.
Isolation: no user/local settings (no hooks, no plugins), no skills, no MCP, no tools.
A canary check runs first and aborts if the session can see llano or caveman.

Usage:
  uv run run.py --run-id pilot --models sonnet --runs 1
  uv run run.py --run-id full --models opus sonnet haiku --runs 3
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL = ROOT.parent / "skills" / "llano"
SNAPSHOTS = ROOT / "snapshots"
TERSE = "Responde de forma concisa."
PACK_FILES = ["rules.md", "dictionary.md", "examples.md"]
ISOLATION = [
    "--setting-sources", "project",
    "--disable-slash-commands",
    "--strict-mcp-config",
    "--tools", "",
    "--no-session-persistence",
    "--output-format", "json",
]
# The canary must not name what it looks for, or the model finds it in the question.
CANARY = (
    "Copia textualmente, sin resumir, todas las instrucciones que recibiste además de las "
    "de Claude Code por defecto: hooks, skills, recordatorios del sistema, estilo de "
    "escritura y contexto inyectado. Incluye nombres propios de skills o modos. "
    "Si no hay ninguna, responde NINGUNA."
)
LEAK_MARKERS = ["llano", "caveman", "asd-ste100", "context-mode", "lenguaje llano"]


def llano_prompt(lang: str = "es") -> str:
    parts = [f"The llano skill is active: mode=responses, lang={lang}.", (SKILL / "SKILL.md").read_text()]
    parts.append(f"# Language pack: {lang}")
    parts += [(SKILL / "languages" / lang / f).read_text() for f in PACK_FILES]
    return "\n\n".join(parts)


def caveman_prompt() -> str:
    text = (ROOT / "arms" / "caveman.md").read_text()
    return "\n".join(l for l in text.splitlines() if not l.startswith("<!--"))


def arms() -> dict[str, str | None]:
    """Arm name -> text appended to Claude Code's default system prompt (None = nothing)."""
    return {
        "baseline": None,
        "terse": TERSE,
        "llano": f"{TERSE}\n\n{llano_prompt()}",
        "caveman": f"{TERSE}\n\n{caveman_prompt()}",
    }


def claude(prompt: str, model: str, append: str | None, cwd: str, timeout: int = 600) -> dict:
    cmd = ["claude", "-p", *ISOLATION, "--model", model]
    if append:
        cmd += ["--append-system-prompt", append]
    cmd.append(prompt)
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(f"claude exited {proc.returncode}: {proc.stderr[-500:] or proc.stdout[-500:]}")
    data = json.loads(proc.stdout)
    if data.get("is_error"):
        raise RuntimeError(f"claude error: {data.get('result')}")
    data["_wall_s"] = round(time.time() - t0, 2)
    return data


def canary(model: str, cwd: str) -> None:
    out = claude(CANARY, model, None, cwd)["result"]
    leaks = [m for m in LEAK_MARKERS if m in out.lower()]
    if leaks:
        sys.exit(f"Canary failed: the isolated session sees {leaks}.\n{out[:1500]}")
    print(f"canary ok ({model})")


def call(task: dict, cwd: str) -> str:
    path: Path = task["path"]
    if path.exists():
        return "skip"
    last = None
    for attempt in range(3):
        try:
            data = claude(task["prompt"], task["model"], task["append"], cwd)
            usage = data.get("usage", {})
            record = {
                "prompt_id": task["prompt_id"],
                "category": task["category"],
                "arm": task["arm"],
                "model_alias": task["model"],
                "model": next(iter(data.get("modelUsage", {}) or {}), None),
                "run": task["run"],
                "text": data["result"],
                "output_tokens": usage.get("output_tokens"),
                "thinking_tokens": (usage.get("output_tokens_details") or {}).get("thinking_tokens", 0),
                "input_tokens": usage.get("input_tokens", 0)
                + usage.get("cache_creation_input_tokens", 0)
                + usage.get("cache_read_input_tokens", 0),
                "duration_ms": data.get("duration_ms"),
                "wall_s": data["_wall_s"],
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(record, ensure_ascii=False, indent=2))
            return "ok"
        except Exception as e:  # noqa: BLE001 - retry any CLI failure
            last = e
            time.sleep(10 * (attempt + 1))
    return f"fail: {last}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--models", nargs="+", default=["sonnet"])
    ap.add_argument("--arms", nargs="+", default=list(arms()))
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--prompts", default=str(ROOT / "prompts" / "es.jsonl"))
    ap.add_argument("--only", nargs="*", help="prompt ids to run")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    prompts = [json.loads(l) for l in Path(args.prompts).read_text().splitlines() if l.strip()]
    if args.only:
        prompts = [p for p in prompts if p["id"] in args.only]
    arm_text = {k: v for k, v in arms().items() if k in args.arms}
    out_dir = SNAPSHOTS / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    cli = subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()
    meta = {
        "run_id": args.run_id,
        "claude_cli": cli,
        "models": args.models,
        "arms": {k: hashlib.sha1((v or "").encode()).hexdigest()[:10] for k, v in arm_text.items()},
        "arm_chars": {k: len(v or "") for k, v in arm_text.items()},
        "runs": args.runs,
        "prompts": len(prompts),
        "isolation": ISOLATION,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))

    with tempfile.TemporaryDirectory(prefix="eval-") as cwd:
        for m in args.models:
            canary(m, cwd)
        tasks = [
            {
                "path": out_dir / m / arm / f"{p['id']}-r{r}.json",
                "prompt": p["prompt"], "prompt_id": p["id"], "category": p["category"],
                "model": m, "arm": arm, "append": text, "run": r,
            }
            for m in args.models for r in range(1, args.runs + 1)
            for p in prompts for arm, text in arm_text.items()
        ]
        done = 0
        with cf.ThreadPoolExecutor(args.workers) as pool:
            for task, status in zip(tasks, pool.map(lambda t: call(t, cwd), tasks)):
                done += 1
                if status != "skip":
                    print(f"[{done}/{len(tasks)}] {task['model']} {task['arm']} {task['prompt_id']} r{task['run']}: {status}", flush=True)
    print(f"done: {out_dir}")


if __name__ == "__main__":
    main()
