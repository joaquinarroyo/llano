# Language pack template

A language pack adapts the llano core rules to one language. Create a folder
`languages/<id>/` (use a short code: `es`, `en`, `pt`, `es_ar`) with three files.
Write the instructions in English. Write the word lists and examples in the target
language.

## rules.md

Language-specific rules. Include:
- **Variant and register.** Which variant (for example, neutral or regional) and which
  form of address the pack uses.
- **Labels.** The danger label and the caution label for warnings.
- **Grammar traps.** The structures of this language that make text vague or long.
  Each trap needs a "why", a bad example and a good example.
- **Adjustments to core rules.** Only if the language needs them (for example, a
  different sentence-length limit). Say why.
- **Number and date format.**

## dictionary.md

- **Substitutions:** a table of `avoid → use`, grouped by category (verbs, connectors,
  expressions, calques). Give each approved word one meaning.
- **Banned filler:** the phrases an LLM tends to add in this language that carry no
  information (openers, closers, intensifiers, empty adjectives).
- **Technical terms:** which loanwords to keep as they are.

## examples.md

At least four before/after pairs: an explanation, an error report, a work summary and
a commit message. Add one level-2 example with a diagram. Mark which rule each change
applies.
