# llano

Plain technical writing style for coding agents, adapted from
[ASD-STE100](https://www.asd-ste100.org/) (Simplified Technical English). Idea from
[Andrej Karpathy](https://x.com/karpathy/status/2105819303471976479).

Language-agnostic core plus switchable language packs. Available packs: `es` (neutral
Spanish).

## Install

```bash
npx skills add joaquinarroyo/llano -g
node ~/.agents/skills/llano/scripts/doctor.mjs --install
```

All language packs are installed. The active one is chosen in the configuration.

A skill loads on demand, so installing it is not enough. `--install` turns llano on for
every session. It adds one plain-text block to the global instructions of each agent it
finds:

- **Claude Code:** `~/.claude/CLAUDE.md`
- **Codex:** `~/.codex/AGENTS.md`
- **Gemini CLI:** `~/.gemini/GEMINI.md`

The block holds the configuration:

```markdown
<!-- llano:start -->
llano: mode=responses, lang=es

Load the `llano` skill at the start of every session and apply it with this configuration. …
<!-- llano:end -->
```

The script shows what it will change and asks before writing. It exits with 1 when you
decline, when there is no terminal to ask in, when a write fails, or when a file could
not be checked.

```bash
node ~/.agents/skills/llano/scripts/doctor.mjs --install --dry-run  # only show the plan
node ~/.agents/skills/llano/scripts/doctor.mjs --install --yes      # apply without asking
node ~/.agents/skills/llano/scripts/doctor.mjs --uninstall          # remove the block (backups stay)
```

**Other agents:** add the `llano:` line and the sentence below it to the project's
`AGENTS.md`. For Cursor, use an always-apply rule that loads the llano skill.

The paths above assume the `~/.agents/skills/llano` install. If the skill lives in
`~/.claude/skills/llano`, use that path instead.

## Security

Skill scanners can flag a skill whose script writes to an agent's global configuration,
because a persistent prompt injection works that way. This is what `doctor.mjs` does and
does not do:

- **It writes only the block shown above**, between `<!-- llano:start -->` and
  `<!-- llano:end -->`. The block is text: it asks the agent to load the skill.
- **It never runs on its own.** It adds no hooks, so nothing from this repo runs when a
  session starts. Updating the skill changes text, not code that runs by itself.
- **You run it, see the plan, and confirm.** Without a terminal (for example, when an
  agent runs it), it only shows the plan. `--yes` is for scripts you control.
- **It backs up each file first** (`*.llano-backup-<time>`) and never deletes those
  backups. A file that changed after the plan was shown is left alone.

To skip the script, paste the block into the files above by hand. The skill works the
same.

**Version 1 users:** version 1 added a `SessionStart` hook that ran `doctor.mjs` in every
session, and kept the configuration in `~/.config/llano/config.json`. Run
`doctor.mjs --install` again. It removes the hook and copies your configuration into the
block. Until then, the hook only shows you a message with that command, and llano does
not load on its own.

## Configuration

```bash
node ~/.agents/skills/llano/scripts/doctor.mjs --set mode=all lang=es
```

`--set` rewrites the block in each agent, with the same plan and confirmation as
`--install`.

## Doctor

```bash
node ~/.agents/skills/llano/scripts/doctor.mjs
```

It checks the block in each agent, leftovers from version 1, the language packs,
duplicate installs and conflicting style skills (such as caveman). It also lists the
available languages.

## Modes and levels

| Mode | Scope |
|---|---|
| `explain` | Only explanations |
| `responses` | All chat responses (default) |
| `all` | Responses, commits, PRs, docs, code comments |
| `off` | Disabled |

Prompts for subagents or other models never use llano.

Levels: **1** text (always), **2** diagram (when asked, or for a flow or architecture
with 4 or more components).

Karpathy's other two formats, interactive HTML and explainer videos, are out of scope.
Other tools and skills produce them (for example, Claude Code artifacts). Llano only
governs the text inside them. A skill that loads later and sets its own style can still
override llano.

Commands: `/llano <mode>`, `/llano lang <id>`, `/llano set …`, `/llano install`,
`/llano uninstall`, `/llano status`, `/llano doctor`.

## Add a language

Copy `skills/llano/languages/es/` to `languages/<id>/` and follow
`skills/llano/languages/_template.md`.
