# Handoff: TASK-001 Verify and pin stack; data model; OpenAPI contract
Bot: architect-bot   Attempt: 2   PR: https://github.com/Gopi-Git001/feedback_borard/pull/2   Branch: feature/TASK-001-stack-and-contracts

## Summary
Verified live (2026-10-27) the current stable version, last release date and official source of every component of the pre-approved stack and pinned them in `stack.md`, with ADR-001 (pinned set) and ADR-002 (Argon2id + PyJWT/HS256, token lifetimes and storage) and ADR-003 (invite token handling). Designed the PostgreSQL data model (7 tables, shared-table tenancy with `organization_id`, composite foreign keys, `UNIQUE (user_id, post_id)` on votes) and an OpenAPI 3.0.3 contract (15 paths, 18 operations) covering features F1-F9, with 404 for cross-organization access. No application, docker or CI code was written.

## Changes in attempt 2 (response to the qa-bot review, https://github.com/Gopi-Git001/feedback_borard/pull/2#issuecomment-6457769981)
Stories on `main` are the PR #3 version (`b495550`, merged 2026-10-27 19:54 CT); the contract and data model were checked against that version.
1. `POST /auth/refresh` and `POST /auth/logout`: marked `x-extra: true`, dropped the F1 tag (`x-features: []`), and the scope note says they go beyond story F1-1. Both are approved per Orchestrator message 2026-10-27, relayed from the human, so they are no longer ASSUMED (contract, ADR-002).
2. The 401 rule and the 403 `ORG_REQUIRED` behaviour are marked ASSUMED in the contract and ADR-002.
3. Rate limiting (429 on signup, login, refresh, logout, invite preview) is labelled approved per Orchestrator message 2026-10-27, relayed from the human in the contract and ADR-002, with a note that it goes beyond F1-1's out-of-scope list. Note: qa-bot asked to drop 429 from `/auth/logout`; I kept it because the Orchestrator said to keep the 429s. Dropping it later is a one-line contract change.
4. This handoff: real PR link, delivery criterion met, open question 1 corrected.
5. ADR-002: one JWT secret rule (base64url, at least 43 characters = 32 bytes, at least 16 distinct characters, weak/placeholder fragments rejected at startup, startup refuses to run) replacing the contradictory text.
6. New ADR-003: invite token stays in the path (smallest change, matches F3-1), with log redaction (app, proxy, error tracking), `Cache-Control: no-store`, `Referrer-Policy: no-referrer`, malformed token = 404; data-model.md and the contract point to it.
7. data-model.md: stale text fixed (stories exist, ER diagram `description`, unique index for `lower(email)`, vote toggle algorithm); grep of architecture/ and decisions/ found no other stale add/remove-vote, pagination or hashed-invite text.
8. `jwt.decode` required claims are the same in the contract and ADR-002: `exp, iat, sub, iss, aud, typ, jti` (`org` is checked per endpoint because it is absent before an organization exists; `jti` is present but unused).
9. `stack.md` addendum: uv, Python/Node/nginx image tags, ruff, mypy, TanStack Query and Vitest (final), no OpenAPI client generator pinned (reason in the file); Node 24 wording corrected to Maintenance LTS.
Also from the review: same-day-release risk note, 404-before-403 order stated in the contract conventions, 404 (not 400) for malformed invite tokens, 422/`BUSINESS_RULE_VIOLATION` removed from the contract (used by no operation), duplicated "no composition rules" removed, trusted-proxy and secret-rotation notes added to ADR-002. TypeScript 6.0.3 and `display_name` at signup are confirmed by the Orchestrator (relayed from the human); ba-bot will update the stories for `display_name`.

