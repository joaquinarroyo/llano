# Results: v3

Claude Code 2.1.292. Models: haiku, sonnet. Runs: 2. Judge: sonnet. Reader: haiku.

Knowledge floor: the reader answers 0 of 42 questions correctly with no text. 'Self-sufficiency, questions not known without text' excludes them.

## All models

### Single turn: baseline vs llano

| | baseline | llano |
|---|---:|---:|
| Words (median) | 191 | 166 |
| Output tokens incl. thinking (median) | 704 | 768 |
| Visible tokens (median) | 515 | 426 |
| Words per kept fact (median) | 44 | 38 |
| Filler phrases per answer | 0.12 | 0.06 |
| First sentence answers | 75% | 92% |
| Self-sufficiency (reader correct) | 90% | 85% |
| Self-sufficiency, questions not known without text | 90% | 85% |
| Key facts kept (verified) | 88% | 87% |
| Wrong claims per answer (verified) | 0.33 | 0.71 |
| Rule violations / 100 words | 1.13 | 0.64 |
| INFLESZ | 65.8 | 74.6 |
| Thinking share of output | 19% | 40% |
| Input tokens (median) | 2590 | 6211 |
| Answers with a diagram | 0% | 0% |
| Diagram share of the answer | -- | -- |
| Judge quotes not found in text | 0% | 0% |
| Diagram verdicts (ok/wrong/redundant) | 0/0/1 | 0/0/0 |

- **Blind preference vs baseline (both orders):** llano 16, tie 16, other 16. Score 50% (ties count half; CI 35–65%). By prompt: 5 llano, 6 other, 1 even, p = 1.0000.

Paired by prompt, llano vs baseline:
- Words (median): better in 10, worse in 2, equal in 0 of 12 prompts (p = 0.0386).
- Output tokens incl. thinking (median): better in 6, worse in 6, equal in 0 of 12 prompts (p = 1.0000).
- Visible tokens (median): better in 12, worse in 0, equal in 0 of 12 prompts (p = 0.0005).
- Words per kept fact (median): better in 9, worse in 3, equal in 0 of 12 prompts (p = 0.1460).
- Filler phrases per answer: better in 4, worse in 1, equal in 7 of 12 prompts (p = 0.3750).
- First sentence answers: better in 5, worse in 1, equal in 6 of 12 prompts (p = 0.2188).
- Self-sufficiency (reader correct): better in 1, worse in 6, equal in 5 of 12 prompts (p = 0.1250).
- Self-sufficiency, questions not known without text: better in 1, worse in 6, equal in 5 of 12 prompts (p = 0.1250).
- Key facts kept (verified): better in 2, worse in 7, equal in 3 of 12 prompts (p = 0.1797).
- Wrong claims per answer (verified): better in 0, worse in 10, equal in 2 of 12 prompts (p = 0.0020).
- Rule violations / 100 words: better in 9, worse in 2, equal in 1 of 12 prompts (p = 0.0654).
- INFLESZ: better in 12, worse in 0, equal in 0 of 12 prompts (p = 0.0005).

### Conversations

| Turn | Viol./100 baseline | Viol./100 llano | Facts baseline | Facts llano | Words baseline | Words llano |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1.47 | 0.75 | 84% | 91% | 223 | 171 |
| 2 | 1.05 | 0.64 | 94% | 97% | 236 | 175 |
| 3 | 0.28 | 0.58 | 89% | 92% | 155 | 100 |

- Self-sufficiency: baseline 100%, llano 100%.
- Wrong claims per conversation: baseline 1.12, llano 1.25.
- **Blind preference, whole conversation (both orders):** llano 4, tie 3, other 1. Score 69% (ties count half; CI 62–75%). By prompt: 2 llano, 0 other, 0 even, p = 0.5000.

## haiku

### Single turn: baseline vs llano

| | baseline | llano |
|---|---:|---:|
| Words (median) | 110 | 126 |
| Output tokens incl. thinking (median) | 588 | 634 |
| Visible tokens (median) | 414 | 337 |
| Words per kept fact (median) | 30 | 33 |
| Filler phrases per answer | 0.04 | 0.04 |
| First sentence answers | 71% | 88% |
| Self-sufficiency (reader correct) | 79% | 74% |
| Self-sufficiency, questions not known without text | 79% | 74% |
| Key facts kept (verified) | 78% | 77% |
| Wrong claims per answer (verified) | 0.62 | 1.21 |
| Rule violations / 100 words | 1.17 | 0.75 |
| INFLESZ | 58.7 | 72.0 |
| Thinking share of output | 34% | 50% |
| Input tokens (median) | 3410 | 6225 |
| Answers with a diagram | 0% | 0% |
| Diagram share of the answer | -- | -- |
| Judge quotes not found in text | 1% | 0% |
| Diagram verdicts (ok/wrong/redundant) | 0/0/1 | 0/0/0 |

- **Blind preference vs baseline (both orders):** llano 6, tie 9, other 9. Score 44% (ties count half; CI 27–60%). By prompt: 3 llano, 5 other, 4 even, p = 0.7266.

