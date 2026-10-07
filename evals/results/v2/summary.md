# Results: v2

Claude Code 2.1.292. Models: haiku, opus, sonnet. Runs: 3. Judge: sonnet. Reader: haiku.

Knowledge floor: the reader answers 0 of 42 questions correctly with no text. 'Self-sufficiency, questions not known without text' excludes them.

## All models

### Single turn: baseline vs llano

| | baseline | llano |
|---|---:|---:|
| Words (median) | 227 | 203 |
| Output tokens incl. thinking (median) | 962 | 946 |
| Visible tokens (median) | 842 | 649 |
| Words per kept fact (median) | 49 | 46 |
| Filler phrases per answer | 0.16 | 0.03 |
| First sentence answers | 73% | 90% |
| Self-sufficiency (reader correct) | 91% | 93% |
| Self-sufficiency, questions not known without text | 91% | 93% |
| Key facts kept (verified) | 90% | 91% |
| Wrong claims per answer (verified) | 0.26 | 0.38 |
| Rule violations / 100 words | 1.05 | 0.51 |
| INFLESZ | 68.9 | 76.1 |
| Thinking share of output | 13% | 35% |
| Input tokens (median) | 1698 | 5285 |
| Answers with a diagram | 4% | 13% |
| Diagram share of the answer | 11% | 9% |
| Judge quotes not found in text | 0% | 0% |
| Diagram verdicts (ok/wrong/redundant) | 1/1/1 | 6/1/7 |

- **Blind preference vs baseline (both orders):** llano 46, tie 21, other 41. Score 52% (ties count half; CI 41–63%). By prompt: 7 llano, 4 other, 1 even, p = 0.5488.

Paired by prompt, llano vs baseline:
- Words (median): better in 9, worse in 3, equal in 0 of 12 prompts (p = 0.1460).
- Output tokens incl. thinking (median): better in 4, worse in 8, equal in 0 of 12 prompts (p = 0.3877).
- Visible tokens (median): better in 12, worse in 0, equal in 0 of 12 prompts (p = 0.0005).
- Words per kept fact (median): better in 8, worse in 4, equal in 0 of 12 prompts (p = 0.3877).
- Filler phrases per answer: better in 7, worse in 1, equal in 4 of 12 prompts (p = 0.0703).
- First sentence answers: better in 6, worse in 0, equal in 6 of 12 prompts (p = 0.0312).
- Self-sufficiency (reader correct): better in 4, worse in 2, equal in 6 of 12 prompts (p = 0.6875).
- Self-sufficiency, questions not known without text: better in 4, worse in 2, equal in 6 of 12 prompts (p = 0.6875).
- Key facts kept (verified): better in 3, worse in 8, equal in 1 of 12 prompts (p = 0.2266).
- Wrong claims per answer (verified): better in 2, worse in 8, equal in 2 of 12 prompts (p = 0.1094).
- Rule violations / 100 words: better in 11, worse in 1, equal in 0 of 12 prompts (p = 0.0063).
- INFLESZ: better in 12, worse in 0, equal in 0 of 12 prompts (p = 0.0005).

### Diagrams: llano vs llano without diagrams (structured prompts)

| | llano | llano_nodiag |
|---|---:|---:|
| Words (median) | 238 | 242 |
| Output tokens incl. thinking (median) | 1084 | 986 |
| Visible tokens (median) | 738 | 648 |
| Words per kept fact (median) | 54 | 50 |
| Filler phrases per answer | 0.00 | 0.04 |
| First sentence answers | 85% | 91% |
| Self-sufficiency (reader correct) | 93% | 91% |
| Self-sufficiency, questions not known without text | 93% | 91% |
| Key facts kept (verified) | 91% | 91% |
| Wrong claims per answer (verified) | 0.41 | 0.44 |
| Rule violations / 100 words | 0.58 | 0.80 |
| INFLESZ | 78.5 | 78.1 |
| Thinking share of output | 34% | 27% |
| Input tokens (median) | 5326 | 4972 |
| Answers with a diagram | 24% | 0% |
| Diagram share of the answer | 9% | -- |
| Judge quotes not found in text | 0% | 0% |
| Diagram verdicts (ok/wrong/redundant) | 5/1/7 | 0/0/0 |

