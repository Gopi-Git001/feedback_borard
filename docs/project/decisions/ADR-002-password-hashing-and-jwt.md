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
- Use `argon2.PasswordHasher.from_parameters(argon2.profiles.RFC_9106_LOW_MEMORY)`, i.e. Argon2id, time_cost=3, memory_cost=65536 KiB (64 MiB), parallelism=4, 16-byte random salt, 32-byte hash (the profile values; verified by running argon2-cffi 25.1.0 on 2026-10-27: `Parameters(type=ID, version=19, salt_len=16, hash_len=32, time_cost=3, memory_cost=65536, parallelism=4)`, five hashes took 40-65 ms each on the architect box; docs: "Choosing Parameters"). Backend-bot must confirm in its first test that one hash takes roughly 50-300 ms in the docker container and report if not; do not lower parameters without a new ADR.
- Store the encoded string (it embeds algorithm, parameters and salt) in `users.password_hash`. On successful login call `check_needs_rehash()` and re-hash if parameters changed.
- Password policy: min 8, max 128 characters (min 8 follows story F1-1). No composition rules, so longer passphrases are possible and encouraged in the UI; reject values over 128 (prevents hash-DoS). Never log or return the password or hash.
- Login must run `verify` against a dummy hash when the email is unknown, so timing does not reveal which emails exist. Error is always `INVALID_CREDENTIALS` (401).

**JWT: PyJWT ~=2.15.1, algorithm HS256 only** (the decode call must pass `algorithms=["HS256"]`; never read the algorithm from the token header).
- Secret: `JWT_SECRET` environment variable. **One rule, checked at startup:** the value must (a) match `^[A-Za-z0-9_-]{43,}$` (base64url alphabet, 43 or more characters, i.e. at least 32 random bytes = 256 bits when generated as below), (b) contain at least 16 distinct characters, and (c) not contain, case-insensitively, any known weak or placeholder fragment: `secret`, `changeme`, `change-me`, `change_me`, `password`, `replace`, `placeholder`, `example`, `default`, `jwt`, `test`, `dev` (and the value must not be empty). The app **refuses to start** (exit non-zero, error message without printing the value) if any check fails. Generate with `python -c "import secrets; print(secrets.token_urlsafe(48))"` (64 characters, 48 random bytes). `.env.example` holds the non-random placeholder `REPLACE_WITH_OUTPUT_OF_secrets_token_urlsafe_48`, which fails (a-c) on purpose. CI generates a fresh random value at the start of each job (a test-only value must pass the same check). Never in code, docs, git or logs. Docker compose reads it from a git-ignored `.env`.
- **Rotation (follow-up, not MVP):** tokens carry no `kid`, so rotating the secret logs everyone out (acceptable at MVP scale). If zero-downtime rotation is needed, add a `kid` header and a list of accepted keys in a new ADR.
- **Access token:** lifetime **15 minutes**. Sent as `Authorization: Bearer <token>`. Kept in JS memory only (never `localStorage`/`sessionStorage`).
- **Refresh token:** lifetime **7 days**, a JWT with `typ=refresh`, set as cookie `refresh_token`: `HttpOnly; Secure` (the `Secure` flag may be switched off only for plain-http local dev, via a config flag); `SameSite=Strict`; `Path=/api/v1/auth`. The SPA never reads it. `POST /auth/refresh` reads the cookie, returns a new access token and rotates the refresh cookie. `POST /auth/logout` clears it. The SPA calls refresh on page load and on a 401. **These two endpoints go beyond story F1-1** (F1-1 lists logout and session expiry as out of scope); they are approved per Orchestrator message 2026-10-27, relayed from the human, and are marked as extras (`x-extra: true`) in the contract. The refresh token is not rotated with reuse detection (see Consequences).
- **Claims:** `sub` (user id, UUID string), `org` (organization id UUID string, **absent** until the user creates or joins an organization), `typ` (`access` or `refresh`), `iat`, `exp`, `jti` (random UUID), `iss` = `feedback-board`, `aud` = `feedback-board-api`. Verification is exactly: `jwt.decode(token, JWT_SECRET, algorithms=["HS256"], issuer="feedback-board", audience="feedback-board-api", options={"require": ["exp", "iat", "sub", "iss", "aud", "typ", "jti"]})`, then check `typ` (`access` for API calls, `refresh` for `/auth/refresh`). `org` is not in the required list because it is absent until the user has an organization; endpoints that need it check it (403 `ORG_REQUIRED`). `jti` must be present but is **not used yet** (there is no revocation table in the MVP); it exists so revocation or reuse detection can be added without changing the token format. The contract (`api-contract.yaml`, Conventions) states the same list.
- **Role is not in the token.** Role (`admin|member`) is read from `memberships` on each request, so a role change or removal takes effect immediately. The membership row must still exist for the `org` claim to be honoured; otherwise respond 401.
- **Organization context:** when a user creates an org or accepts an invite the response issues a **new** access token containing `org` and rotates the refresh cookie, because the claim changed. Endpoints that need an org return 403 `ORG_REQUIRED` when `org` is absent (**ASSUMED**: no story or brief text defines this behaviour; the contract marks it ASSUMED). Tenant id is taken only from the verified token; no request body, query or path field may set it.
- Failure behaviour: missing/invalid/expired token -> 401 `UNAUTHENTICATED` with `WWW-Authenticate: Bearer` (**ASSUMED**: the brief and stories name only 403 and 404; 401 is the standard reading).
- CORS: only the configured frontend origin; credentials allowed for the refresh cookie. In docker compose the frontend proxies `/api` to the backend so it is same-origin.
- Rate limiting: `signup`, `login`, `refresh`, `logout` and invite `preview` return 429 `RATE_LIMITED` (approved per Orchestrator message 2026-10-27, relayed from the human; story F1-1 lists rate limiting of login attempts as out of scope, so this goes beyond F1-1). Per IP; implementation left to backend-bot, no new service required. Behind the docker proxy the client IP is taken from `X-Forwarded-For` only when the request comes from the configured trusted proxy address; otherwise the socket peer address is used. Because F1-1 requires 409 `EMAIL_TAKEN` on signup, signup is an email-enumeration oracle that only this rate limit mitigates.
- Invite tokens appear in URL paths; their handling (log redaction, no-store, referrer policy) is decided in ADR-003.

