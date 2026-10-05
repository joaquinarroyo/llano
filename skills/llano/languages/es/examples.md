# Spanish (es) — examples

Each pair shows typical LLM output and the llano version. The notes give the rule
numbers (C = core rule in SKILL.md, T = grammar trap in rules.md).

## 1. Explanation

**Before (69 words)**

> ¡Excelente pregunta! Básicamente, el caché de la aplicación funciona de manera que,
> en el caso de que un usuario realice una solicitud que ya fue procesada previamente,
> el sistema procede a devolver la respuesta almacenada, evitando así tener que
> consultar nuevamente la base de datos, lo cual permite mejorar significativamente
> el rendimiento de manera eficiente. Cabe destacar que esto es fundamental en el
> panorama actual. ¡Espero que te sirva!

**After (37 words)**

> La caché guarda la respuesta de cada solicitud. Si llega la misma solicitud otra
> vez, la aplicación devuelve la respuesta guardada. No consulta la base de datos.
> Por eso la respuesta tarda menos. No medí cuánto menos.

Notes: filler removed (C17). "en el caso de que" → "si", "procede a devolver" →
"devuelve" (dictionary). One long sentence → five short sentences (C6, C7).
"Significativamente" had no data behind it, so it became a concrete uncertainty (C18,
C20).

## 2. Error report

**Before**

> Se intentó ejecutar la migración, pero se produjo un error, por lo que se procedió a
> revisar los logs, observándose que posiblemente la columna podría no existir.

**After**

> La migración `0042_add_email` falló: la columna `users.email_verified` no existe.
> El log lo dice en la línea 18. Probablemente la migración `0041` no se aplicó.
> Ejecuta `make migrate-status` para verificarlo.

Notes: the result goes first (C14). "Se intentó / se produjo / se procedió" hide the
agent (T1). The gerund "observándose" is removed (T3). Two hedges become one (T7).
Exact names (C19).

## 3. Work summary

**Before**

> He llevado a cabo una serie de modificaciones en diversos archivos con el objetivo de
> resolver el problema de autenticación. Es importante mencionar que también realicé
> la actualización de los tests correspondientes para asegurar que todo funcione sin
> problemas.

**After**

> Corregí el error de autenticación. El token expiraba antes de tiempo porque
> `auth/session.ts:42` usaba segundos en vez de milisegundos.
>
> - `auth/session.ts`: cambié la unidad a milisegundos.
> - `auth/session.test.ts`: agregué un test para la expiración.
>
> Los 48 tests pasan.

Notes: "llevar a cabo una serie de modificaciones" → "corregí" (C3). The vague
"diversos archivos" becomes a list of files (C15, C19). "Sin problemas" becomes a
fact: 48 tests pass (C20).

## 4. Commit message (mode `all`)

**Before**

> Se realizaron mejoras en el manejo de errores del módulo de pagos de la aplicación
> de manera de garantizar un funcionamiento más robusto

**After**

> fix(pagos): reintentar el cobro si el proveedor responde 503
>
> El proveedor devuelve 503 durante sus ventanas de mantenimiento. Antes el cobro
> fallaba sin reintento. Ahora el cliente reintenta 3 veces con espera de 2 s.

Notes: Conventional Commits format kept (mode `all`). "Robusto" → the concrete
behavior (C20). The "de" chain "manejo de errores del módulo de pagos de la
aplicación" is gone (T4). If the repo writes commits in English, write them in English.

## 5. Level 2: diagram

Question: "¿Cómo fluye una solicitud de login?"

> El login pasa por cuatro componentes. El gateway valida el formato. El servicio de
> autenticación verifica la contraseña en Postgres. Redis guarda la sesión.
>
> ```
> Cliente ──POST /login──▶ Gateway ──▶ Auth service ──▶ Postgres
>                            │              │          (verifica hash)
>                            │              ▼
>                            │           Redis
>                            │       (guarda sesión)
>                            ◀── 200 + cookie ──┘
> ```
>
> Si Postgres no responde en 2 s, el servicio de autenticación devuelve 503.

Notes: there are 4 components that relate to each other, so level 2 applies. The text
before the diagram says what it shows, with one action per sentence (C7).
The labels are short and use the same terms as the text (C1).
