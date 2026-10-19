# Llano operations

Read this file only when the user runs a `/llano` command or asks about llano's setup.

## Configuration

The configuration lives in a marked, plain-text block in the global instructions of each
agent. `doctor.mjs --install` writes it:

```markdown
<!-- llano:start -->
llano: mode=responses, lang=es

Load the `llano` skill at the start of every session and apply it with this configuration. …
<!-- llano:end -->
```

Where the active configuration comes from, in order:
1. A change the user made in this session with a command below.
2. A `llano: mode=…, lang=…` line in CLAUDE.md, AGENTS.md or GEMINI.md: the block, or a
   line the user added by hand.
3. Defaults: `mode=responses, lang=es`.

## Commands

| Command | Effect |
|---|---|
| `/llano <mode>` or "llano all" | Change the mode for this session only. |
| `/llano lang <id>` | Change the language for this session only. |
| `/llano set mode=<m> lang=<id>` | Save the change in the block: run `node "<doctor>" --set mode=<m> lang=<id>`. |
| `/llano install` | Write or update the block: run `node "<doctor>" --install`. |
| `/llano uninstall` | Remove the block: run `node "<doctor>" --uninstall`. |
| `/llano status` | Show the current mode and language. |
| `/llano doctor` | Run `node "<doctor>"` and summarize the result. |

`--set`, `--install` and `--uninstall` write to the user's global instructions. When you
run them, there is no terminal to ask in, so the script only shows its plan and exits
with 1. Show the plan to the user. Run the same command again with `--yes` only after the
user approves it.

`<doctor>` is an absolute path. Take it from the llano block. Without the block, use
`scripts/doctor.mjs` inside the folder that contains SKILL.md (usually
`~/.claude/skills/llano` or `~/.agents/skills/llano`). Do not run a relative path: the
working directory is the user's project, not the skill folder.

Confirm a change in one sentence.

## Language selection

- **Responses:** use the language of the active pack. If the user writes in another
  language and a pack exists for it, use that pack. If no pack exists, answer in the
  user's language with the core rules only.
- **Mode `all`:** use the language of the destination (the repo, the doc, the commit
  history). If no pack exists for it, apply the core rules only. For English, the core
  rules are ASD-STE100 at about 80%.

To add a language, copy `languages/es/` and follow `languages/_template.md`.

## Activation in each agent

| Agent | Always-on activation |
|---|---|
| Claude Code | The block in `~/.claude/CLAUDE.md` (`--install`) |
| Codex | The block in `~/.codex/AGENTS.md` (`--install`) |
| Gemini CLI | The block in `~/.gemini/GEMINI.md` (`--install`) |
| Others that read AGENTS.md | A `llano: mode=responses, lang=es` line in the project's AGENTS.md |
| Cursor | An always-apply rule that loads the llano skill |

## Version 1

Version 1 used a SessionStart hook and `~/.config/llano/config.json`. `--install` removes
that hook from `~/.claude/settings.json` and copies the values from the config file into
the block. After that, nothing reads the config file. The doctor reports a hook in any
other settings file, and the user removes it by hand.
