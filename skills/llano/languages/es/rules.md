# Spanish (es) — rules

## Variant and register

- **Neutral Spanish.** No regionalisms. No voseo ("revisa", not "revisá"). No "vosotros".
- **Address the user as "tú"**, in a direct and neutral way ("puedes", "revisa"). Do not
  use "usted".
- When a neutral word and a regional word compete, use the one with the widest reach:
  "computadora" over "ordenador", "archivo" over "fichero", "celular" over "móvil".

## Labels

- Danger: **Peligro:** (irreversible action, data loss, security risk)
- Caution: **Atención:** (can fail or break in a reversible way)

## Grammar traps

### 1. Impersonal / passive "se" that hides the agent

Why: "se" removes the subject. The reader does not know who did the action, and that
is often the most important fact in a technical report.

- ✗ "Se borró la tabla de usuarios."
- ✓ "La migración `0042` borró la tabla de usuarios."

"Se" is fine when the agent does not matter: "El archivo se guarda en `/tmp`."

### 2. Nominalization with light verbs

Why: "realizar / llevar a cabo / efectuar / hacer + noun" adds two or three words and
hides the real verb.

- ✗ "Realicé la instalación de las dependencias."
- ✓ "Instalé las dependencias."

### 3. Gerund misuse

Why: a gerund for a later action, or a chain of gerunds, blurs the order of events.

- ✗ "Ejecuté los tests, obteniendo 3 errores."
- ✓ "Ejecuté los tests. Fallaron 3."
- ✗ "Revisando el log y viendo que faltaba la variable, agregándola se resolvió."
- ✓ "El log mostraba que faltaba `API_URL`. Agregué la variable y el error desapareció."

A gerund for a simultaneous action is fine: "El servidor responde 500 mientras procesa
la cola" (or "procesando la cola").

### 4. "de" chains (noun clusters)

Why: Spanish builds noun clusters with "de". Long chains make the reader parse
backwards. Core rule 5 (three nouns max) applies to the "de" chain.

- ✗ "el archivo de configuración del servidor de producción del cliente"
- ✓ "el archivo de configuración de producción (`prod.yaml`)"

### 5. Subordinate clauses chained with "que"

Why: each "que" opens a clause. Two or three in a row overload memory.

- ✗ "Creo que el problema es que la función que valida el token no considera que puede
  expirar."
- ✓ "La función que valida el token no considera la expiración. Esa es la causa
  probable."

### 6. Anglicism calques

Why: they read as translation errors and some change the meaning. See the "Calques"
section of `dictionary.md`.

### 7. Hedging stacks

Why: Spanish LLM output stacks "podría", "quizás", "posiblemente", "en principio" in one
sentence. Core rule 18: one uncertainty, concrete, with its reason.

- ✗ "En principio, quizás podría deberse posiblemente a la caché."
- ✓ "La causa probable es la caché. No lo verifiqué."

## Adjustments to core rules

- **Sentence length:** keep 20 / 25 words. Spanish uses more function words than
  English, so treat the limit as a target. If a sentence needs 27 words to keep a
  condition intact, the exception rule applies.
- **Questions:** use opening marks (¿ ¡). Avoid rhetorical questions in answers.

## Numbers and dates

- Decimals with a point in technical context (`0.5 s`, `1.25 GB`), because code and
  tools use a point.
- Thousands without separator in technical values (`10000 ms`). In prose with large
  quantities, use a space (`1 500 000 usuarios`).
- Absolute dates: `5 de octubre de 2026` or ISO `2026-10-05`.
