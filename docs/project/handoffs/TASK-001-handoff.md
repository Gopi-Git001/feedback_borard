# Handoff: TASK-001 Verify and pin stack; data model; OpenAPI contract
Bot: architect-bot   Attempt: 1   PR: <PR link: filled in when the PR is opened>   Branch: feature/TASK-001-stack-and-contracts

## Summary
Verified live (2026-10-27) the current stable version, last release date and official source of every component of the pre-approved stack and pinned them in `stack.md`, with ADR-001 (pinned set) and ADR-002 (Argon2id + PyJWT/HS256, token lifetimes and storage). Designed the PostgreSQL data model (7 tables, shared-table tenancy with `organization_id`, composite foreign keys, `UNIQUE (user_id, post_id)` on votes) and an OpenAPI 3.0.3 contract (15 paths, 19 operations) covering features F1-F9, with 404 for cross-organization access. No application, docker or CI code was written.

## Acceptance criteria
| Criterion | Status (met / not met) | Test that proves it |
|---|---|---|
| Given stack.md, every row has version, last-release date and an official source link, and no pre-release versions | **met** (with 3 documented freshness exceptions, see Open questions) | `stack.md` tables: every row has pinned version, exact version, date, URL. Versions fetched from PyPI JSON, npm registry, python.org, postgresql.org, nodejs.org, GitHub releases on 2026-10-27. Pre-release check: no version string contains rc/beta/dev/canary/pre; dist-tags checked (npm dist-tags checked 2026-10-27: typescript `latest` 7.0.2 vs `rc`/`beta`/`next` pre-releases; vite `latest` 8.3.5 vs `beta`; react `latest` 19.3.1 vs `canary`/`rc`; only stable versions are pinned). |
| Given the data model, votes are unique per user+post and every tenant table has organization_id | **met** | `data-model.md` section 3.6: `UNIQUE (user_id, post_id)`; section 1 lists the tenant tables (memberships, invites, posts, votes, comments, each `organization_id uuid NOT NULL`, indexed in section 5); `organizations` is the tenant root; `users` is global by design (explained). Composite FKs make cross-org votes/comments impossible. Not executed against a live database (doc task); backend-bot's migration `0001_initial` must test it. |
| Given the OpenAPI file, it validates with an OpenAPI linter and covers every feature F1-F9 | **met** | Lint results below. Coverage script: all 19 operations carry `x-features`; union = F1..F9 (F1 auth, F2 orgs/invites/me, F3 invite create/preview/accept, F4 create/get post, F5 PUT/DELETE vote, F6 comments list/create, F7 list+filter+sort, F8 status PATCH, F9 DELETE post). |
| Given a cross-org request, the contract specifies a 404 response | **met** | `api-contract.yaml`: every `/posts/{post_id}*` operation and `/invites/{token}*` lists `404` -> `components/responses/NotFound` (`POST_NOT_FOUND`/`INVITE_NOT_FOUND`, "exists in another organization is indistinguishable"). Stated in `info.description` and in the operation descriptions. No request field or parameter carries an organization id (`grep organization_id api-contract.yaml` = 0 matches). |
| Deliver in one PR on `feature/TASK-001-stack-and-contracts`, title `TASK-001: ...` | **not met yet** | See "Open questions" item 1: the architect box could commit locally but could not push or open the PR (the GitHub connector has no commit/push tool and git push needs credentials, which I did not use). The branch with the commits is ready to push. |

## Files changed
All new, all under `docs/project/`:
- `docs/project/stack.md`
- `docs/project/decisions/ADR-001-pinned-stack.md`
- `docs/project/decisions/ADR-002-password-hashing-and-jwt.md`
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
- `@redocly/cli` 2.71.2 `lint` (recommended ruleset): **valid, 0 errors, 1 warning** (`info-license`: no license object, deliberate for an internal project). First run had 2 errors (`nullable` without `type`) and 10 warnings; all fixed.
- Contract coverage script: 15 paths, 19 operations, features F1-F9 all covered. Every operation has `x-roles`. All operations that return a body have an example response; the 2 operations without examples (`POST /auth/logout`, `DELETE /posts/{post_id}`) have no request/response body (204).
- Argon2 parameters executed: argon2-cffi 25.1.0 with `RFC_9106_LOW_MEMORY` gave `type=ID, version=19, salt_len=16, hash_len=32, time_cost=3, memory_cost=65536, parallelism=4`; hash+verify round trip OK, hash alone 40-65 ms (5 runs), hash+verify ~130 ms on the architect box.
- Not run: SQL DDL was not executed against PostgreSQL (no DDL file is delivered, only the model); no application tests (no code in scope).

