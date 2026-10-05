# llano

Plain technical writing style for coding agents, adapted from
[ASD-STE100](https://www.asd-ste100.org/) (Simplified Technical English). Idea from
[Andrej Karpathy](https://x.com/karpathy/status/2105819303471976479).

Language-agnostic core plus switchable language packs. Available packs: `es` (neutral
Spanish).

## Install

```bash
npx skills add joaquinarroyo/llano -g
```

All language packs are installed. The active one is chosen in the config.

## Always-on activation

A skill loads on demand. To apply llano to every response:

**Claude Code:** install the SessionStart hook. It checks the setup and activates llano
in every new session. It stays silent if everything is fine.

```bash
node ~/.claude/skills/llano/scripts/doctor.mjs --install-hook
```

**Other agents:** add this to `AGENTS.md`:

```markdown
llano: mode=responses, lang=es

At the start of every session, load the `llano` skill with this configuration and
apply it to every response.
```

## Configuration

`~/.config/llano/config.json` (override the path with `$LLANO_CONFIG`):

```json
{ "mode": "responses", "lang": "es" }
```

```bash
node ~/.claude/skills/llano/scripts/doctor.mjs --set mode=all lang=es
```

## Doctor

```bash
node ~/.claude/skills/llano/scripts/doctor.mjs
```

It checks the config, the language pack, duplicate installs, conflicting style skills
(such as caveman) and automatic activation. It also lists the available languages.

## Modes and levels

| Mode | Scope |
|---|---|
| `explain` | Only explanations |
| `responses` | All chat responses (default) |
| `all` | Responses, commits, PRs, docs, code comments |
| `off` | Disabled |

Levels: **1** text (always), **2** diagram (when the subject has 3+ related parts).

Commands: `/llano <mode>`, `/llano lang <id>`, `/llano set …`, `/llano status`,
`/llano doctor`, `/llano install-hook`.

## Add a language

Copy `skills/llano/languages/es/` to `languages/<id>/` and follow
`skills/llano/languages/_template.md`.
