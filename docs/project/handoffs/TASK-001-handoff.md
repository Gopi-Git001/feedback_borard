# Handoff: TASK-001 Verify and pin stack; data model; OpenAPI contract
Bot: architect-bot   Attempt: 2b (security-bot FAIL on PR #2 addressed)   PR: https://github.com/Gopi-Git001/feedback_borard/pull/2   Branch: feature/TASK-001-stack-and-contracts

## Summary
Verified live (2026-10-27) the current stable version, last release date and official source of every component of the pre-approved stack and pinned them in `stack.md`, with ADR-001 (pinned set) and ADR-002 (Argon2id + PyJWT/HS256, DB-backed refresh tokens, rate limits), ADR-003 (invite token in the URL fragment and POST body) and ADR-004 (security baseline, new in attempt 2b). Designed the PostgreSQL data model (9 tables after attempt 2b: 7 business tables plus `refresh_tokens` and `rate_limit_counters`; shared-table tenancy with `organization_id`, composite foreign keys, `UNIQUE (user_id, post_id)` on votes) and an OpenAPI 3.0.3 contract (15 paths, 18 operations) covering features F1-F9, with 404 for cross-organization access. No application, docker or CI code was written.

## Changes in attempt 2 (response to the qa-bot review, https://github.com/Gopi-Git001/feedback_borard/pull/2#issuecomment-6457769981)
Stories on `main` are the PR #3 version (`b495550`, merged 2026-10-27 19:54 CT); the contract and data model were checked against that version.
1. `POST /auth/refresh` and `POST /auth/logout`: marked `x-extra: true`, dropped the F1 tag (`x-features: []`), and the scope note says they go beyond story F1-1. Both are approved per Orchestrator message 2026-10-27, relayed from the human, so they are no longer ASSUMED (contract, ADR-002).
2. The 401 rule and the 403 `ORG_REQUIRED` behaviour are marked ASSUMED in the contract and ADR-002.
3. Rate limiting (429 on signup, login, refresh, logout, invite preview) is labelled approved per Orchestrator message 2026-10-27, relayed from the human in the contract and ADR-002, with a note that it goes beyond F1-1's out-of-scope list. Note: qa-bot asked to drop 429 from `/auth/logout`; I kept it because the Orchestrator said to keep the 429s. Dropping it later is a one-line contract change. **Update (attempt 2b): dropped, per later steering; 429 stays on signup, login, refresh, invite preview/accept.**
4. This handoff: real PR link, delivery criterion met, open question 1 corrected.
5. ADR-002: one JWT secret rule (base64url, at least 43 characters = 32 bytes, at least 16 distinct characters, weak/placeholder fragments rejected at startup, startup refuses to run) replacing the contradictory text.
6. New ADR-003 (**superseded by attempt 2b below**): invite token stayed in the path (smallest change, matches F3-1), with log redaction (app, proxy, error tracking), `Cache-Control: no-store`, `Referrer-Policy: no-referrer`, malformed token = 404; data-model.md and the contract point to it.
7. data-model.md: stale text fixed (stories exist, ER diagram `description`, unique index for `lower(email)`, vote toggle algorithm); grep of architecture/ and decisions/ found no other stale add/remove-vote, pagination or hashed-invite text.
8. `jwt.decode` required claims are the same in the contract and ADR-002: `exp, iat, sub, iss, aud, typ, jti` (`org` is checked per endpoint because it is absent before an organization exists; `jti` was present but unused; now used for refresh tokens, see attempt 2b).
9. `stack.md` addendum: uv, Python/Node/nginx image tags, ruff, mypy, TanStack Query and Vitest (final), no OpenAPI client generator pinned (reason in the file); Node 24 wording corrected to Maintenance LTS.
Also from the review: same-day-release risk note, 404-before-403 order stated in the contract conventions, 404 (not 400) for malformed invite tokens, 422/`BUSINESS_RULE_VIOLATION` removed from the contract (used by no operation), duplicated "no composition rules" removed, trusted-proxy and secret-rotation notes added to ADR-002. TypeScript 6.0.3 and `display_name` at signup are confirmed by the Orchestrator (relayed from the human); ba-bot will update the stories for `display_name`.

## Attempt 2b: response to the security-bot review (FAIL, https://github.com/Gopi-Git001/feedback_borard/pull/2#issuecomment-6457850545)
Delivered as new commits `TASK-001: ...` on top of `4ed04d4` (docs only, `docs/project/`), patches in `/workspace/TASK-001/attempt2b/`. The six Attempt 2 patches are not repeated. Orchestrator decisions relayed on 2026-10-27 were followed; the later steering from ba-bot TASK-039 / PR #4 (four items) is included.

### REVERSAL to flag to the human
**Attempt 2 said "refresh tokens are stateless, no revocation in the MVP". That decision is reversed.** Refresh tokens are now stored server-side (hash only) in a new `refresh_tokens` table with rotation, reuse detection, an absolute 7-day cap from login, and logout that revokes the whole family. Every place that carried the old note was rewritten or removed (ADR-002 Consequences, handoff open question 6 and follow-ups, data-model.md); the only remaining mentions of "stateless" are the sentences that say it is superseded.

### What changed per finding
| # | Finding | Change | Where |
|---|---|---|---|
| 1 (blocker) | Refresh token unbounded and not revocable | `refresh_tokens` table (`user_id`, `family_id`, `family_started_at`, `token_hash` = SHA-256 of the JWT `jti`, `expires_at`, `revoked_at`, `revoked_reason`, `replaced_by`). Rotation on every refresh; reuse of a rotated or revoked token revokes the whole family (401); every token expires at login time + 7 days so rotation never extends the session; logout revokes the family; 10-active-families cap per user (ASSUMED). `organization_id` is **deliberately not stored** (a session belongs to a user who exists before any organization; the `org` claim is re-read from `memberships` on each refresh; stated in data-model.md section 1). Two-tab race: 10 s leeway (`REFRESH_REUSE_LEEWAY_SECONDS`) answers 401 without revoking, plus a cross-tab lock in the SPA. | ADR-002, data-model.md 3.8, contract `/auth/refresh`, `/auth/logout` |
| 2 (blocker) | Invite token in URL paths and logs | Link is `<origin>/join#<token>` (fragment, never sent to a server). New `POST /invites/preview` and `POST /invites/accept` take `{token}` in the body; the path operations `/invites/{token}` and `/invites/{token}/accept` are gone. `Cache-Control: no-store` on invite responses, `Referrer-Policy: no-referrer`, bodies never logged, 404 for malformed or unknown tokens. ADR-003 rewritten. The admin still sees the same link every time. | ADR-003, contract, data-model.md |
| 3 (should-fix) | Invite token in plaintext; no expiry/regenerate/remove-member | Plaintext removed: the token is **derived** (`HMAC-SHA256(INVITE_TOKEN_KEY, version + organization id)`) and only `sha256(token)` is stored in `invites.token_hash`, plus `token_version`. This keeps F3-1 (same link every time) and a database dump reveals nothing usable. **Expiry, regenerate/revoke and remove-member are NOT added** (product scope, Orchestrator decision); recorded as follow-ups and as a residual risk in ADR-003. This adds one secret, `INVITE_TOKEN_KEY` (my design choice, not in the Orchestrator's list; the fallback if rejected is in ADR-003). | ADR-003, data-model.md 3.4 |
| 4 (should-fix) | JWT secret "32 random bytes" vs "32 characters" | One rule: unpadded base64url that **decodes to at least 32 bytes**, at least 16 distinct characters, weak-fragment denylist; same rule for `INVITE_TOKEN_KEY`; app refuses to start. ADR-002 text, the `.env.example` placeholder explanation and the plan wording are now consistent (see "Plan impact" below for `<32 chars` in TASK-004). | ADR-002 |
| 5 (should-fix) | Rate limiting under-specified | Concrete ASSUMED numbers per endpoint group, shared counter store in PostgreSQL (`rate_limit_counters`), one trusted nginx proxy that overwrites `X-Forwarded-For` plus `TRUSTED_PROXY_IPS`, per-account login limit, limits on invite accept and organization create, Argon2 concurrency cap (`ARGON2_MAX_CONCURRENCY`, default 4 = 256 MiB per worker). **429 removed from `/auth/logout`** (steering). **Env vars** (`RATE_LIMIT_ENABLED` and one `RATE_LIMIT_*` per group, `<max>/<window_seconds>`) so Playwright sets `RATE_LIMIT_ENABLED=false`; startup refuses that value with `APP_ENV=production` (steering). | ADR-002, data-model.md 3.9, contract |
| 6 (should-fix) | No security headers/CSP/no-store | New ADR-004: CSP for SPA and API, `nosniff`, `Referrer-Policy`, `Cache-Control: no-store` on auth/org/invite responses, HSTS only over HTTPS, `Permissions-Policy`, COOP; user content rendered as text only (no `dangerouslySetInnerHTML`). The review's point that XSS can still call `/auth/refresh` is recorded as a **residual risk**, not removed. | ADR-004, contract conventions |
| 7 | CSRF, `Secure` toggle, CORS | Origin check plus required header `X-Requested-With: feedback-board` on `/auth/refresh` and `/auth/logout` (403 `FORBIDDEN`); `Secure` flag can be off only when `APP_ENV` is not `production`, startup refuses otherwise; CORS pinned to one explicit origin. | ADR-004, ADR-002, contract |
| 8 | JWT decode details | `require` list now includes `typ`; `typ=access` required on every API endpoint (a refresh token is never a bearer token); `leeway=30`; `jti` used for refresh tokens; rotation without `kid` stated as logging everyone out. | ADR-002, contract |
| 9 | Composite FKs | **Adopted** (it was simple): `posts`, `comments`, `votes`, `invites` reference `memberships (organization_id, user_id)` with `ON DELETE RESTRICT`. `organizations.created_by` cannot (membership is created after the organization). | data-model.md |
| 10 | Claim vs membership; 404-before-403; DB role; RLS | The `org` claim is a hint: `SELECT role FROM memberships WHERE user_id = :sub AND organization_id = :org`, no row = 401. 404-before-403 stated for every post sub-resource. Non-owner DB role required (migrations run as owner). RLS scheduled as a follow-up, not built. | ADR-002, ADR-004, data-model.md 1 and 8 |
| 11 | Password policy | **Not met, deliberately:** minimum stays 8 (story F1-1). Gap versus NIST SP 800-63B-4 (15) and OWASP ASVS (12), no breached-password check, no change/reset/verification flow: recorded as follow-ups, with the rule that a future reset flow must revoke all families. | ADR-002, ADR-004 |
| 12 | Signup 409 oracle | **Not removed:** F1-1 requires "Email already registered". Mitigated by the per-IP signup limit; documented. | ADR-002, ADR-004, contract |
| 13 | Redaction | `Authorization`, `Cookie`, `Set-Cookie` headers and the bodies of `/auth/*` and `/invites/*` are never logged; 400 `details` never echo submitted values. | ADR-004, contract |
Also (steering item 1): `display_name` is 1-80 and the contract and data-model.md both say "trim leading/trailing whitespace first, then validate the length; the trimmed value is stored".

### Stories impact (for ba-bot; I edited no story)
- **F3-1 invite link:** the full URL is now `<origin>/join#<token>` (token in the fragment, not a path); "Copy" copies that URL. AC1-AC2 "same URL with the same token" stays true, including after logout and login (the token is derived, not session-dependent). Token minimum 32 characters unchanged (43). Add that the token is never sent to the server in a path or query. **Logout now revokes the refresh-token family** (per steering): it does not change the link, but the AC2 "log out and in again (a new session)" step now starts a new family; mention it. Data touched: Invite stores a token hash, not the token.
- **F2-1 create or join:** joining uses `POST /invites/preview` (shows the organization name) and `POST /invites/accept` with the token in a body; "Join with invite link" opens `/join#<token>`; the SPA removes the fragment from the address bar after reading it; a logged-out visitor signs up or logs in first and the SPA keeps the token in `sessionStorage` (`pending_invite`) until accept (resolves the ASSUMED logged-out flow). AC4: an edited or truncated token, or a link without a fragment, shows "Invite link is invalid" (404; no API call when the fragment is empty). AC6: accept without a login is 401; preview stays public.
- **E2E-1 owner journey:** step 3 uses the `/join#<token>` URL form; add a check that no request URL contains the token; the suite runs with `RATE_LIMIT_ENABLED=false`.
- **F1-1 signup/login:** `display_name` required, 1-80 after trimming; the "Out of scope: logout/session expiry rules, rate limiting" line now conflicts with the approved extras (refresh, logout, rate limiting; 429 on signup and login per IP, per account on login); the 409 "Email already registered" stays.
- **F1-2 logout/refresh (TASK-039 / PR #4, not on `main` when I looked):** logout now **revokes the whole refresh-token family** server-side; refresh **rotates** the token, **reuse of a rotated or revoked token revokes the family and gives 401**, and the session ends **7 days after login** whatever the activity; refresh and logout need `X-Requested-With: feedback-board` and a matching `Origin` (403 otherwise); logout is idempotent and has **no 429**; an access token issued before logout works for up to 15 minutes more.
- No change for F4-1, F5-1, F6-1, F7-1, F8-1, F9-1.

### Plan impact (for the Orchestrator, I did not edit plan.md)
TASK-003 (`.env.example` gains `INVITE_TOKEN_KEY`, `APP_ENV`, `FRONTEND_ORIGIN`, `TRUSTED_PROXY_IPS`, `RATE_LIMIT_*`, `ARGON2_MAX_CONCURRENCY`, two DB roles); TASK-004 (the "JWT_SECRET missing or <32 chars" check becomes the decode-to-32-bytes rule); TASK-006 (nine tables, composite FKs, `refresh_tokens`, `rate_limit_counters`, hashed invites); TASK-007 (nginx headers and log format); TASK-010 (rotation, reuse detection, CSRF header, limits); TASK-017 and TASK-026 (POST body invites, `/join#<token>`).

### Follow-ups and risks recorded (not built)
Invite expiry, regenerate/revoke link (`token_version` bump) and remove-member (product scope); RLS; scheduled cleanup of `refresh_tokens` and `rate_limit_counters`; breached-password check and longer minimum; password reset/change (must revoke families); `kid` JWT key rotation; access-token denylist (a 15-minute window after logout is accepted); XSS can still call `/auth/refresh` (residual); signup enumeration oracle (rate limit only); a per-account login limit lets an attacker lock a victim's login for 15 minutes.

### Not met / honest limits
- Password minimum stays 8 (F1-1), below NIST and ASVS.
- Signup keeps the 409 oracle (F1-1).
- Invite link cannot be expired, regenerated or revoked, and members cannot be removed (scope).
- Nothing was executed: no DDL against PostgreSQL (the `CHECK expires_at <= family_started_at + interval '7 days'` and the composite FKs are untested until TASK-006), no refresh-race test, no header or CSP test; the CSP and header syntax were not re-verified against MDN in this attempt (ADR-004 says so).
- I added things beyond the Orchestrator's list, to be accepted or removed: `INVITE_TOKEN_KEY` and the derived token (finding 3), a 429 on `POST /organizations` (finding 5), and the 10-families cap.

## Acceptance criteria
| Criterion | Status (met / not met) | Test that proves it |
|---|---|---|
| Given stack.md, every row has version, last-release date and an official source link, and no pre-release versions | **met** (with 3 documented freshness exceptions, see Open questions) | `stack.md` tables: every row has pinned version, exact version, date, URL. Versions fetched from PyPI JSON, npm registry, python.org, postgresql.org, nodejs.org, GitHub releases on 2026-10-27. Pre-release check: no version string contains rc/beta/dev/canary/pre; dist-tags checked (npm dist-tags checked 2026-10-27: typescript `latest` 7.0.2 vs `rc`/`beta`/`next` pre-releases; vite `latest` 8.3.5 vs `beta`; react `latest` 19.3.1 vs `canary`/`rc`; only stable versions are pinned). |
| Given the data model, votes are unique per user+post and every tenant table has organization_id | **met** | `data-model.md` section 3.6: `UNIQUE (user_id, post_id)`; section 1 lists the tenant tables (memberships, invites, posts, votes, comments, each `organization_id uuid NOT NULL`, indexed in section 5); `organizations` is the tenant root; `users` is global by design (explained). Composite FKs make cross-org votes/comments impossible. Not executed against a live database (doc task); backend-bot's migration `0001_initial` must test it. |
| Given the OpenAPI file, it validates with an OpenAPI linter and covers every feature F1-F9 | **met** | Lint results below. Coverage script: all 18 operations carry `x-features` (the two approved extras have `[]` and `x-extra: true`); union over the other 16 = F1..F9 (F1 auth, F2 orgs/invites/me, F3 invite create/preview/accept, F4 create/get post, F5 POST vote toggle, F6 comments list/create, F7 list+filter+sort, F8 status PATCH, F9 DELETE post). |
| Given a cross-org request, the contract specifies a 404 response | **met** | `api-contract.yaml`: every `/posts/{post_id}*` operation and `POST /invites/preview` and `POST /invites/accept` list `404` -> `components/responses/NotFound` (`POST_NOT_FOUND`/`INVITE_NOT_FOUND`, "exists in another organization is indistinguishable"). Stated in `info.description` and in the operation descriptions. No request field or parameter carries an organization id (`grep organization_id api-contract.yaml` = 0 matches). |
| Deliver in one PR on `feature/TASK-001-stack-and-contracts`, title `TASK-001: ...` | **met** | PR #2 https://github.com/Gopi-Git001/feedback_borard/pull/2 (opened by another agent from the architect-bot's local commits, because architect-bot has no push access), branch `feature/TASK-001-stack-and-contracts`, title starts `TASK-001: `, commits `TASK-001: ...`. Attempt 2 commits are delivered as patches in `/workspace/TASK-001/attempt2/` and attempt 2b commits in `/workspace/TASK-001/attempt2b/` on the shared box until someone with push access pushes them. |

## Files changed
All new, all under `docs/project/`:
- `docs/project/stack.md`
- `docs/project/decisions/ADR-001-pinned-stack.md`
- `docs/project/decisions/ADR-002-password-hashing-and-jwt.md`
- `docs/project/decisions/ADR-003-invite-token-handling.md` (new in attempt 2, rewritten in attempt 2b)
- `docs/project/decisions/ADR-004-security-baseline.md` (new in attempt 2b)
- `docs/project/architecture/data-model.md`
- `docs/project/architecture/api-contract.yaml`
- `docs/project/handoffs/TASK-001-handoff.md`
- Removed placeholder `.gitkeep` from `architecture/` and `decisions/` (now non-empty). `handoffs/.gitkeep` is left in place.
No files outside `docs/project/` changed. `board.md` was not touched (Orchestrator only).

## How to test locally
```bash
python3 -m venv .venv && .venv/bin/pip install openapi-spec-validator
.venv/bin/openapi-spec-validator docs/project/architecture/api-contract.yaml
npx --yes @redocly/cli@2.71.2 lint docs/project/architecture/api-contract.yaml
# re-verify any pinned version, e.g.
curl -s https://pypi.org/pypi/fastapi/json | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['info']['version'])"
curl -s https://registry.npmjs.org/vite/latest | python3 -c "import json,sys;print(json.load(sys.stdin)['version'])"
```
Mermaid ER diagram renders in GitHub's markdown preview (`data-model.md` section 4).

## Test results
- `openapi-spec-validator` 0.9.0: `api-contract.yaml: OK`.
- `@redocly/cli` 2.71.2 `lint` (recommended ruleset), re-run in attempt 2b on the final file (15 paths, 18 operations, F1-F9 still covered, every operation has `x-roles`): **valid, 0 errors, 1 warning** (`info-license`: no license object, deliberate for an internal project). First run had 2 errors (`nullable` without `type`) and 10 warnings; all fixed.
- Contract coverage script: 15 paths, 18 operations, features F1-F9 all covered. Every operation has `x-roles`. All operations that return a body have an example response; the 2 operations without examples (`POST /auth/logout`, `DELETE /posts/{post_id}`) have no request/response body (204).
- Argon2 parameters executed: argon2-cffi 25.1.0 with `RFC_9106_LOW_MEMORY` gave `type=ID, version=19, salt_len=16, hash_len=32, time_cost=3, memory_cost=65536, parallelism=4`; hash+verify round trip OK, hash alone 40-65 ms (5 runs), hash+verify ~130 ms on the architect box.
- Not run: SQL DDL was not executed against PostgreSQL (no DDL file is delivered, only the model); no application tests (no code in scope).

## Decisions made (and why)
- Python 3.14 (not 3.15), Node 24 LTS (not 26), TypeScript 6.0.3 (not 7.0.2, because typescript-eslint 8.72.1 supports only `<6.1.0`), SQLAlchemy 2.1.6 with 2.0.55 fallback, `react-router` 8.5.1 single package. Reasons in ADR-001 and stack.md notes.
- Argon2id (RFC 9106 low-memory profile) over bcrypt; PyJWT HS256 with secret from env; access 15 min in JS memory; refresh 7 days in HttpOnly SameSite=Strict cookie; role read from DB per request, not stored in the token (ADR-002).
- Superseded in attempt 2b: refresh tokens are DB-backed families (ADR-002), the invite token is in the URL fragment and POST body and stored as a hash (ADR-003). The text below is the original reasoning where not contradicted by the attempt 2b section.
- Added `POST /auth/refresh` and `POST /auth/logout` (now approved per Orchestrator message 2026-10-27, relayed from the human; extras beyond F1-1): refresh was requested by the Orchestrator's message; logout is needed because an HttpOnly cookie can only be cleared by the server. Both are small additions beyond the TASK-001.md endpoint list.
- `POST /posts/{id}/vote` toggles and returns `VoteState` (200), so the UI can update counts without a refetch. Status change is `PATCH /posts/{id}/status`.
- Creating an org or accepting an invite returns a new access token with the `org` claim (the claim changes).
- Denormalised `vote_count` and `comment_count` on posts for efficient sort-by-votes; maintained transactionally.
- Composite foreign keys `(organization_id, post_id)` as database-level tenant isolation; PostgreSQL RLS recorded as a follow-up.
- Reconciled with the TASK-002 stories (merged to main during this task, PR #1): one persistent invite token per organization (F3-1), shown as the same link every time (attempt 2b: derived and stored as a hash, not in clear), `POST /organizations/current/invite` is get-or-create; vote is a single toggle endpoint `POST /posts/{id}/vote` (F5-1); no pagination (F7-1, F6-1); password min 8 (F1-1); limits: org name 60, title 120, description required 2000, comment 1000; messages "Email already registered", "Invalid email or password", "You already belong to an organization", "Invite link is invalid". Where my first draft differed, the stories won.

## Open questions
1. Architect-bot cannot push (no git credentials; the GitHub connector has no commit tool). PR #2 was opened by another agent from my local commits; attempt 2 is provided as patches (`/workspace/TASK-001/attempt2/`) and needs someone with push access to apply them to the PR branch.
2. Freshness exceptions (older than 12 months, still the latest stable and not deprecated): argon2-cffi 25.1.0 (2025-06-03), email-validator 2.3.0 (2025-08-26), httpx 0.28.1 (2024-12-06, only 1.0 dev pre-releases exist after it). bcrypt 5.0.0 (2025-09-25) is also older than 12 months. Orchestrator to accept or overrule.
3. TypeScript 6.0.3 instead of the newer stable 7.0.2 (lint compatibility): confirmed by the Orchestrator (relayed from the human) on 2026-10-27; revisit when typescript-eslint supports TS 7.
4. `react-router` v8 usage in SPA/library mode should be confirmed by frontend-bot against reactrouter.com (the docs page fetched only described framework mode).
5. Stories F1-F9 are marked READY "conditional on brief approval"; if the brief changes (limits, password minimum 8, no pagination), the contract and data model change with it.
6. ~~Refresh tokens are stateless~~ **Reversed in attempt 2b:** refresh tokens are DB-backed with rotation, reuse detection, an absolute 7-day cap and logout revocation (ADR-002). Orchestrator to tell the human.
7. SQLAlchemy 2.1 went GA on 2026-09-24; pytest 9.2.0, react-router 8.5.1, uv 0.13.6 and ruff 0.17.3 were released on 2026-10-27, the day of the check: newest releases carry regression risk (fallbacks in stack.md note 11).
8. The 401 rule and 403 `ORG_REQUIRED` remain ASSUMED; Orchestrator to confirm or add them to the stories.
9. Invite token handling was rewritten in attempt 2b (fragment plus POST body, derived hashed token, ADR-003); security-bot to re-review. Orchestrator to accept the extra secret `INVITE_TOKEN_KEY` or ask for plain random tokens.
10. `display_name` is required at signup in the contract (approved); the stories do not mention it yet (ba-bot to update).
11. No OpenAPI client generator is pinned: openapi-typescript 7.13.0 has peer `typescript ^5.x`, which conflicts with TypeScript 6.0.3 (stack.md addendum).
12. Stories (TASK-002) landed on main while I worked; I rebased onto main (`0567ef4`), reconciled contract and data model with them (see Decisions made), and in attempt 2 checked against the PR #3 version (`b495550`).

## Suggested follow-up tasks
- Persistent audit log table for admin actions (status change, delete).
- PostgreSQL Row-Level Security as a second tenant-isolation layer.
- Invite expiry, regeneration/revocation and remove-member (out of MVP, product scope; `token_version` allows regeneration without a schema change), pagination for board and comments.
- Backend scaffold task: Alembic `0001_initial` from `data-model.md` plus cross-org isolation tests; frontend scaffold task generating a typed client from `api-contract.yaml`.
- Upgrade review for TypeScript 7 / Python 3.15 / Node 26 LTS.
- Optional hardening: `kid`-based JWT key rotation, breached-password check and longer minimum length, password reset/change (revoking families), scheduled cleanup jobs, logging/redaction and header tests for ADR-003 and ADR-004.