- **Blind preference vs no diagrams (both orders):** llano 17, tie 18, other 19. Score 48% (ties count half; CI 37–57%). By prompt: 3 llano, 3 other, 0 even, p = 1.0000.

Paired by prompt, llano vs llano_nodiag:
- Words (median): better in 3, worse in 3, equal in 0 of 6 prompts (p = 1.0000).
- Output tokens incl. thinking (median): better in 0, worse in 6, equal in 0 of 6 prompts (p = 0.0312).
- Visible tokens (median): better in 1, worse in 5, equal in 0 of 6 prompts (p = 0.2188).
- Words per kept fact (median): better in 2, worse in 4, equal in 0 of 6 prompts (p = 0.6875).
- Filler phrases per answer: better in 2, worse in 0, equal in 4 of 6 prompts (p = 0.5000).
- First sentence answers: better in 0, worse in 2, equal in 4 of 6 prompts (p = 0.5000).
- Self-sufficiency (reader correct): better in 3, worse in 1, equal in 2 of 6 prompts (p = 0.6250).
- Self-sufficiency, questions not known without text: better in 3, worse in 1, equal in 2 of 6 prompts (p = 0.6250).
- Key facts kept (verified): better in 2, worse in 4, equal in 0 of 6 prompts (p = 0.6875).
- Wrong claims per answer (verified): better in 3, worse in 1, equal in 2 of 6 prompts (p = 0.6250).
- Rule violations / 100 words: better in 4, worse in 1, equal in 1 of 6 prompts (p = 0.3750).
- INFLESZ: better in 3, worse in 3, equal in 0 of 6 prompts (p = 1.0000).

### Conversations

| Turn | Viol./100 baseline | Viol./100 llano | Facts baseline | Facts llano | Words baseline | Words llano |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1.09 | 0.65 | 94% | 93% | 318 | 286 |
| 2 | 1.18 | 0.51 | 97% | 95% | 298 | 272 |
| 3 | 0.40 | 0.29 | 93% | 89% | 198 | 116 |

- Self-sufficiency: baseline 98%, llano 98%.
- Wrong claims per conversation: baseline 1.06, llano 0.61.
- **Blind preference, whole conversation (both orders):** llano 16, tie 1, other 1. Score 92% (ties count half; CI 83–100%). By prompt: 2 llano, 0 other, 0 even, p = 0.5000.

## haiku

### Single turn: baseline vs llano

| | baseline | llano |
|---|---:|---:|
| Words (median) | 112 | 136 |
| Output tokens incl. thinking (median) | 583 | 682 |
| Visible tokens (median) | 405 | 356 |
| Words per kept fact (median) | 32 | 37 |
| Filler phrases per answer | 0.06 | 0.03 |
| First sentence answers | 69% | 94% |
| Self-sufficiency (reader correct) | 79% | 81% |
| Self-sufficiency, questions not known without text | 79% | 81% |
| Key facts kept (verified) | 78% | 78% |
| Wrong claims per answer (verified) | 0.67 | 1.06 |
| Rule violations / 100 words | 1.00 | 0.61 |
| INFLESZ | 60.1 | 72.7 |
| Thinking share of output | 35% | 56% |
| Input tokens (median) | 3410 | 6180 |
| Answers with a diagram | 3% | 6% |
| Diagram share of the answer | 15% | 15% |
| Judge quotes not found in text | 1% | 0% |
| Diagram verdicts (ok/wrong/redundant) | 0/1/1 | 0/1/1 |

- **Blind preference vs baseline (both orders):** llano 12, tie 2, other 22. Score 36% (ties count half; CI 19–54%). By prompt: 3 llano, 9 other, 0 even, p = 0.1460.

