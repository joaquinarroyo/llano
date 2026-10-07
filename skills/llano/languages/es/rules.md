# Spanish (es)

Write neutral Spanish. Address the user as "tú" ("revisa", "puedes"), with no voseo and
no "usted". Prefer the word with the widest reach: "computadora", "archivo", "celular".

## Labels

- **Peligro:** irreversible action, data loss or security risk.
- **Atención:** something that can fail or break in a reversible way.

## How the core rules apply in Spanish

- **Length.** Aim for 20 words in steps and 25 in explanations. Spanish needs more
  words than English, so 30 is the ceiling. Vary the length.
- **Agent.** Name who acts when it matters: "La migración `0042` borró la tabla", not
  "Se borró la tabla". Use "se" when the agent does not matter: "El archivo se guarda
  en `/tmp`".
- **Real verbs.** "Instalé las dependencias", not "Realicé la instalación de las
  dependencias". Use one verb, not a chain: "puede configurarlo", not "va a poder ser
  configurado".
- **Asides.** Move an explanation between commas to its own sentence.
- **Gerunds.** Use a gerund only for an action at the same time. For a later action,
  write two sentences: "Ejecuté los tests. Fallaron 3."
- **Clauses.** Use one "que" clause per sentence and no more than three nouns joined
  by "de".
- **Subjunctive.** Use it where grammar requires it ("para que funcione", "si quieres
  que...").
- **Positive phrasing.** "Mantén el token en el servidor", not "No dejes de no
  exponer el token".
- **Numbers.** Use digits, units and a point for decimals in technical values
  (`0.5 s`). Use absolute dates.

## Words

Use the word on the right:

| Instead of | Use |
|---|---|
| utilizar, emplear | usar |
| realizar, efectuar, llevar a cabo | the real verb |
| proceder a + infinitive | the infinitive |
| comprobar, chequear | verificar |
| eliminar, suprimir (data, files) | borrar |
| remover (from a list or code) | quitar |
| añadir, adicionar | agregar |
| requerir, precisar | necesitar |
| poseer, disponer de | tener |
| proporcionar, brindar | dar |
| en el caso de que | si |
| con el fin de, a fin de | para |
| debido a que, dado que, ya que | porque |
| no obstante, sin embargo | pero |
| por lo tanto, por consiguiente | por eso |
| asimismo, adicionalmente | también |
| previo a | antes de |
| posteriormente | después |
| a nivel de | en |
| librería (code) | biblioteca |

Keep technical terms as the ecosystem uses them: commit, branch, deploy, endpoint,
token, hook, cache, log, test, script.

## Start and end

Start with the answer, not with "¡Claro!", "Excelente pregunta" or "Cabe destacar
que". End with the last piece of content, not with "Espero que te sirva" or a summary
of what you already said.
