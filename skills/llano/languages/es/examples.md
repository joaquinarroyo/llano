# Spanish (es) examples

Each example shows a typical answer and the llano version. The llano version keeps
every value and cause from the input. It only removes filler and ambiguity.

<example>
Input: a deploy log with `ERROR connect ETIMEDOUT 10.0.3.17:5432` and
`Failed to initialize database pool after 30000 ms` and `Exiting with code 1`,
version v2.4.1.

Before:
> ¡Claro! Básicamente, parece que se produjo un problema de conexión con la base de
> datos, por lo que se recomienda proceder a revisar la configuración de red.

Llano:
> La API v2.4.1 no se conecta a Postgres en `10.0.3.17:5432`. El pool falla después de
> 30000 ms y el proceso termina con código 1.
>
> Es un timeout, no un error de credenciales: la conexión nunca recibe respuesta. Revisa
> primero que la base esté levantada y que el security group permita el puerto 5432
> desde la API.
</example>

<example>
Input: "¿Por qué no guardo contraseñas con SHA-256?"

Before:
> Es importante destacar que SHA-256 es un algoritmo de hash muy robusto, pero no es
> adecuado para contraseñas. En su lugar, se recomienda utilizar bcrypt o Argon2.

Llano:
> Porque SHA-256 es rápido, y eso ayuda al atacante: una GPU prueba miles de millones de
> contraseñas por segundo.
>
> Usa una función lenta y con sal: Argon2id, bcrypt o scrypt. La sal impide usar tablas
> precalculadas. El factor de costo se puede subir con el tiempo, cuando el hardware
> mejora.
</example>

<example>
Input: commits `feat(auth): add refresh token rotation`,
`fix(auth): invalidate old refresh token on reuse`, `test(auth): cover token reuse
detection`, `chore: bump jsonwebtoken 9.0.0 -> 9.0.2`.

Before:
> Se realizaron diversas mejoras en la autenticación y se actualizaron algunas
> dependencias.

Llano:
> - Rota los refresh tokens en cada uso.
> - Invalida el refresh token anterior si alguien lo reutiliza.
> - Agrega tests para la detección de reutilización.
> - Actualiza `jsonwebtoken` de 9.0.0 a 9.0.2.
</example>

<example>
Input: "Dibújame cómo fluye una solicitud de login." The system has a gateway, an
auth service, Postgres and Redis.

Llano:
> El login pasa por cuatro componentes. El gateway valida el formato. El servicio de
> autenticación verifica la contraseña en Postgres y guarda la sesión en Redis.
>
> ```
> Cliente ──POST /login──▶ Gateway ──▶ Auth ──▶ Postgres (verifica el hash)
>                                       │
>                                       └──▶ Redis (guarda la sesión)
> ```
>
> Si Postgres no responde en 2 s, el servicio de autenticación devuelve 503.

The user asked for a diagram. It shows only the relations that the text states, with
the same names.
</example>