Paired by prompt, llano vs baseline:
- Words (median): better in 5, worse in 7, equal in 0 of 12 prompts (p = 0.7744).
- Output tokens incl. thinking (median): better in 1, worse in 11, equal in 0 of 12 prompts (p = 0.0063).
- Visible tokens (median): better in 9, worse in 3, equal in 0 of 12 prompts (p = 0.1460).
- Words per kept fact (median): better in 6, worse in 6, equal in 0 of 12 prompts (p = 1.0000).
- Filler phrases per answer: better in 2, worse in 1, equal in 9 of 12 prompts (p = 1.0000).
- First sentence answers: better in 5, worse in 0, equal in 7 of 12 prompts (p = 0.0625).
- Self-sufficiency (reader correct): better in 3, worse in 1, equal in 8 of 12 prompts (p = 0.6250).
- Self-sufficiency, questions not known without text: better in 3, worse in 1, equal in 8 of 12 prompts (p = 0.6250).
- Key facts kept (verified): better in 2, worse in 7, equal in 3 of 12 prompts (p = 0.1797).
- Wrong claims per answer (verified): better in 1, worse in 9, equal in 2 of 12 prompts (p = 0.0215).
- Rule violations / 100 words: better in 6, worse in 4, equal in 2 of 12 prompts (p = 0.7539).
- INFLESZ: better in 12, worse in 0, equal in 0 of 12 prompts (p = 0.0005).

### Diagrams: llano vs llano without diagrams (structured prompts)

| | llano | llano_nodiag |
|---|---:|---:|
| Words (median) | 151 | 149 |
| Output tokens incl. thinking (median) | 720 | 702 |
| Visible tokens (median) | 393 | 425 |
| Words per kept fact (median) | 38 | 36 |
| Filler phrases per answer | 0.00 | 0.11 |
| First sentence answers | 89% | 100% |
| Self-sufficiency (reader correct) | 83% | 78% |
| Self-sufficiency, questions not known without text | 83% | 78% |
| Key facts kept (verified) | 78% | 79% |
| Wrong claims per answer (verified) | 1.22 | 1.06 |
| Rule violations / 100 words | 0.72 | 1.03 |
| INFLESZ | 75.5 | 73.7 |
| Thinking share of output | 57% | 44% |
| Input tokens (median) | 6180 | 5906 |
| Answers with a diagram | 11% | 0% |
| Diagram share of the answer | 15% | -- |
| Judge quotes not found in text | 0% | 0% |
| Diagram verdicts (ok/wrong/redundant) | 0/1/1 | 0/0/0 |

- **Blind preference vs no diagrams (both orders):** llano 6, tie 3, other 9. Score 42% (ties count half; CI 28–56%). By prompt: 1 llano, 3 other, 2 even, p = 0.6250.

Paired by prompt, llano vs llano_nodiag:
- Words (median): better in 4, worse in 2, equal in 0 of 6 prompts (p = 0.6875).
- Output tokens incl. thinking (median): better in 2, worse in 4, equal in 0 of 6 prompts (p = 0.6875).
- Visible tokens (median): better in 5, worse in 1, equal in 0 of 6 prompts (p = 0.2188).
- Words per kept fact (median): better in 3, worse in 3, equal in 0 of 6 prompts (p = 1.0000).
- Filler phrases per answer: better in 2, worse in 0, equal in 4 of 6 prompts (p = 0.5000).
- First sentence answers: better in 0, worse in 2, equal in 4 of 6 prompts (p = 0.5000).
- Self-sufficiency (reader correct): better in 3, worse in 0, equal in 3 of 6 prompts (p = 0.2500).
- Self-sufficiency, questions not known without text: better in 3, worse in 0, equal in 3 of 6 prompts (p = 0.2500).
- Key facts kept (verified): better in 1, worse in 5, equal in 0 of 6 prompts (p = 0.2188).
- Wrong claims per answer (verified): better in 1, worse in 3, equal in 2 of 6 prompts (p = 0.6250).
- Rule violations / 100 words: better in 4, worse in 0, equal in 2 of 6 prompts (p = 0.1250).
- INFLESZ: better in 4, worse in 2, equal in 0 of 6 prompts (p = 0.6875).

### Conversations

| Turn | Viol./100 baseline | Viol./100 llano | Facts baseline | Facts llano | Words baseline | Words llano |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1.75 | 1.19 | 81% | 79% | 135 | 145 |
| 2 | 0.95 | 0.49 | 92% | 85% | 148 | 152 |
| 3 | 0.40 | 0.59 | 88% | 85% | 90 | 110 |

- Self-sufficiency: baseline 100%, llano 94%.
- Wrong claims per conversation: baseline 2.33, llano 1.83.
- **Blind preference, whole conversation (both orders):** llano 4, tie 1, other 1. Score 75% (ties count half; CI 50–100%). By prompt: 1 llano, 0 other, 1 even, p = 1.0000.