## Acceptance criteria
| Criterion | Status (met / not met) | Test that proves it |
|---|---|---|
| Given stack.md, every row has version, last-release date and an official source link, and no pre-release versions | **met** (with 3 documented freshness exceptions, see Open questions) | `stack.md` tables: every row has pinned version, exact version, date, URL. Versions fetched from PyPI JSON, npm registry, python.org, postgresql.org, nodejs.org, GitHub releases on 2026-10-27. Pre-release check: no version string contains rc/beta/dev/canary/pre; dist-tags checked (npm dist-tags checked 2026-10-27: typescript `latest` 7.0.2 vs `rc`/`beta`/`next` pre-releases; vite `latest` 8.3.5 vs `beta`; react `latest` 19.3.1 vs `canary`/`rc`; only stable versions are pinned). |
| Given the data model, votes are unique per user+post and every tenant table has organization_id | **met** | `data-model.md` section 3.6: `UNIQUE (user_id, post_id)`; section 1 lists the tenant tables (memberships, invites, posts, votes, comments, each `organization_id uuid NOT NULL`, indexed in section 5); `organizations` is the tenant root; `users` is global by design (explained). Composite FKs make cross-org votes/comments impossible. Not executed against a live database (doc task); backend-bot's migration `0001_initial` must test it. |
| Given the OpenAPI file, it validates with an OpenAPI linter and covers every feature F1-F9 | **met** | Lint results below. Coverage script: all 18 operations carry `x-features` (the two approved extras have `[]` and `x-extra: true`); union over the other 16 = F1..F9 (F1 auth, F2 orgs/invites/me, F3 invite create/preview/accept, F4 create/get post, F5 POST vote toggle, F6 comments list/create, F7 list+filter+sort, F8 status PATCH, F9 DELETE post). |
| Given a cross-org request, the contract specifies a 404 response | **met** | `api-contract.yaml`: every `/posts/{post_id}*` operation and `/invites/{token}*` lists `404` -> `components/responses/NotFound` (`POST_NOT_FOUND`/`INVITE_NOT_FOUND`, "exists in another organization is indistinguishable"). Stated in `info.description` and in the operation descriptions. No request field or parameter carries an organization id (`grep organization_id api-contract.yaml` = 0 matches). |
| Deliver in one PR on `feature/TASK-001-stack-and-contracts`, title `TASK-001: ...` | **met** | PR #2 https://github.com/Gopi-Git001/feedback_borard/pull/2 (opened by another agent from the architect-bot's local commits, because architect-bot has no push access), branch `feature/TASK-001-stack-and-contracts`, title starts `TASK-001: `, commits `TASK-001: ...`. Attempt 2 commits are delivered as patches in `/workspace/TASK-001/attempt2/` on the shared box until someone with push access pushes them. |

## Files changed
All new, all under `docs/project/`:
- `docs/project/stack.md`
- `docs/project/decisions/ADR-001-pinned-stack.md`
- `docs/project/decisions/ADR-002-password-hashing-and-jwt.md`
- `docs/project/decisions/ADR-003-invite-token-handling.md` (new in attempt 2)
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
- `@redocly/cli` 2.71.2 `lint` (recommended ruleset), re-run in attempt 2 on the final file: **valid, 0 errors, 1 warning** (`info-license`: no license object, deliberate for an internal project). First run had 2 errors (`nullable` without `type`) and 10 warnings; all fixed.
- Contract coverage script: 15 paths, 18 operations, features F1-F9 all covered. Every operation has `x-roles`. All operations that return a body have an example response; the 2 operations without examples (`POST /auth/logout`, `DELETE /posts/{post_id}`) have no request/response body (204).
- Argon2 parameters executed: argon2-cffi 25.1.0 with `RFC_9106_LOW_MEMORY` gave `type=ID, version=19, salt_len=16, hash_len=32, time_cost=3, memory_cost=65536, parallelism=4`; hash+verify round trip OK, hash alone 40-65 ms (5 runs), hash+verify ~130 ms on the architect box.
- Not run: SQL DDL was not executed against PostgreSQL (no DDL file is delivered, only the model); no application tests (no code in scope).

