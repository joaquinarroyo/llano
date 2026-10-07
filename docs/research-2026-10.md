# Research: improving llano (October 2026)

Five parallel research passes after the first full eval (commit `08229cb`). That eval
found that llano lowers rule violations in every model, wins blind preference on
Sonnet (69%), and loses fidelity on Sonnet (−7% key facts) and Haiku (−8%, wrong
claims +64%). The thinking share also rises from 14% to 37%. This file records the
findings and the sources.

## 1. Why llano loses facts

- **Brevity can raise hallucination.** "Answer concisely" makes many models worse at
  resisting misinformation, because a correct caveat needs room
  ([Phare](https://arxiv.org/html/2505.11365v1)).
- **Simplification fails by omission.** About 71% of simplification edits are
  deletions, and "loss of informative content" affects about 20% of sentences
  ([2505.16392](https://arxiv.org/html/2505.16392)). Plain-language summaries are less
  factual ([FactPICO](https://arxiv.org/html/2402.11456)).
- **Format constraints cost reasoning, more for small models.** Writing freely first and
  converting the format after recovers most of the loss
  ([Let Me Speak Freely?](https://arxiv.org/abs/2408.02442); the effect size is disputed
  by [dottxt](https://blog.dottxt.ai/say-what-you-mean.html)). Small models give wrong
  answers under length limits ([Constrained-CoT](https://arxiv.org/pdf/2407.19825)). The
  effect of brevity depends on scale
  ([Brevity Constraints](https://arxiv.org/html/2604.00025v1)).
- **Denser is better only up to a point.** The useful move is "same facts, fewer words",
  not "fewer words" ([Chain of Density](https://arxiv.org/abs/2309.04269)).
- **A verification pass reduces hallucination**
  ([Chain-of-Verification](https://arxiv.org/abs/2309.11495)).
- **Other style skills do not measure fidelity.** SimpleEnglish reports linter violations
  only. Caveman states that its token runs "do not prove semantic or technical
  equivalence" ([HONEST-NUMBERS](https://github.com/JuliusBrussee/caveman/blob/main/docs/HONEST-NUMBERS.md)).

## 2. Why small models do worse

- **Compliance falls roughly exponentially with rule count.** Reasoning models stay
  stable up to about 150 instructions. Claude 3.5 Haiku collapses early and levels off at
  7–15%. Earlier instructions are followed better (primacy)
  ([IFScale](https://arxiv.org/abs/2507.11538); [Curse of Instructions](https://arxiv.org/html/2509.21051v1)).
  The llano core, the traps, about 115 substitutions and the banned list add up to more
  than 100 instructions.
- **Reasoning and instruction following trade off.** Thinking can lower compliance or add
  content ([MathIF](https://arxiv.org/abs/2505.14810);
  [When Thinking Fails](https://arxiv.org/abs/2505.11423)). Past some budget, extra
  reasoning flips correct answers ([2604.10739](https://arxiv.org/html/2604.10739v1)).
- **Diagram quality follows model scale.** ASCII and spatial layout are weak points
  ([MermaidSeqBench](https://arxiv.org/html/2511.14967v3);
  [2410.01733](https://arxiv.org/html/2410.01733v2)). A diagram that only repeats the text
  adds load (redundancy principle), and a wrong diagram is worse than none.
- **Anthropic says to test skills on every model.** "What works for Opus might need more
  detail for Haiku"
  ([skill best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)).

## 3. Delivery and prompt design

- **Output styles fit llano better than a skill plus a hook.** They set "role, tone, and
  response format for every response", live in the system prompt, are cached and survive
  compaction. Two cautions: set `keep-coding-instructions: true`, or Claude Code's coding
  instructions are dropped, and remember that only one style can be active
  ([output styles](https://code.claude.com/docs/en/output-styles)).
- **After compaction, a skill is truncated.** Claude Code re-attaches only the first
  5,000 tokens of each invoked skill. Llano is about 8.5k tokens, so it loses its tail
  ([skills](https://code.claude.com/docs/en/skills)).
- **Prompting guidance.** Use the smallest high-signal prompt. Tell the model what to do,
  not what not to do. Match the prompt's style to the output. Use 3–5 varied examples in
  `<example>` tags. Explain why. Avoid capitals and "MUST"
  ([Claude prompting](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices);
  [context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).
- **Banned lists prime the banned words.** Positive wording works better
  ([16x eval](https://eval.16x.engineer/blog/the-pink-elephant-negative-instructions-llms-effectiveness-analysis);
  practitioner evidence).
- **Other agents:** Codex reads AGENTS.md (32 KiB cap). Cursor has Rules and Skills.

## 4. Spanish plain language

- **ISO 24495-1 / UNE-ISO 24495-1:2024** has four principles: relevant, findable,
  understandable, usable. It asks for "reasonably short" sentences of varied length, with
  **no word limit**. It also asks for the same word for the same meaning, and terms and
  acronyms defined on first use
  ([UNE](https://www.une.org/encuentra-tu-norma/busca-tu-norma/norma?c=N0072523)).
- **Spanish plain-language guides agree on:** active voice, a named agent, few
  subordinate clauses, no gerunds, few nominalizations and positive phrasing.
- **Lectura Fácil (UNE 153101 EX)** adds: no verb periphrasis, no comma-bounded
  explanations inside a sentence, digits for numbers
  ([summary](https://olgacarreras.blogspot.com/2019/02/lectura-facil-pautas-y-recomendaciones.html)).
- **STE rules that transfer badly to Spanish:**
  - Hard word caps push models toward fragments.
  - A blanket rule against the impersonal "se" is too strict.
  - The subjunctive is grammatically required in some places.
- **Metrics:**
  - Do not use Fernández-Huerta: it has a formula error.
  - INFLESZ is the reference, but it was validated on health texts and technical terms
    lower its score.
  - Feature-based measures work better: sentence length distribution, verbs and commas
    per sentence, gerund and nominalization rates, word frequency
    ([TSAR 2022](https://aclanthology.org/2022.tsar-1.18.pdf)).
- **Spanish LLM-isms** (press and blogs): "cabe destacar", "es importante señalar",
  "cuando se trata de", "en el ámbito de", "en un mundo donde", "indudablemente",
  "en última instancia", "asimismo", groups of three, summary closers.

## 5. Evaluation method

- **Judge bias:**
  - Judges prefer their own model's text
    ([self-preference](https://arxiv.org/abs/2404.13076)).
  - Style bias dominates position and verbosity bias
    ([SOS-Bench](https://arxiv.org/abs/2409.15268);
    [2604.23178](https://arxiv.org/html/2604.23178v2)).
  - A "which is clearer" verdict is a style judgment, so it is the weakest signal for a
    style skill.
- **Liking is not understanding.** Readers rated LLM summaries as good as human ones but
  understood the human ones better ([2505.10409](https://arxiv.org/abs/2505.10409)).
  Comprehension multiple-choice questions are the standard outcome measure
  ([2505.01980](https://arxiv.org/abs/2505.01980)).
- **Judge both orders and count a split verdict as a tie**
  ([position bias](https://arxiv.org/abs/2406.07791)). A judge that never declares a tie
  is normal ([MT-Bench](https://arxiv.org/abs/2306.05685)).
- **Use a panel of judges from different families**
  ([PoLL](https://arxiv.org/abs/2404.18796)). Use a majority of 3 judge samples rather
  than one call ([Rating Roulette](https://arxiv.org/abs/2510.27106)).
- **Fidelity:**
  - Human-written key facts with automatic assignment track humans well
    ([AutoNuggetizer](https://arxiv.org/abs/2504.15068)).
  - Count wrong claims per atomic claim ([FActScore](https://arxiv.org/abs/2305.14251)).
  - Calibrate the judge against 50–100 human labels
    ([Alternative Annotator Test](https://arxiv.org/abs/2501.10970)).
- **Statistics:**
  - Cluster by prompt ([Miller](https://arxiv.org/abs/2411.00640)).
  - Mixed-effects models ([2509.24086](https://arxiv.org/abs/2509.24086)).
  - With 24 prompts, a sign test detects only win rates of about 70% or more.

## Recommendations

### Skill (v2)

1. **Content first, style second.** Decide the facts, values and causes first. Then write
   them plainly. Do not audit rules while thinking.
2. **Protect facts.**
   - Copy every number, version, count, path, flag and name from the input exactly.
   - Keep one sentence of cause: "X porque Y".
   - If a rule would drop a fact, break the rule.
3. **Small core.**
   - About 1,200–1,500 tokens: purpose, about 10 positive rules in priority order with
     fidelity first, and 3–4 examples in `<example>` tags.
   - Write the core itself in llano style, with no "MUST".
4. **Language pack inline, short.**
   - The 20 most frequent substitutions, written as "usa X".
   - The full dictionary and the banned list move to an on-demand reference and to the
     linter.
5. **Spanish rules, adjusted.**
   - Length is a target of 20/25 words, with a ceiling of about 30. Vary length and do
     not fragment.
   - Flag the impersonal "se" only when the agent matters.
   - Allow the subjunctive.
   - Add rules against verb periphrasis and comma-bounded explanations.
   - Define terms on first use.
   - Add the Spanish LLM-isms to the banned list.
6. **Gated diagrams.**
   - Off for small models.
   - Otherwise only when the relations are explicit in the text, and never draw a
     relation the text does not state.
   - Prefer a list or a table.
7. **Tiers by model:** lite for Haiku (6–8 rules plus examples, no diagrams), standard
   for Sonnet, full for Opus.
8. **Delivery in Claude Code: an output style** with `keep-coding-instructions: true`,
   installed by the doctor. Keep the skill for other agents and for manual use.

### Eval (v2)

1. **Primary metric: a reader-model comprehension test.** Turn the key facts into
   multiple-choice questions, which a reader model answers using only the response.
2. **Judge panel:**
   - Include at least one judge from outside the Claude family.
   - Judge both A/B orders and count a split verdict as a tie.
3. **Fidelity:**
   - Ask one question per fact (present / partial / absent), with a verbatim quote.
   - Take a majority of 3 samples.
   - Count wrong claims per atomic claim.
4. **Human calibration:** about 60 items labeled by Spanish-speaking developers.
5. **Linter:** report it as a manipulation check only. Compute INFLESZ on prose without
   technical terms, and add structural metrics.
6. **Ablation:** remove the dictionary, the traps, the examples and the diagrams one at a
   time, to find which one costs facts.
7. **More prompts:** add prompts and independent key facts. Fit a mixed-effects model and
   simulate power before running.
