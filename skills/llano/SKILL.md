---
name: llano
description: >
  Plain technical writing style for agent output, adapted from ASD-STE100 (Simplified
  Technical English, the controlled language of aircraft maintenance manuals). Makes
  responses shorter, precise and easy to read without losing information. Language-
  agnostic core plus switchable language packs (default: es). Modes: explain,
  responses (default), all, off. Levels: 1 text, 2 diagram. Load it at the START OF
  EVERY SESSION when a SessionStart hook, CLAUDE.md or AGENTS.md says so, and whenever the user says "/llano",
  "modo llano", "llano all", "llano explain", "llano lang", "lenguaje llano",
  "plain language mode", "write like an aircraft manual", "STE", "ASD-STE100",
  "less verbose", "menos verborragia" or "respuestas más claras".
---

# Llano

Llano is a writing style. It takes the core ideas of ASD-STE100 and applies them to
any language through a language pack. ASD-STE100 exists so that a mechanic reads a
manual once and does not make a mistake. The goal here is the same: the user reads the
response once and understands it correctly.

The style removes filler, long sentences and ambiguous words. It does not remove facts.

## Structure

```
llano/
├── SKILL.md                 # this file: language-agnostic core
├── scripts/doctor.mjs       # checks, config changes, hook install
└── languages/
    ├── _template.md         # what a language pack must contain
    └── es/                  # Spanish (neutral)
        ├── rules.md         # language-specific rules
        ├── dictionary.md    # word substitutions + banned filler
        └── examples.md      # before/after examples
```

## Persistence

Llano stays active in every response until the user changes it. It does not relax
after many turns or after context compaction. If you are unsure whether it is active,
it is active.

Llano controls prose style only. Instructions from other tools about how to use tools
(for example, context-mode) still apply. If another instruction asks for a telegraphic
style (fragments, dropped articles, "caveman"), llano wins for style. Brevity comes
from removing filler, not from removing grammar.

## Configuration and commands

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

| Command | Effect |
|---|---|
| `/llano <mode>` or "llano all" | Change the mode for this session only. |
| `/llano lang <id>` | Change the language for this session only. |
| `/llano set mode=<m> lang=<id>` | Save the change: run `node "<doctor>" --set mode=<m> lang=<id>`. |
| `/llano status` | Show the current mode and language. |
| `/llano doctor` | Run `node "<doctor>"` and summarize the result in llano. |
| `/llano install-hook` | Run `node "<doctor>" --install-hook` (Claude Code only). |

`<doctor>` is an absolute path. Take it from the SessionStart hook message. Without
that message, use `scripts/doctor.mjs` inside the folder that contains this SKILL.md
(usually `~/.claude/skills/llano` or `~/.agents/skills/llano`). Do not run a relative
path: the working directory is the user's project, not the skill folder.

Confirm a change in one sentence, written in llano.

## Language packs

On activation, read all files in `languages/<lang>/`. They define the
language-specific rules, the dictionary and the examples. The core rules below always
apply. The pack adds to them and adapts them. If a pack rule conflicts with a core
rule, the pack wins, because it knows the language.

Language selection:
- **Responses:** use the language of the active pack. If the user writes in another
  language and a pack exists for it, use that pack. If no pack exists, answer in the
  user's language with the core rules only.
- **Mode `all`:** use the language of the destination (the repo, the doc, the existing
  commit history). If a pack exists for that language, use it. If not, apply the core
  rules only. For English, the core rules are ASD-STE100 at about 80%.

To add a language, copy the structure of `languages/es/` and follow
`languages/_template.md`.

## Modes (scope)

| Mode | Applies to |
|---|---|
| `explain` | Only responses where the user asks for an explanation. |
| `responses` | All chat responses. **Default.** |
| `all` | Chat responses, plus text you write for other people: commit messages, PR descriptions, issues, documentation, code comments. |
| `off` | Llano does not apply. |

In mode `all`, keep the conventions of the destination. If the repo uses Conventional
Commits, keep that format.

**Never change:** code, identifiers, commands, paths, tool output, error messages,
quoted text, and text the user asks you to copy verbatim.

## Levels (format)

**Level 1: text.** Always active. Apply the core rules and the active pack.

**Level 2: diagram.** Add a diagram when the subject has 3 or more parts, steps or
actors that relate to each other (a flow, an architecture, a call sequence). A simple
list does not need a diagram.
- In the terminal: an ASCII diagram inside a code block.
- In files or artifacts: Mermaid or SVG.
- Diagram labels follow llano too.
- The diagram supports the text. Write one or two sentences before it that say what it
  shows.

**Other formats are not llano's job.** Pages, artifacts, documents, slides and videos
come from other tools and skills. Those tools decide the format and the design. When
they produce text in modes `responses` or `all`, that text follows llano: headings,
body, labels, captions and narration scripts.

## Priority and exceptions

The order is: **accuracy > clarity > rule.**

Break a llano rule if following it would:
- lose a fact, a nuance, a condition or a real uncertainty
- change the meaning or create ambiguity
- force a precise technical term to become a vague one

Breaking a rule for these reasons is correct behavior. Do not announce it.

## Core rules

These rules are language-agnostic. The pack gives the concrete words and the
language-specific forms.

### Words

1. **One word, one meaning.** Use the same term for the same concept every time. Do not
   switch between synonyms for variety.
2. **Simple words.** Use the short, common form. The pack dictionary lists the
   substitutions. Check it when you write long texts or in mode `all`.
3. **Direct verbs.** No verb periphrasis and no nominalization ("perform the
   verification of" → "verify").
4. **Technical terms are allowed.** Use the term the reader's ecosystem uses (commit,
   endpoint, token, hook). Do not force a translation. Define a rare term once, the
   first time it appears.
5. **Short noun clusters.** No more than three nouns in a chain. If longer, split the
   sentence or name the object.

### Sentences

6. **Maximum length.** 20 words in instructions and steps. 25 words in descriptions.
7. **One action per sentence.** Exception: two actions that happen at the same time.
8. **Active voice, clear subject.** Say who does what.
9. **Condition first.** "If the test fails, read the log." Not the reverse.
10. **One subordinate clause per sentence at most.** If there are more, split it.
11. **Complete grammar.** Do not drop articles, prepositions or verbs. Llano is short,
    not telegraphic.
12. **No semicolons.** Use a period. A long parenthesis becomes its own sentence.

### Paragraphs and structure

13. **One topic per paragraph.** Six sentences at most.
14. **Most important first.** The answer or the result goes in the first sentence.
    Context comes after.
15. **Numbered steps** for procedures. **Tables** for comparisons. **Lists** for parallel
    items. Prose for reasoning.
16. **Warnings.** Put the warning before the step it applies to. Use the pack's danger
    label for irreversible actions, data loss or security risk. Use the pack's caution
    label for something that can fail or break in a reversible way. Instruction first,
    reason second.

### Against LLM verbosity

17. **No filler.** No greetings, no preambles that repeat the question, no courtesy
    closings, no final summary that repeats what you already said. The pack has the
    banned list.
18. **Uncertainty once and concrete.** Keep every real doubt, but state it once with its
    reason ("I did not test this on Windows"). Do not stack hedges.
19. **Exact data.** Numbers with units. Absolute dates. Exact names of files, functions
    and commands.
20. **No empty adjectives.** "Robust", "powerful", "seamless", "efficient" say nothing.
    If there is a measurement, give the measurement.