## Decisions made (and why)
- Python 3.14 (not 3.15), Node 24 LTS (not 26), TypeScript 6.0.3 (not 7.0.2, because typescript-eslint 8.72.1 supports only `<6.1.0`), SQLAlchemy 2.1.6 with 2.0.55 fallback, `react-router` 8.5.1 single package. Reasons in ADR-001 and stack.md notes.
- Argon2id (RFC 9106 low-memory profile) over bcrypt; PyJWT HS256 with secret from env; access 15 min in JS memory; refresh 7 days in HttpOnly SameSite=Strict cookie; role read from DB per request, not stored in the token (ADR-002).
- Added `POST /auth/refresh` and `POST /auth/logout`: refresh was requested by the Orchestrator's message; logout is needed because an HttpOnly cookie can only be cleared by the server. Both are small additions beyond the TASK-001.md endpoint list.
- `PUT/DELETE /posts/{id}/vote` are idempotent and return `VoteState` (200) instead of 201/204/409, so the UI can update counts without a refetch. Status change is `PATCH /posts/{id}/status`.
- Creating an org or accepting an invite returns a new access token with the `org` claim (the claim changes).
- Denormalised `vote_count` and `comment_count` on posts for efficient sort-by-votes; maintained transactionally.
- Composite foreign keys `(organization_id, post_id)` as database-level tenant isolation; PostgreSQL RLS recorded as a follow-up.
- Invite token stored only as SHA-256 hash; raw token returned once.
- Post `description` is optional (default empty) in the contract; the brief says posts have a description.

## Open questions
1. **PR not opened (blocker for the delivery criterion).** The `cursor-github` connector has no tool that commits or pushes files, and plain `git push` needs GitHub credentials, which the bot does not have and must not look for. The 6 files are committed locally on branch `feature/TASK-001-stack-and-contracts` (based on main `f66e21f`) in `/workspace/fbrepo` on the shared box, plus a patch/bundle at `/workspace/TASK-001/`. Need: someone with push access (a cloud agent launched on the repo, or the user) to push the branch and open the PR titled `TASK-001: Stack pins, ADRs, data model and API contract`.
2. Freshness exceptions (older than 12 months, still the latest stable and not deprecated): argon2-cffi 25.1.0 (2025-06-03), email-validator 2.3.0 (2025-08-26), httpx 0.28.1 (2024-12-06, only 1.0 dev pre-releases exist after it). bcrypt 5.0.0 (2025-09-25) is also older than 12 months. Orchestrator to accept or overrule.
3. TypeScript 6.0.3 instead of the newer stable 7.0.2 (lint compatibility). Orchestrator to confirm; revisit when typescript-eslint supports TS 7.
4. `react-router` v8 usage in SPA/library mode should be confirmed by frontend-bot against reactrouter.com (the docs page fetched only described framework mode).
5. Is a non-empty post description required? Modelled as optional.
6. Refresh tokens are stateless (no revocation until expiry, max 7 days); accepted for the MVP, follow-up listed below.
7. SQLAlchemy 2.1 went GA on 2026-09-24 and pytest 9.2.0 was released today (2026-10-27): newest releases carry regression risk.
8. Stories (TASK-002, ba-bot) were not yet available; entities came from the brief. Reconcile when stories land.

## Suggested follow-up tasks
- Persistent audit log table for admin actions (status change, delete).
- Refresh-token revocation (`jti` table) and reuse detection.
- PostgreSQL Row-Level Security as a second tenant-isolation layer.
- Invite revocation endpoint (column `revoked_at` already exists).
- Backend scaffold task: Alembic `0001_initial` from `data-model.md` plus cross-org isolation tests; frontend scaffold task generating a typed client from `api-contract.yaml`.
- Upgrade review for TypeScript 7 / Python 3.15 / Node 26 LTS.
