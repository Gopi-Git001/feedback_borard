# ADR-002: Password hashing (Argon2id) and JWT approach
Status: Proposed
Date: 2026-10-27   Deciders: architect-bot (proposes), Orchestrator (approves)

## Context
Brief: built-in email/password, passwords hashed, JWT auth, multi-tenant by organization (one org per user for the MVP), tenant isolation enforced on every query. No external auth services. Security-bot and backend-bot need exact parameters. The tenant must come from the token, never from a request field.

## Options considered
Password hashing (choose one):
1. **argon2-cffi 25.1.0 (Argon2id).** Winner of the Password Hashing Competition, standardised in RFC 9106; library ships ready-made RFC 9106 profiles and `check_needs_rehash`. Cons: last release 2025-06-03 (older than 12 months, but repository active 2026-10-01); native extension (wheels exist for cp314).
2. **bcrypt 5.0.0.** Mature, simple. Cons: 72-byte input limit, not memory-hard, also older than 12 months (2025-09-25).
JWT:
1. **PyJWT 2.15.1**, HS256 symmetric. Small, maintained (release 2026-09-28), enough for a single backend that both signs and verifies.
2. RS256/EdDSA asymmetric. Not needed: there is one service, no third-party verifier. Reconsider if a second service must verify tokens.
Browser token storage:
1. Access token in JS memory + refresh token in an HttpOnly cookie (chosen).
2. Both in `localStorage`: simplest but any XSS can steal long-lived credentials. Rejected.

## Decision
**Password hashing: Argon2id via argon2-cffi ~=25.1.0.**
- Use `argon2.PasswordHasher.from_parameters(argon2.profiles.RFC_9106_LOW_MEMORY)`, i.e. Argon2id, time_cost=3, memory_cost=65536 KiB (64 MiB), parallelism=4, 16-byte random salt, 32-byte hash (the profile values; verified by running argon2-cffi 25.1.0 on 2026-10-27: `Parameters(type=ID, version=19, salt_len=16, hash_len=32, time_cost=3, memory_cost=65536, parallelism=4)`, one hash took about 46 ms on the architect box; docs: "Choosing Parameters"). Backend-bot must confirm in its first test that one hash takes roughly 50-300 ms in the docker container and report if not; do not lower parameters without a new ADR.
- Store the encoded string (it embeds algorithm, parameters and salt) in `users.password_hash`. On successful login call `check_needs_rehash()` and re-hash if parameters changed.
- Password policy: min 10, max 128 characters, no composition rules; reject values over 128 (prevents hash-DoS). Never log or return the password or hash.
- Login must run `verify` against a dummy hash when the email is unknown, so timing does not reveal which emails exist. Error is always `INVALID_CREDENTIALS` (401).

**JWT: PyJWT ~=2.15.1, algorithm HS256 only** (the decode call must pass `algorithms=["HS256"]`; never read the algorithm from the token header).
- Secret: `JWT_SECRET` environment variable, at least 32 random bytes (e.g. `openssl rand -base64 48`). Never in code, docs, git or logs. Docker compose reads it from a git-ignored `.env`; `.env.example` holds a placeholder only. App refuses to start if it is missing or shorter than 32 characters.
- **Access token:** lifetime **15 minutes**. Sent as `Authorization: Bearer <token>`. Kept in JS memory only (never `localStorage`/`sessionStorage`).
- **Refresh token:** lifetime **7 days**, a JWT with `typ=refresh`, set as cookie `refresh_token`: `HttpOnly; Secure` (the `Secure` flag may be switched off only for plain-http local dev, via a config flag); `SameSite=Strict`; `Path=/api/v1/auth`. The SPA never reads it. `POST /auth/refresh` reads the cookie, returns a new access token and rotates the refresh cookie. `POST /auth/logout` clears it. The SPA calls refresh on page load and on a 401.
- **Claims:** `sub` (user id, UUID string), `org` (organization id UUID string, **absent** until the user creates or joins an organization), `typ` (`access` or `refresh`), `iat`, `exp`, `jti` (random UUID), `iss` = `feedback-board`, `aud` = `feedback-board-api`. Validate `exp`, `iss`, `aud`, `typ` on every request.
- **Role is not in the token.** Role (`admin|member`) is read from `memberships` on each request, so a role change or removal takes effect immediately. The membership row must still exist for the `org` claim to be honoured; otherwise respond 401.
- **Organization context:** when a user creates an org or accepts an invite the response issues a **new** access token containing `org` and rotates the refresh cookie, because the claim changed. Endpoints that need an org return 403 `ORG_REQUIRED` when `org` is absent. Tenant id is taken only from the verified token; no request body, query or path field may set it.
- Failure behaviour: missing/invalid/expired token -> 401 `UNAUTHENTICATED` with `WWW-Authenticate: Bearer`.
- CORS: only the configured frontend origin; credentials allowed for the refresh cookie. In docker compose the frontend proxies `/api` to the backend so it is same-origin.
- Rate limiting: `login`, `signup`, `refresh` and invite `preview` return 429 `RATE_LIMITED` (per IP; implementation choice left to backend-bot, no new service required).

## Consequences
- Easier: no external auth service; Argon2id resists GPU cracking; XSS cannot steal the refresh token; role changes apply instantly; token has no tenant-spoofing path.
- Harder / limits: refresh tokens are **stateless**, so logout only clears the cookie and a stolen refresh token stays valid until it expires (max 7 days). Acceptable for the MVP (free product, no PII beyond email and name); follow-up: store refresh-token `jti` hashes in a table for revocation and reuse detection. Each request needs one membership lookup.
- Memory cost: 64 MiB per concurrent login hash; with the default uvicorn worker count, size container memory accordingly (hash in a thread pool, `run_in_threadpool`, so the event loop is not blocked).
- Symmetric key: anyone who holds `JWT_SECRET` can mint tokens. Keep it out of logs and CI output (GitHub Actions secret for CI; a test-only value is fine for CI because no real data exists).
- Fallback: bcrypt 5.0.0 (cost 12) if argon2-cffi wheels fail to build on a target platform.

## Sources (verified 2026-10-27)
- https://pypi.org/pypi/argon2-cffi/json (25.1.0, 2025-06-03); https://argon2-cffi.readthedocs.io/en/stable/parameters.html (RFC 9106 profiles); https://github.com/hynek/argon2-cffi (last commit 2026-10-01)
- https://pypi.org/pypi/bcrypt/json (5.0.0, 2025-09-25) as the rejected option
- https://pypi.org/pypi/pyjwt/json (2.15.1, 2026-09-28); https://github.com/jpadilla/pyjwt/releases/tag/2.15.1
- RFC 9106 (Argon2): https://www.rfc-editor.org/rfc/rfc9106
