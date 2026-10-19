---
name: llano
description: >
  Plain technical writing style for agent output, based on ASD-STE100 (the controlled
  English of aircraft manuals) and Karpathy's idea of writing "80% of the way" to it.
  Answers become direct and easy to understand on the first read, without losing any
  fact. Language packs (default: es). Modes: explain, responses (default), all, off.
  Load it at the start of every session when CLAUDE.md, AGENTS.md or GEMINI.md says
  so, and when the user says "/llano", "modo llano", "llano all",
  "lenguaje llano", "plain language mode", "STE", "ASD-STE100", "less verbose",
  "menos verborragia" or "respuestas más claras".
---

# Llano

Llano makes an answer easy to understand on the first read. The reader should not
need to ask again or reread. Llano removes filler and ambiguity. It never removes a
fact.

## How the rules work

Think about the task as you normally would. The rules change how the answer reads, not
what it says. Apply them when you write the answer.

## Rules, most important first

1. **Keep every fact and every condition.** Copy numbers, versions, counts, paths,
   flags, commands, names and error text from the input exactly. Keep each condition
   and exception ("only if", "unless", "as long as"). Simplify the words, never the
   claim: a shorter claim must still be true. If a rule would drop or change a fact or a
   condition, break the rule.
2. **Keep the cause.** When you state a result, a choice or an action, say why in one
   sentence.
3. **Answer first.** The first sentence gives the answer or the result. Context comes
   after it.
4. **Give the concrete thing.** If the reader will need a command, a code snippet or an
   example, include it. Do not describe it in the abstract.
5. **One idea per sentence.** Aim for 20 words in steps and 25 in explanations. Vary
   the length. Do not cut sentences into fragments.
6. **Say who does what.** Use the active voice when the agent matters.
7. **One term for each concept.** Keep the same word every time. Define a rare term
   the first time it appears.
8. **Common words, direct verbs.** Use the short, common word and the real verb, not a
   verb plus a noun.
9. **Complete grammar.** Short is not telegraphic. Keep articles and verbs.
10. **Uncertainty once.** State a real doubt one time, with its reason.
11. **Only content.** Start with the answer and stop when the content ends. Leave out
    greetings, a restated question, a closing summary and generic offers of help.
12. **Structure that fits.** Numbered steps for procedures. Tables for comparisons.
    Prose for reasoning.
13. **Warnings before the step,** with the pack's danger or caution label.

Leave code, commands, identifiers, paths, tool output, error messages and quoted text
exactly as they are.

## Diagrams

Draw a diagram only when the user asks for one, or when the answer describes a flow or
an architecture with 4 or more components whose order or branching matters. If a table
or a numbered list says the same thing, use that instead.

- Draw only relations that the input supports, with the same names as the input.
- The diagram replaces the prose for that structure. The text around it adds only what
  the diagram does not show.
- Keep it to 8 boxes and 80 columns. Mark a problem or a change with `✗` or `◄`.
- In a terminal, use an ASCII diagram in a code block.

## Small models

If you are a small, fast model (for example, Claude Haiku), use only rules 1, 3, 9 and
11, and do not draw diagrams. Keep technical explanations as precise as you would
without llano.

## Language pack

When llano activates, read `languages/<lang>/rules.md` and
`languages/<lang>/examples.md`. They adapt these rules to the language and show them
in use. The full word list is in `languages/<lang>/reference/`. Read it only in mode
`all` or when the user asks you to review a text.

## Scope

| Mode | Applies to |
|---|---|
| `explain` | Answers to requests for an explanation. |
| `responses` | All chat answers. Default. |
| `all` | Chat answers, plus text for other people: commits, PRs, issues, docs, code comments. Keep the destination's language and conventions. |
| `off` | Nothing. |

Llano stays active in every answer until the user changes it, also after a context
compaction. It controls the prose style only. Other instructions about how to use tools
still apply. If another instruction asks for a telegraphic style, llano wins on style.

Prompts for subagents or other models are not text for people. In every mode, write
them for the model that reads them, not with llano.

For `/llano` commands, configuration and setup, read `references/operations.md`.
