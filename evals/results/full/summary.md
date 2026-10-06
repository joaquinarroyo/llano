# Results: full

Claude Code 2.1.292. Models: haiku, sonnet, opus. Runs: 3. Judge: sonnet.

## All models

### Single turn

| | Baseline | Llano |
|---|---:|---:|
| Words (median) | 208 | 178 |
| Visible tokens (median) | 794 | 629 |
| Output tokens incl. thinking (median) | 973 | 940 |
| Thinking share of output | 14% | 37% |
| Violations / 100 words | 1.22 | 0.30 |
| INFLESZ | 70.1 | 77.2 |
| Key facts kept | 89% | 84% |
| Wrong claims (total) | 74 | 106 |
| Input tokens (median) | 1679 | 10054 |

- **Blind preference:** llano 126, tie 0, baseline 90. Win rate 58% (clustered CI 51%–66%). By prompt: 15 llano, 9 baseline, 0 even, p = 0.3075.
- **Violations:** lower with llano in 24 of 24 prompts, higher in 0 (p = 0.0000).
- **Fidelity:** llano − baseline = -5% [-9%, -2%].
- **Words:** -19% [-27%, -13%].
- **Output tokens incl. thinking:** +7% [+1%, +19%].

### Conversations

| Turn | Viol./100 baseline | Viol./100 llano | Facts baseline | Facts llano |
|---:|---:|---:|---:|---:|
| 1 | 0.95 | 0.30 | 89% | 94% |
| 2 | 1.12 | 0.31 | 92% | 92% |
| 3 | 0.80 | 0.21 | 91% | 86% |

- **Blind preference (whole conversation):** llano 26, tie 0, baseline 10. By conversation: 4 llano, 0 baseline, p = 0.1250.

## haiku

### Single turn

| | Baseline | Llano |
|---|---:|---:|
| Words (median) | 124 | 108 |
| Visible tokens (median) | 412 | 376 |
| Output tokens incl. thinking (median) | 589 | 698 |
| Thinking share of output | 38% | 54% |
| Violations / 100 words | 1.12 | 0.52 |
| INFLESZ | 63.3 | 74.1 |
| Key facts kept | 77% | 69% |
| Wrong claims (total) | 56 | 92 |
| Input tokens (median) | 3405 | 9911 |

- **Blind preference:** llano 32, tie 0, baseline 40. Win rate 44% (clustered CI 32%–57%). By prompt: 10 llano, 14 baseline, 0 even, p = 0.5413.
- **Violations:** lower with llano in 18 of 24 prompts, higher in 3 (p = 0.0015).
- **Fidelity:** llano − baseline = -8% [-13%, -3%].
- **Words:** -5% [-14%, +7%].
- **Output tokens incl. thinking:** +16% [+10%, +46%].

### Conversations

| Turn | Viol./100 baseline | Viol./100 llano | Facts baseline | Facts llano |
|---:|---:|---:|---:|---:|
| 1 | 1.26 | 0.64 | 69% | 81% |
| 2 | 1.04 | 0.68 | 77% | 81% |
| 3 | 0.54 | 0.42 | 80% | 69% |

- **Blind preference (whole conversation):** llano 8, tie 0, baseline 4. By conversation: 3 llano, 1 baseline, p = 0.6250.

## opus

### Single turn

| | Baseline | Llano |
|---|---:|---:|
| Words (median) | 262 | 255 |
| Visible tokens (median) | 1045 | 988 |
| Output tokens incl. thinking (median) | 1104 | 1109 |
| Thinking share of output | 6% | 20% |
| Violations / 100 words | 1.24 | 0.10 |
| INFLESZ | 74.0 | 79.5 |
| Key facts kept | 94% | 93% |
| Wrong claims (total) | 10 | 5 |
| Input tokens (median) | 1576 | 10059 |

- **Blind preference:** llano 44, tie 0, baseline 28. Win rate 61% (clustered CI 49%–74%). By prompt: 15 llano, 9 baseline, 0 even, p = 0.3075.
- **Violations:** lower with llano in 24 of 24 prompts, higher in 0 (p = 0.0000).
- **Fidelity:** llano − baseline = -1% [-4%, +1%].
- **Words:** -14% [-26%, -0%].
- **Output tokens incl. thinking:** +4% [-10%, +18%].

### Conversations

| Turn | Viol./100 baseline | Viol./100 llano | Facts baseline | Facts llano |
|---:|---:|---:|---:|---:|
| 1 | 0.73 | 0.06 | 100% | 100% |
| 2 | 0.98 | 0.11 | 100% | 100% |
| 3 | 0.81 | 0.07 | 95% | 98% |

- **Blind preference (whole conversation):** llano 8, tie 0, baseline 4. By conversation: 3 llano, 1 baseline, p = 0.6250.

## sonnet

### Single turn

| | Baseline | Llano |
|---|---:|---:|
| Words (median) | 262 | 190 |
| Visible tokens (median) | 1002 | 694 |
| Output tokens incl. thinking (median) | 1151 | 1178 |
| Thinking share of output | 10% | 42% |
| Violations / 100 words | 1.30 | 0.28 |
| INFLESZ | 73.2 | 77.9 |
| Key facts kept | 97% | 89% |
| Wrong claims (total) | 8 | 9 |
| Input tokens (median) | 1580 | 10062 |

- **Blind preference:** llano 50, tie 0, baseline 22. Win rate 69% (clustered CI 58%–79%). By prompt: 19 llano, 5 baseline, 0 even, p = 0.0066.
- **Violations:** lower with llano in 21 of 24 prompts, higher in 2 (p = 0.0001).
- **Fidelity:** llano − baseline = -7% [-14%, -2%].
- **Words:** -26% [-40%, -22%].
- **Output tokens incl. thinking:** +7% [-1%, +23%].

### Conversations

| Turn | Viol./100 baseline | Viol./100 llano | Facts baseline | Facts llano |
|---:|---:|---:|---:|---:|
| 1 | 0.84 | 0.19 | 98% | 100% |
| 2 | 1.35 | 0.15 | 98% | 96% |
| 3 | 1.03 | 0.15 | 98% | 91% |

- **Blind preference (whole conversation):** llano 10, tie 0, baseline 2. By conversation: 4 llano, 0 baseline, p = 0.1250.