## opus

### Single turn: baseline vs llano

| | baseline | llano |
|---|---:|---:|
| Words (median) | 299 | 280 |
| Output tokens incl. thinking (median) | 1212 | 1093 |
| Visible tokens (median) | 1114 | 950 |
| Words per kept fact (median) | 60 | 57 |
| Filler phrases per answer | 0.28 | 0.06 |
| First sentence answers | 75% | 86% |
| Self-sufficiency (reader correct) | 99% | 98% |
| Self-sufficiency, questions not known without text | 99% | 98% |
| Key facts kept (verified) | 98% | 99% |
| Wrong claims per answer (verified) | 0.06 | 0.06 |
| Rule violations / 100 words | 1.09 | 0.36 |
| INFLESZ | 73.7 | 78.0 |
| Thinking share of output | 6% | 16% |
| Input tokens (median) | 1580 | 5167 |
| Answers with a diagram | 8% | 19% |
| Diagram share of the answer | 10% | 8% |
| Judge quotes not found in text | 0% | 0% |
| Diagram verdicts (ok/wrong/redundant) | 1/0/0 | 5/0/2 |

- **Blind preference vs baseline (both orders):** llano 16, tie 11, other 9. Score 60% (ties count half; CI 43–75%). By prompt: 8 llano, 3 other, 1 even, p = 0.2266.

Paired by prompt, llano vs baseline:
- Words (median): better in 9, worse in 3, equal in 0 of 12 prompts (p = 0.1460).
- Output tokens incl. thinking (median): better in 7, worse in 5, equal in 0 of 12 prompts (p = 0.7744).
- Visible tokens (median): better in 9, worse in 3, equal in 0 of 12 prompts (p = 0.1460).
- Words per kept fact (median): better in 8, worse in 4, equal in 0 of 12 prompts (p = 0.3877).
- Filler phrases per answer: better in 5, worse in 0, equal in 7 of 12 prompts (p = 0.0625).
- First sentence answers: better in 4, worse in 2, equal in 6 of 12 prompts (p = 0.6875).
- Self-sufficiency (reader correct): better in 1, worse in 1, equal in 10 of 12 prompts (p = 1.0000).
- Self-sufficiency, questions not known without text: better in 1, worse in 1, equal in 10 of 12 prompts (p = 1.0000).
- Key facts kept (verified): better in 2, worse in 3, equal in 7 of 12 prompts (p = 1.0000).
- Wrong claims per answer (verified): better in 2, worse in 1, equal in 9 of 12 prompts (p = 1.0000).
- Rule violations / 100 words: better in 11, worse in 0, equal in 1 of 12 prompts (p = 0.0010).
- INFLESZ: better in 9, worse in 3, equal in 0 of 12 prompts (p = 0.1460).

### Diagrams: llano vs llano without diagrams (structured prompts)

| | llano | llano_nodiag |
|---|---:|---:|
| Words (median) | 301 | 288 |
| Output tokens incl. thinking (median) | 1158 | 1110 |
| Visible tokens (median) | 1076 | 1052 |
| Words per kept fact (median) | 62 | 62 |
| Filler phrases per answer | 0.00 | 0.00 |
| First sentence answers | 78% | 83% |
| Self-sufficiency (reader correct) | 96% | 98% |
| Self-sufficiency, questions not known without text | 96% | 98% |
| Key facts kept (verified) | 98% | 97% |
| Wrong claims per answer (verified) | 0.00 | 0.17 |
| Rule violations / 100 words | 0.36 | 0.59 |
| INFLESZ | 80.3 | 80.2 |
| Thinking share of output | 12% | 8% |
| Input tokens (median) | 5166 | 4812 |
| Answers with a diagram | 33% | 0% |
| Diagram share of the answer | 9% | -- |
| Judge quotes not found in text | 0% | 0% |
| Diagram verdicts (ok/wrong/redundant) | 4/0/2 | 0/0/0 |

- **Blind preference vs no diagrams (both orders):** llano 6, tie 7, other 5. Score 53% (ties count half; CI 39–69%). By prompt: 3 llano, 3 other, 0 even, p = 1.0000.

