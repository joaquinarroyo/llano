# English (en) examples

Each example shows a typical answer and the llano version. The llano version keeps
every value and cause from the input. It only removes filler and ambiguity.

<example>
Input: a deploy log from the API service, version v2.4.1, with
`ERROR connect ETIMEDOUT 10.0.3.17:5432` and
`Failed to initialize database pool after 30000 ms` and `Exiting with code 1`. The
database is Postgres. A security group controls access to it.

Before:
> Sure! Basically, it looks like there was an issue connecting to the database, so I
> would recommend that you go ahead and take a look at your network configuration.

Llano:
> API v2.4.1 cannot connect to Postgres at `10.0.3.17:5432`. The pool fails after
> 30000 ms and the process exits with code 1.
>
> This is a timeout, not a credentials error: the connection never gets a reply. First,
> verify that the database is up. Run this from the API host:
>
> ```bash
> pg_isready -h 10.0.3.17 -p 5432
> ```
>
> If it does not reply, verify that the security group allows port 5432 from the API.
</example>

<example>
Input: "Why shouldn't I store passwords with SHA-256?"

Before:
> It's important to note that SHA-256 is a very robust hashing algorithm, but it isn't
> well suited for passwords. Instead, it is recommended to utilize bcrypt or Argon2.

Llano:
> Because SHA-256 is fast, and that helps the attacker: one GPU tests billions of
> passwords per second.
>
> Use a slow, salted function: Argon2id, bcrypt or scrypt. The salt stops attacks with
> precomputed tables. You can raise the cost factor over time, as hardware gets faster.
</example>

<example>
Input: commits `feat(auth): add refresh token rotation`,
`fix(auth): invalidate old refresh token on reuse`, `test(auth): cover token reuse
detection`, `chore: bump jsonwebtoken 9.0.0 -> 9.0.2`.

Before:
> Various improvements were made to authentication and some dependencies were updated.

Llano:
> - Rotates refresh tokens on each use.
> - Invalidates the old refresh token if someone uses it again.
> - Adds tests for reuse detection.
> - Updates `jsonwebtoken` from 9.0.0 to 9.0.2.
</example>

<example>
Input: "Draw how a login request flows." The client sends `POST /login` to
the gateway. The gateway validates the request format and sends it to the auth
service. The auth service verifies the password hash in Postgres and stores the
session in Redis. If Postgres does not reply in 2 s, it returns 503.

Llano:
> The gateway validates the format and sends the request to the auth service.
>
> ```
> Client ──POST /login──▶ Gateway ──▶ Auth ──▶ Postgres (verifies the hash)
>                                      │
>                                      └──▶ Redis (stores the session)
> ```
>
> If Postgres does not reply in 2 s, the auth service returns 503.

The user asked for a diagram. It draws only the relations in the input, with the same
names. The text adds only what the diagram does not show: the format check and the
2 s timeout.
</example>
