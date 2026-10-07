# Llano operations

Read this file only when the user runs a `/llano` command or asks about llano's setup.

## Configuration

The persistent configuration lives in `~/.config/llano/config.json` (or the path in
`$LLANO_CONFIG`):

```json
{ "mode": "responses", "lang": "es" }
```

Where the active configuration comes from, in order:
1. A change the user made in this session with a command below.
2. The SessionStart hook message (`llano is active: mode=…, lang=…`).
3. A `llano: mode=…, lang=…` line in AGENTS.md or CLAUDE.md (agents without hooks).
4. The config file.
5. Defaults: `mode=responses, lang=es`.

## Commands

| Command | Effect |
|---|---|
| `/llano <mode>` or "llano all" | Change the mode for this session only. |
| `/llano lang <id>` | Change the language for this session only. |
| `/llano set mode=<m> lang=<id>` | Save the change: run `node "<doctor>" --set mode=<m> lang=<id>`. |
| `/llano status` | Show the current mode and language. |
| `/llano doctor` | Run `node "<doctor>"` and summarize the result. |
| `/llano install-hook` | Run `node "<doctor>" --install-hook` (Claude Code only). |

`<doctor>` is an absolute path. Take it from the SessionStart hook message. Without
that message, use `scripts/doctor.mjs` inside the folder that contains SKILL.md
(usually `~/.claude/skills/llano` or `~/.agents/skills/llano`). Do not run a relative
path: the working directory is the user's project, not the skill folder.

Confirm a change in one sentence.

## Language selection

- **Responses:** use the language of the active pack. If the user writes in another
  language and a pack exists for it, use that pack. If no pack exists, answer in the
  user's language with the core rules only.
- **Mode `all`:** use the language of the destination (the repo, the doc, the commit
  history). If no pack exists for it, apply the core rules only. For English, the core
  rules are ASD-STE100 at about 80%.

To add a language, copy `languages/es/` and follow `languages/_template.md`.

## Activation in other agents

| Agent | Always-on activation |
|---|---|
| Claude Code | SessionStart hook: `node "<doctor>" --install-hook` |
| Codex and others that read AGENTS.md | A `llano: mode=responses, lang=es` line in AGENTS.md |
| Cursor | An always-apply rule that loads the llano skill |