Paired by prompt, llano vs llano_nodiag:
- Words (median): better in 2, worse in 4, equal in 0 of 6 prompts (p = 0.6875).
- Output tokens incl. thinking (median): better in 1, worse in 5, equal in 0 of 6 prompts (p = 0.2188).
- Visible tokens (median): better in 1, worse in 5, equal in 0 of 6 prompts (p = 0.2188).
- Words per kept fact (median): better in 2, worse in 4, equal in 0 of 6 prompts (p = 0.6875).
- Filler phrases per answer: better in 0, worse in 0, equal in 6 of 6 prompts (p = 1.0000).
- First sentence answers: better in 0, worse in 1, equal in 5 of 6 prompts (p = 1.0000).
- Self-sufficiency (reader correct): better in 0, worse in 1, equal in 5 of 6 prompts (p = 1.0000).
- Self-sufficiency, questions not known without text: better in 0, worse in 1, equal in 5 of 6 prompts (p = 1.0000).
- Key facts kept (verified): better in 2, worse in 0, equal in 4 of 6 prompts (p = 0.5000).
- Wrong claims per answer (verified): better in 3, worse in 0, equal in 3 of 6 prompts (p = 0.2500).
- Rule violations / 100 words: better in 3, worse in 1, equal in 2 of 6 prompts (p = 0.6250).
- INFLESZ: better in 3, worse in 3, equal in 0 of 6 prompts (p = 1.0000).

### Conversations

| Turn | Viol./100 baseline | Viol./100 llano | Facts baseline | Facts llano | Words baseline | Words llano |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.68 | 0.42 | 100% | 100% | 344 | 320 |
| 2 | 1.22 | 0.36 | 100% | 100% | 365 | 304 |
| 3 | 0.21 | 0.23 | 98% | 94% | 202 | 147 |

- Self-sufficiency: baseline 94%, llano 100%.
- Wrong claims per conversation: baseline 0.50, llano 0.00.
- **Blind preference, whole conversation (both orders):** llano 6, tie 0, other 0. Score 100% (ties count half; CI 100–100%). By prompt: 2 llano, 0 other, 0 even, p = 0.5000.

## sonnet

### Single turn: baseline vs llano

| | baseline | llano |
|---|---:|---:|
| Words (median) | 292 | 232 |
| Output tokens incl. thinking (median) | 1163 | 1220 |
| Visible tokens (median) | 1064 | 748 |
| Words per kept fact (median) | 62 | 48 |
| Filler phrases per answer | 0.14 | 0.00 |
| First sentence answers | 75% | 89% |
| Self-sufficiency (reader correct) | 96% | 98% |
| Self-sufficiency, questions not known without text | 96% | 98% |
| Key facts kept (verified) | 95% | 98% |
| Wrong claims per answer (verified) | 0.06 | 0.03 |
| Rule violations / 100 words | 1.08 | 0.54 |
| INFLESZ | 72.8 | 77.7 |
| Thinking share of output | 10% | 38% |
| Input tokens (median) | 1585 | 5172 |
| Answers with a diagram | 0% | 14% |
| Diagram share of the answer | -- | 8% |
| Judge quotes not found in text | 0% | 0% |
| Diagram verdicts (ok/wrong/redundant) | 0/0/0 | 1/0/4 |

- **Blind preference vs baseline (both orders):** llano 18, tie 8, other 10. Score 61% (ties count half; CI 44–76%). By prompt: 7 llano, 3 other, 2 even, p = 0.3438.

