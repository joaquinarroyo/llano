# Evals

Measures what llano changes in Claude Code output, against a plain conciseness
instruction. Every call goes through `claude -p`, so it runs on a Claude
subscription with no API key.

## Arms

All arms keep Claude Code's default system prompt. They differ only in the text
added with `--append-system-prompt`.

| Arm | Added text |
|---|---|
| `baseline` | none |
| `terse` | `Responde de forma concisa.` |
| `llano` | `terse` + `SKILL.md` + the `es` pack |
| `caveman` | `terse` + caveman's `SKILL.md` (pinned in `arms/caveman.md`) |

The honest delta is **llano vs terse**. Comparing only against `baseline` mixes the
style with the generic request to be brief. This follows the lesson from
[caveman's evals](https://github.com/JuliusBrussee/caveman/tree/main/evals).

## Isolation

Each call runs with `--setting-sources project --disable-slash-commands
--strict-mcp-config --tools ""` in an empty temporary folder. No user hooks,
plugins, skills, MCP servers or tools are loaded. A canary runs first: it asks the
model to copy every extra instruction it received and aborts if the answer names
llano, caveman or context-mode. The canary does not name these words in its
question, so the model cannot find them there.

## Metrics

| Metric | Source | Deterministic |
|---|---|---|
| Visible output tokens | Claude usage, minus thinking tokens | yes |
| Words | `lint.py`, prose only (no code, no tables) | yes |
| Rule violations per 100 words | `lint.py`, rules and dictionary from the `es` pack | yes |
| INFLESZ readability | `lint.py`, Szigriszt-Pazos formula | yes |
| Fidelity (key facts kept, wrong claims) | `judge.py`, Claude Sonnet | no |
| Blind preference, llano vs each arm | `judge.py`, Claude Sonnet, random A/B order | no |

## Run

```bash
uv run run.py --run-id pilot --models sonnet --runs 1
uv run judge.py --run-id pilot --judge-model sonnet
uv run measure.py --run-id pilot
cd report && tectonic report.tex
```

Runs resume: existing results are skipped. `snapshots/`, `judge/` and `results/`
are committed as the source of the reported numbers.

## Files

| File | Role |
|---|---|
| `prompts/es.jsonl` | 24 Spanish prompts in 6 categories, each with 5 key facts |
| `run.py` | Generates responses per model, arm, prompt and run |
| `judge.py` | Fidelity and blind pairwise judgments |
| `lint.py` | Rule checker and readability. Also works alone: `uv run lint.py file.md` |
| `measure.py` | Summary, LaTeX tables and macros, PDF figures |
| `report/` | LaTeX report, built with `tectonic` |

## Limits

- The linter measures adherence to llano's own rules, so llano has an advantage on
  that metric by design. Fidelity and blind preference balance it.
- The judge and the generator are both Claude models.
- The prompts were written by the skill's author.
