# Evals

Measures what llano changes in Claude Code output. Every call goes through
`claude -p`, so it runs on a Claude subscription with no API key.

## Goal

Llano follows [Karpathy's point](https://x.com/karpathy/status/2105819303471976479):
people spend more and more time reading LLM output, so the output must be easy to
understand. The eval asks one question: **does llano make responses easier to
understand, without losing precision?**

| Role | Metric | Why |
|---|---|---|
| **Primary** | Blind preference: which response a developer understands better in one read | Measures the goal directly |
| Support | Rule violations per 100 words, INFLESZ readability | Explain *why* a response reads better |
| **Condition** | Fidelity: key facts kept, wrong claims added | Clarity must not cost precision |
| Secondary | Words and visible tokens | Shorter output is a side effect, not the goal |

A result where llano reads better but drops facts is a failure. A result where llano
saves no tokens but reads better and keeps every fact is a success.

## Arms

| Arm | What runs |
|---|---|
| `baseline` | Claude Code as it ships, with nothing added |
| `llano` | The same, plus `SKILL.md` and the `es` pack (`--append-system-prompt`) |

## Isolation

The eval must not depend on the machine or the person that runs it. No personal
skills, settings, memory or account data may reach the model. No extra token or API
key is needed.

- **Clean config, same sign-in.** `CLAUDE_CONFIG_DIR` points to an empty temporary
  folder, so nothing from `~/.claude` is read: no settings, hooks, plugins, skills,
  memory or `CLAUDE.md`. `CLAUDE_SECURESTORAGE_CONFIG_DIR=""` keeps using the existing
  sign-in from the system keychain. Only the credentials are shared, not the profile.
- **Anonymized profile.** Claude Code puts the account email in the prompt. A first
  call fills the temporary profile. The harness then removes the email and names and
  marks the profile as fresh, so Claude Code does not fetch it again for 24 hours.
  `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` stops the bootstrap call that would
  write the email back. Before every call, the harness checks the profile and aborts
  if personal data returns.
- **Nothing extra loaded.** `--setting-sources project`, `--disable-slash-commands`,
  `--strict-mcp-config`, `--tools ""`, auto-memory off
  (`CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `autoMemoryEnabled: false`),
  `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1`, an empty temporary working folder, no session
  saved.
- **Canary.** Before each run, the model is asked to copy every extra instruction and
  any user or account data it received. The run aborts if the answer contains llano,
  other style skills, the home path, the user name or an email address. The canary
  does not name these words in its question, so the model cannot find them there.

What the model still sees: Claude Code's default system prompt, the date, the OS,
the shell and a temporary working folder.

## Prompt sets

- `prompts/es.jsonl`: 24 single-turn prompts in 6 categories, each with 5 key facts.
- `prompts/es_conversations.jsonl`: 4 conversations of 3 turns, each turn with its
  own key facts. They check that the style holds after the first answer, as it must
  in a real session.

## Metrics

| Metric | Source | Deterministic |
|---|---|---|
| Blind preference, llano vs baseline | `judge.py`, random A/B order | no |
| Fidelity (key facts kept, wrong claims) | `judge.py` | no |
| Rule violations per 100 words | `lint.py`, rules and dictionary from the `es` pack | yes |
| INFLESZ readability | `lint.py`, Szigriszt-Pazos formula | yes |
| Words, visible output tokens | `lint.py`, Claude usage minus thinking tokens | yes |

The judge is Claude Sonnet, in the same isolated setup.

## Statistics

Runs of the same prompt are not independent. Significance and confidence intervals
are computed over prompts (clustered), not over individual comparisons. The pooled
view also averages over models before testing.

## Run

```bash
uv run run.py --run-id full --models opus sonnet haiku --runs 3
uv run judge.py --run-id full --judge-model sonnet
uv run measure.py --run-id full     # writes results/full/summary.md
```

Runs resume: existing results are skipped. If the skill changes, a run refuses to
continue under the same `--run-id`. `snapshots/`, `judge/` and `results/` are
committed as the source of the reported numbers.

Size of the full run: 24 prompts × 2 arms × 3 models × 3 runs = 432 responses, plus
72 conversations. The judge adds about 756 calls.

## Files

| File | Role |
|---|---|
| `run.py` | Generates responses per model, arm, prompt and run |
| `judge.py` | Fidelity and blind pairwise judgments |
| `lint.py` | Rule checker and readability. Also works alone: `uv run lint.py file.md` |
| `measure.py` | Clustered statistics per model and pooled |
| `report/` | LaTeX report (to be updated for the two-arm design) |

## Limits

- The linter measures adherence to llano's own rules, so llano has an advantage on
  that metric by design. Fidelity and blind preference balance it.
- The judge and the generators are Claude models. With three generator models, the
  judge does not only grade its own model.
- The prompts were written by the skill's author.
