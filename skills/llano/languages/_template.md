# Language pack template

A language pack adapts the llano core rules to one language. Create a folder
`languages/<id>/` (use a short code: `es`, `en`, `pt`, `es_ar`) with this structure:

```
<id>/
├── rules.md               always loaded, short (about 500 words)
├── examples.md            always loaded, 3–4 examples in <example> tags
└── reference/
    └── dictionary.md      loaded on demand and used by the eval linter
```

Keep the always-loaded files small. The agent reads them in every session, and long
rule lists lower accuracy, most of all on small models.
Write the instructions in English. Write the word lists and examples in the target
language.

## rules.md (always loaded)

Language-specific rules, written as what to do. Include the 15–20 most frequent word
substitutions as a short table. Include:
- **Variant and register.** Which variant (for example, neutral or regional) and which
  form of address the pack uses.
- **Labels.** The danger label and the caution label for warnings.
- **Grammar traps.** The structures of this language that make text vague or long.
  Each trap needs a "why", a bad example and a good example.
- **Adjustments to core rules.** Only if the language needs them (for example, a
  different sentence-length limit). Say why.
- **Number and date format.**

## reference/dictionary.md (on demand)

- **Substitutions:** a table of `avoid → use`, grouped by category (verbs, connectors,
  expressions, calques). Give each approved word one meaning.
- **Banned filler:** the phrases an LLM tends to add in this language that carry no
  information (openers, closers, intensifiers, empty adjectives).
- **Technical terms:** which loanwords to keep as they are.

## examples.md (always loaded)

Three or four short before/after pairs inside `<example>` tags. Each llano version
must keep every value and cause from its input. Include one diagram example that draws
only relations stated in the text.