Paired by prompt, llano vs baseline:
- Words (median): better in 6, worse in 6, equal in 0 of 12 prompts (p = 1.0000).
- Output tokens incl. thinking (median): better in 6, worse in 6, equal in 0 of 12 prompts (p = 1.0000).
- Visible tokens (median): better in 12, worse in 0, equal in 0 of 12 prompts (p = 0.0005).
- Words per kept fact (median): better in 5, worse in 7, equal in 0 of 12 prompts (p = 0.7744).
- Filler phrases per answer: better in 1, worse in 1, equal in 10 of 12 prompts (p = 1.0000).
- First sentence answers: better in 3, worse in 0, equal in 9 of 12 prompts (p = 0.2500).
- Self-sufficiency (reader correct): better in 1, worse in 4, equal in 7 of 12 prompts (p = 0.3750).
- Self-sufficiency, questions not known without text: better in 1, worse in 4, equal in 7 of 12 prompts (p = 0.3750).
- Key facts kept (verified): better in 3, worse in 6, equal in 3 of 12 prompts (p = 0.5078).
- Wrong claims per answer (verified): better in 0, worse in 10, equal in 2 of 12 prompts (p = 0.0020).
- Rule violations / 100 words: better in 6, worse in 5, equal in 1 of 12 prompts (p = 1.0000).
- INFLESZ: better in 12, worse in 0, equal in 0 of 12 prompts (p = 0.0005).

### Conversations

| Turn | Viol./100 baseline | Viol./100 llano | Facts baseline | Facts llano | Words baseline | Words llano |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2.18 | 0.64 | 69% | 81% | 120 | 137 |
| 2 | 0.96 | 0.75 | 88% | 94% | 135 | 135 |
| 3 | 0.00 | 0.29 | 84% | 91% | 84 | 100 |

- Self-sufficiency: baseline 100%, llano 100%.
- Wrong claims per conversation: baseline 2.00, llano 2.50.
- **Blind preference, whole conversation (both orders):** llano 0, tie 3, other 1. Score 38% (ties count half; CI 25–50%). By prompt: 0 llano, 1 other, 1 even, p = 1.0000.

## sonnet

### Single turn: baseline vs llano

| | baseline | llano |
|---|---:|---:|
| Words (median) | 292 | 208 |
| Output tokens incl. thinking (median) | 1150 | 988 |
| Visible tokens (median) | 998 | 678 |
| Words per kept fact (median) | 61 | 45 |
| Filler phrases per answer | 0.21 | 0.08 |
| First sentence answers | 79% | 96% |
| Self-sufficiency (reader correct) | 100% | 97% |
| Self-sufficiency, questions not known without text | 100% | 97% |
| Key facts kept (verified) | 98% | 97% |
| Wrong claims per answer (verified) | 0.04 | 0.21 |
| Rule violations / 100 words | 1.10 | 0.54 |
| INFLESZ | 72.9 | 77.2 |
| Thinking share of output | 11% | 34% |
| Input tokens (median) | 1585 | 5223 |
| Answers with a diagram | 0% | 0% |
| Diagram share of the answer | -- | -- |
| Judge quotes not found in text | 0% | 1% |
| Diagram verdicts (ok/wrong/redundant) | 0/0/0 | 0/0/0 |

- **Blind preference vs baseline (both orders):** llano 10, tie 7, other 7. Score 56% (ties count half; CI 38–75%). By prompt: 6 llano, 5 other, 1 even, p = 1.0000.

Paired by prompt, llano vs baseline:
- Words (median): better in 11, worse in 1, equal in 0 of 12 prompts (p = 0.0063).
- Output tokens incl. thinking (median): better in 7, worse in 5, equal in 0 of 12 prompts (p = 0.7744).
- Visible tokens (median): better in 11, worse in 1, equal in 0 of 12 prompts (p = 0.0063).
- Words per kept fact (median): better in 10, worse in 2, equal in 0 of 12 prompts (p = 0.0386).
- Filler phrases per answer: better in 4, worse in 1, equal in 7 of 12 prompts (p = 0.3750).
- First sentence answers: better in 3, worse in 1, equal in 8 of 12 prompts (p = 0.6250).
- Self-sufficiency (reader correct): better in 0, worse in 2, equal in 10 of 12 prompts (p = 0.5000).
- Self-sufficiency, questions not known without text: better in 0, worse in 2, equal in 10 of 12 prompts (p = 0.5000).
- Key facts kept (verified): better in 1, worse in 3, equal in 8 of 12 prompts (p = 0.6250).
- Wrong claims per answer (verified): better in 0, worse in 4, equal in 8 of 12 prompts (p = 0.1250).
- Rule violations / 100 words: better in 9, worse in 2, equal in 1 of 12 prompts (p = 0.0654).
- INFLESZ: better in 12, worse in 0, equal in 0 of 12 prompts (p = 0.0005).

### Conversations

| Turn | Viol./100 baseline | Viol./100 llano | Facts baseline | Facts llano | Words baseline | Words llano |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.76 | 0.86 | 100% | 100% | 367 | 254 |
| 2 | 1.15 | 0.52 | 100% | 100% | 330 | 248 |
| 3 | 0.56 | 0.88 | 94% | 94% | 203 | 120 |

- Self-sufficiency: baseline 100%, llano 100%.
- Wrong claims per conversation: baseline 0.25, llano 0.00.
- **Blind preference, whole conversation (both orders):** llano 4, tie 0, other 0. Score 100% (ties count half; CI 100–100%). By prompt: 2 llano, 0 other, 0 even, p = 0.5000.