## Decisions made (and why)
- Python 3.14 (not 3.15), Node 24 LTS (not 26), TypeScript 6.0.3 (not 7.0.2, because typescript-eslint 8.72.1 supports only `<6.1.0`), SQLAlchemy 2.1.6 with 2.0.55 fallback, `react-router` 8.5.1 single package. Reasons in ADR-001 and stack.md notes.
- Argon2id (RFC 9106 low-memory profile) over bcrypt; PyJWT HS256 with secret from env; access 15 min in JS memory; refresh 7 days in HttpOnly SameSite=Strict cookie; role read from DB per request, not stored in the token (ADR-002).
- Added `POST /auth/refresh` and `POST /auth/logout` (now approved per Orchestrator message 2026-10-27, relayed from the human; extras beyond F1-1): refresh was requested by the Orchestrator's message; logout is needed because an HttpOnly cookie can only be cleared by the server. Both are small additions beyond the TASK-001.md endpoint list.
- `POST /posts/{id}/vote` toggles and returns `VoteState` (200), so the UI can update counts without a refetch. Status change is `PATCH /posts/{id}/status`.
- Creating an org or accepting an invite returns a new access token with the `org` claim (the claim changes).
- Denormalised `vote_count` and `comment_count` on posts for efficient sort-by-votes; maintained transactionally.
- Composite foreign keys `(organization_id, post_id)` as database-level tenant isolation; PostgreSQL RLS recorded as a follow-up.
- Reconciled with the TASK-002 stories (merged to main during this task, PR #1): one persistent invite token per organization (F3-1), stored in clear because the admin is shown the same link every time, `POST /organizations/current/invite` is get-or-create; vote is a single toggle endpoint `POST /posts/{id}/vote` (F5-1); no pagination (F7-1, F6-1); password min 8 (F1-1); limits: org name 60, title 120, description required 2000, comment 1000; messages "Email already registered", "Invalid email or password", "You already belong to an organization", "Invite link is invalid". Where my first draft differed, the stories won.

## Open questions
1. Architect-bot cannot push (no git credentials; the GitHub connector has no commit tool). PR #2 was opened by another agent from my local commits; attempt 2 is provided as patches (`/workspace/TASK-001/attempt2/`) and needs someone with push access to apply them to the PR branch.
2. Freshness exceptions (older than 12 months, still the latest stable and not deprecated): argon2-cffi 25.1.0 (2025-06-03), email-validator 2.3.0 (2025-08-26), httpx 0.28.1 (2024-12-06, only 1.0 dev pre-releases exist after it). bcrypt 5.0.0 (2025-09-25) is also older than 12 months. Orchestrator to accept or overrule.
3. TypeScript 6.0.3 instead of the newer stable 7.0.2 (lint compatibility): confirmed by the Orchestrator (relayed from the human) on 2026-10-27; revisit when typescript-eslint supports TS 7.
4. `react-router` v8 usage in SPA/library mode should be confirmed by frontend-bot against reactrouter.com (the docs page fetched only described framework mode).
5. Stories F1-F9 are marked READY "conditional on brief approval"; if the brief changes (limits, password minimum 8, no pagination), the contract and data model change with it.
6. Refresh tokens are stateless (no revocation until expiry, max 7 days); accepted for the MVP, follow-up listed below.
7. SQLAlchemy 2.1 went GA on 2026-09-24; pytest 9.2.0, react-router 8.5.1, uv 0.13.6 and ruff 0.17.3 were released on 2026-10-27, the day of the check: newest releases carry regression risk (fallbacks in stack.md note 11).
8. The 401 rule and 403 `ORG_REQUIRED` remain ASSUMED; Orchestrator to confirm or add them to the stories.
9. Invite token in URL paths (ADR-003) needs security-bot's review; alternatives (body/header, URL fragment) are listed there.
10. `display_name` is required at signup in the contract (approved); the stories do not mention it yet (ba-bot to update).
11. No OpenAPI client generator is pinned: openapi-typescript 7.13.0 has peer `typescript ^5.x`, which conflicts with TypeScript 6.0.3 (stack.md addendum).
12. Stories (TASK-002) landed on main while I worked; I rebased onto main (`0567ef4`), reconciled contract and data model with them (see Decisions made), and in attempt 2 checked against the PR #3 version (`b495550`).

## Suggested follow-up tasks
- Persistent audit log table for admin actions (status change, delete).
- Refresh-token revocation (`jti` table) and reuse detection.
- PostgreSQL Row-Level Security as a second tenant-isolation layer.
- Invite revocation/regeneration (out of MVP; needs an ADR because of `UNIQUE (organization_id)`), pagination for board and comments.
- Backend scaffold task: Alembic `0001_initial` from `data-model.md` plus cross-org isolation tests; frontend scaffold task generating a typed client from `api-contract.yaml`.
- Upgrade review for TypeScript 7 / Python 3.15 / Node 26 LTS.
- Optional hardening: composite FKs to `memberships` for authors/voters, `kid`-based JWT key rotation, encrypting `invites.token` at rest, logging/redaction tests for ADR-003.