Paired by prompt, llano vs baseline:
- Words (median): better in 12, worse in 0, equal in 0 of 12 prompts (p = 0.0005).
- Output tokens incl. thinking (median): better in 3, worse in 9, equal in 0 of 12 prompts (p = 0.1460).
- Visible tokens (median): better in 12, worse in 0, equal in 0 of 12 prompts (p = 0.0005).
- Words per kept fact (median): better in 11, worse in 1, equal in 0 of 12 prompts (p = 0.0063).
- Filler phrases per answer: better in 5, worse in 0, equal in 7 of 12 prompts (p = 0.0625).
- First sentence answers: better in 3, worse in 1, equal in 8 of 12 prompts (p = 0.6250).
- Self-sufficiency (reader correct): better in 2, worse in 1, equal in 9 of 12 prompts (p = 1.0000).
- Self-sufficiency, questions not known without text: better in 2, worse in 1, equal in 9 of 12 prompts (p = 1.0000).
- Key facts kept (verified): better in 2, worse in 1, equal in 9 of 12 prompts (p = 1.0000).
- Wrong claims per answer (verified): better in 1, worse in 1, equal in 10 of 12 prompts (p = 1.0000).
- Rule violations / 100 words: better in 11, worse in 1, equal in 0 of 12 prompts (p = 0.0063).
- INFLESZ: better in 11, worse in 1, equal in 0 of 12 prompts (p = 0.0063).

### Diagrams: llano vs llano without diagrams (structured prompts)

| | llano | llano_nodiag |
|---|---:|---:|
| Words (median) | 252 | 256 |
| Output tokens incl. thinking (median) | 1288 | 1142 |
| Visible tokens (median) | 900 | 898 |
| Words per kept fact (median) | 54 | 51 |
| Filler phrases per answer | 0.00 | 0.00 |
| First sentence answers | 89% | 89% |
| Self-sufficiency (reader correct) | 98% | 96% |
| Self-sufficiency, questions not known without text | 98% | 96% |
| Key facts kept (verified) | 98% | 98% |
| Wrong claims per answer (verified) | 0.00 | 0.11 |
| Rule violations / 100 words | 0.65 | 0.79 |
| INFLESZ | 79.8 | 80.5 |
| Thinking share of output | 36% | 34% |
| Input tokens (median) | 5171 | 4817 |
| Answers with a diagram | 28% | 0% |
| Diagram share of the answer | 8% | -- |
| Judge quotes not found in text | 0% | 0% |
| Diagram verdicts (ok/wrong/redundant) | 1/0/4 | 0/0/0 |

- **Blind preference vs no diagrams (both orders):** llano 5, tie 8, other 5. Score 50% (ties count half; CI 25–69%). By prompt: 3 llano, 2 other, 1 even, p = 1.0000.

Paired by prompt, llano vs llano_nodiag:
- Words (median): better in 5, worse in 1, equal in 0 of 6 prompts (p = 0.2188).
- Output tokens incl. thinking (median): better in 1, worse in 5, equal in 0 of 6 prompts (p = 0.2188).
- Visible tokens (median): better in 2, worse in 3, equal in 1 of 6 prompts (p = 1.0000).
- Words per kept fact (median): better in 3, worse in 3, equal in 0 of 6 prompts (p = 1.0000).
- Filler phrases per answer: better in 0, worse in 0, equal in 6 of 6 prompts (p = 1.0000).
- First sentence answers: better in 1, worse in 1, equal in 4 of 6 prompts (p = 1.0000).
- Self-sufficiency (reader correct): better in 1, worse in 1, equal in 4 of 6 prompts (p = 1.0000).
- Self-sufficiency, questions not known without text: better in 1, worse in 1, equal in 4 of 6 prompts (p = 1.0000).
- Key facts kept (verified): better in 2, worse in 2, equal in 2 of 6 prompts (p = 1.0000).
- Wrong claims per answer (verified): better in 2, worse in 0, equal in 4 of 6 prompts (p = 0.5000).
- Rule violations / 100 words: better in 4, worse in 1, equal in 1 of 6 prompts (p = 0.3750).
- INFLESZ: better in 1, worse in 5, equal in 0 of 6 prompts (p = 0.2188).

### Conversations

| Turn | Viol./100 baseline | Viol./100 llano | Facts baseline | Facts llano | Words baseline | Words llano |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.82 | 0.34 | 100% | 100% | 338 | 297 |
| 2 | 1.37 | 0.68 | 100% | 100% | 330 | 291 |
| 3 | 0.59 | 0.05 | 94% | 88% | 224 | 104 |

- Self-sufficiency: baseline 100%, llano 100%.
- Wrong claims per conversation: baseline 0.33, llano 0.00.
- **Blind preference, whole conversation (both orders):** llano 6, tie 0, other 0. Score 100% (ties count half; CI 100–100%). By prompt: 2 llano, 0 other, 0 even, p = 0.5000.