## Consequences
- Easier: no external auth service; Argon2id resists GPU cracking; XSS cannot steal the refresh token; role changes apply instantly; token has no tenant-spoofing path.
- Harder / limits: refresh tokens are **stateless**, so logout only clears the cookie and a stolen refresh token stays valid until it expires (max 7 days). Acceptable for the MVP (free product, no PII beyond email and name); follow-up: store refresh-token `jti` hashes in a table for revocation and reuse detection. Each request needs one membership lookup.
- Memory cost: 64 MiB per concurrent login hash; with the default uvicorn worker count, size container memory accordingly (hash in a thread pool, `run_in_threadpool`, so the event loop is not blocked).
- Symmetric key: anyone who holds `JWT_SECRET` can mint tokens. Keep it out of logs and CI output (CI generates a fresh random value per job, which must pass the same startup check; no real data exists in CI).
- Fallback: bcrypt 5.0.0 (cost 12) if argon2-cffi wheels fail to build on a target platform.

## Related
- ADR-003 (invite token handling), ADR-001 (pinned stack).

## Sources (verified 2026-10-27)
- https://pypi.org/pypi/argon2-cffi/json (25.1.0, 2025-06-03); https://argon2-cffi.readthedocs.io/en/stable/parameters.html (RFC 9106 profiles); https://github.com/hynek/argon2-cffi (last commit 2026-10-01)
- https://pypi.org/pypi/bcrypt/json (5.0.0, 2025-09-25) as the rejected option
- https://pypi.org/pypi/pyjwt/json (2.15.1, 2026-09-28); https://github.com/jpadilla/pyjwt/releases/tag/2.15.1
- RFC 9106 (Argon2): https://www.rfc-editor.org/rfc/rfc9106
