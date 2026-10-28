# Stack: pinned versions (Team Feedback Board)

Status: Proposed (awaiting Orchestrator approval) | Owner: architect-bot | Task: TASK-001
Date checked: **2026-10-27** (America/Chicago). Every version below was fetched live on that date from the source in the last column, not from memory.

The stack itself is **pre-approved** (brief.md, Constraints). Alternatives were not compared. This file only verifies and pins versions.

## Rules for using this file
- Pin **major.minor** in code and CI, with the exact verified patch as a lower bound. Use a lock file (`uv.lock` / `package-lock.json`) so installs are reproducible.
- Python packages: use compatible-release pins (`~=`). For 0.x packages (FastAPI, Uvicorn) the minor version is treated as breaking, so `~=0.162.0` means "0.162.x only".
- No beta / RC / dev / canary / EOL versions anywhere. Verified: every version below is a plain stable release (no `rc`, `beta`, `dev`, `canary`, `pre` suffix) and none is yanked or deprecated on its registry.
- Changing any pin needs an ADR (supersede ADR-001) and Orchestrator go-ahead.

## Runtime and infrastructure

| Component | Pinned (major.minor) | Exact verified version | Last release date | Support status | Source (official) |
|---|---|---|---|---|---|
| Python | **3.14** | 3.14.10 | 2026-10-25 | bugfix; supported until 2030-10 | https://www.python.org/downloads/ (cross-check https://endoflife.date/api/python.json) |
| PostgreSQL | **18** | 18.6 | 2026-08-13 | supported; final release 2030-11-14 | https://www.postgresql.org/support/versioning/ and https://www.postgresql.org/docs/release/18.6/ |
| PostgreSQL Docker image | `postgres:18.6-alpine` | tag exists, rebuilt 2026-10-26 | n/a | follows PostgreSQL 18.6 | https://hub.docker.com/v2/repositories/library/postgres/tags/18.6-alpine |
| Node.js | **24 (LTS "Krypton")** | 24.22.1 | 2026-10-20 | LTS; EOL 2028-04-30 | https://nodejs.org/en/about/previous-releases, https://nodejs.org/dist/index.json (cross-check https://endoflife.date/api/nodejs.json) |
| Docker Compose | **v5.6** | v5.6.1 | 2026-10-21 | current release | https://github.com/docker/compose/releases/tag/v5.6.1 |
| GitHub Actions runner | `ubuntu-24.04` | n/a (GA image label; `ubuntu-latest` = 24.04 today) | n/a | GA | https://github.com/actions/runner-images (README, checked 2026-10-27) |
| actions/checkout | **v7** | v7.0.1 | 2026-07-20 | current | https://github.com/actions/checkout/releases/tag/v7.0.1 |
| actions/setup-python | **v7** | v7.1.0 | 2026-10-22 | current | https://github.com/actions/setup-python/releases/tag/v7.1.0 |
| actions/setup-node | **v7** | v7.1.0 | 2026-10-08 | current | https://github.com/actions/setup-node/releases/tag/v7.1.0 |
| actions/upload-artifact | **v7** | v7.0.2 | 2026-10-07 | current | https://github.com/actions/upload-artifact/releases/tag/v7.0.2 |

## Backend (Python 3.14)

| Package | Pinned | Exact verified version | Last release date | Source (official registry / repo) |
|---|---|---|---|---|
| FastAPI | `~=0.162.0` | 0.162.0 | 2026-10-23 | https://pypi.org/pypi/fastapi/json , https://github.com/fastapi/fastapi/releases/tag/0.162.0 |
| Pydantic | `~=2.14.1` | 2.14.1 | 2026-10-11 | https://pypi.org/pypi/pydantic/json |
| pydantic-settings | `~=2.16.1` | 2.16.1 | 2026-10-20 | https://pypi.org/pypi/pydantic-settings/json |
| Uvicorn (`uvicorn[standard]`) | `~=0.54.0` | 0.54.0 | 2026-09-25 | https://pypi.org/pypi/uvicorn/json |
| SQLAlchemy | `~=2.1.6` | 2.1.6 (2.1.0 GA was 2026-09-24) | 2026-10-21 | https://pypi.org/pypi/sqlalchemy/json |
| Alembic | `~=1.20.1` | 1.20.1 | 2026-10-22 | https://pypi.org/pypi/alembic/json |
| psycopg (`psycopg[binary]`) | `~=3.3.6` | 3.3.6 (cp314 wheels published) | 2026-09-18 | https://pypi.org/pypi/psycopg/json , https://pypi.org/pypi/psycopg-binary/json |
| argon2-cffi (password hashing, ADR-002) | `~=25.1.0` | 25.1.0 | 2025-06-03 (see note 1) | https://pypi.org/pypi/argon2-cffi/json , https://argon2-cffi.readthedocs.io/en/stable/ |
| PyJWT (JWT, ADR-002) | `~=2.15.1` | 2.15.1 | 2026-09-28 | https://pypi.org/pypi/pyjwt/json , https://github.com/jpadilla/pyjwt/releases/tag/2.15.1 |
| email-validator (for Pydantic `EmailStr`) | `~=2.3.0` | 2.3.0 | 2025-08-26 (see note 2) | https://pypi.org/pypi/email-validator/json |
| pytest | `~=9.2.0` | 9.2.0 | 2026-10-27 | https://pypi.org/pypi/pytest/json |
| httpx (FastAPI `TestClient`, tests only) | `~=0.28.1` | 0.28.1 | 2024-12-06 (see note 3) | https://pypi.org/pypi/httpx/json |

Compatibility checked from registry metadata (`requires_python`, `requires_dist`): FastAPI 0.162.0 needs Python >=3.10 and Pydantic >=2.9; SQLAlchemy 2.1.6 needs Python >=3.11; Alembic 1.20.1 needs SQLAlchemy >=2.0; PyJWT 2.15.1 needs Python >=3.9. All are satisfied by Python 3.14 and the pins above. Binary wheels for cp314 exist for psycopg-binary 3.3.6, pydantic-core 2.50.1 and argon2-cffi-bindings 26.1.0.

## Frontend (Node 24 LTS)

| Package | Pinned | Exact verified version | Last release date | Source (npm registry) |
|---|---|---|---|---|
| React / react-dom | `~19.3.1` | 19.3.1 | 2026-10-14 | https://registry.npmjs.org/react/latest , https://registry.npmjs.org/react-dom/latest |
| TypeScript | `~6.0.3` (see note 4) | 6.0.3 | 2026-04-16 | https://registry.npmjs.org/typescript (version 6.0.3) |
| Vite | `~8.3.5` | 8.3.5 | 2026-10-21 | https://registry.npmjs.org/vite/latest (requires Node ^20.19 or >=22.12) |
| @vitejs/plugin-react | `~6.1.2` | 6.1.2 | 2026-10-05 | https://registry.npmjs.org/@vitejs/plugin-react/latest (peer: vite ^8) |
| React Router (`react-router`; see note 5) | `~8.5.1` | 8.5.1 | 2026-10-27 | https://registry.npmjs.org/react-router/latest (requires Node >=22.22) |
| TanStack Query (data fetching, proposed) | `~5.105.0` | 5.105.0 | 2026-10-26 | https://registry.npmjs.org/@tanstack/react-query/latest |
| Vitest (unit tests, proposed) | `~5.0.5` | 5.0.5 | 2026-10-15 | https://registry.npmjs.org/vitest/latest (requires Node ^22.12 or ^24 or >=26) |
| ESLint | `~10.13.0` | 10.13.0 | 2026-10-16 | https://registry.npmjs.org/eslint/latest |
| typescript-eslint | `~8.72.1` | 8.72.1 | 2026-10-26 | https://registry.npmjs.org/typescript-eslint/latest (peer: typescript >=4.8.4 <6.1.0) |
| @types/react, @types/react-dom | `~19.3.0` | 19.3.0 | 2026-09-09 | https://registry.npmjs.org/@types/react/latest |
| @playwright/test (e2e) | `~1.64.1` | 1.64.1 | 2026-10-14 | https://registry.npmjs.org/@playwright/test/latest , https://github.com/microsoft/playwright/releases/tag/v1.64.1 |

## Authentication (built-in, no external service)
Password hashing: **argon2-cffi 25.1.0 (Argon2id)**. Tokens: **PyJWT 2.15.1, HS256**. Details and parameters in ADR-002.

## Notes and exceptions (honest flags)
1. **argon2-cffi** last release is 2025-06-03, older than the 12-month freshness rule in tech-research. It is not abandoned: the repository had a commit on 2026-10-01 (https://github.com/hynek/argon2-cffi), there is no deprecation notice, and it is the Argon2 binding that the pwdlib package (0.3.1, 2026-08-12) wraps via its `argon2` extra (PyPI metadata). bcrypt 5.0.0 (2025-09-25) is also older than 12 months, so neither option passes the rule; argon2 was chosen on merit (ADR-002). Accepted exception, flagged for the Orchestrator.
2. **email-validator** 2.3.0 is from 2025-08-26 (older than 12 months by 2026-08-26). Repository active (commit 2026-10-15). Accepted exception; it is a transitive requirement of Pydantic `EmailStr`.
3. **httpx** 0.28.1 (2024-12-06) is the latest *stable* release; only `1.0.dev*` pre-releases exist after it, and those are forbidden. Last repo commit 2026-02-23. Used only in tests. Accepted exception.
4. **TypeScript 6.0.3, not 7.0.2.** TypeScript 7.0.2 (2026-07-08) is the current `latest` on npm and is stable. It is **not pinned** because typescript-eslint 8.72.1 (the current release) declares peer `typescript >=4.8.4 <6.1.0`, so TS 7 would break the lint step required by the frontend checks in CI. 6.0.3 is the last 6.x release and is not deprecated. Revisit when typescript-eslint supports TS 7 (new ADR). **TypeScript 6.0.3 is confirmed** (Orchestrator message 2026-10-27, relayed from the human).
5. **React Router**: the `latest` tag of `react-router` is 8.5.1; `react-router-dom` is only published as the 7.x line (latest 7.18.5, dist-tag `latest`). Pin the single `react-router` package at 8.5.1 and import everything from `react-router`. frontend-bot should confirm library-mode (SPA, `createBrowserRouter`) usage against https://reactrouter.com when building; if it differs, report to the Orchestrator rather than switch silently.
6. **Python 3.15** (3.15.2, 2026-10-25; first released 2026-10-09) is also stable, and cp315 wheels exist for the key packages. 3.14 is pinned because it was released a year ago (2025-10-07) and has had ten patch releases (3.14.1 to 3.14.10); upgrade to 3.15 in a later, separate task.
7. **Node 26** (26.12.1) is "Current" today and becomes LTS on 2026-10-28 (endoflife.date). Node 24 is pinned because it is an LTS line (since 2025-10-28) with security support until 2028-04-30. Per endoflife.date its *active* support ended on 2026-10-20, so it is now in **Maintenance LTS** (not Active LTS); Node 26 becomes LTS tomorrow (2026-10-28) with active support to 2027-10-27. A **Node 26 review is due** (new ADR, separate task). Node 22 is also still LTS.
8. **SQLAlchemy 2.1** went GA only on 2026-09-24 (about a month before this check). Fallback: SQLAlchemy 2.0.55 (2026-10-16), which Alembic 1.20.1 also supports. See ADR-001 consequences.
9. Playwright browsers are installed by `npx playwright install --with-deps` in CI; browser build versions follow the pinned `@playwright/test`.
10. Do not add the legacy top-level `version:` key to compose files.
11. **Same-day releases (risk, not blocking).** On 2026-10-27, the day of this check, new releases of pytest (9.2.0; previous 9.1.1 from June), react-router (8.5.1; previous 8.5.0 from 2026-10-19), uv (0.13.6; previous 0.13.5, 2026-10-22) and ruff (0.17.3; previous 0.17.2, 2026-10-22) were published. They are the registry `latest` and are pinned as such; if one of them breaks the scaffold, fall back to the previous release named here and report it to the Orchestrator (no new ADR needed for a one-patch fallback inside the same minor, a new ADR for a different minor).

## Addendum: tooling and image gaps (verified 2026-10-27)
Only values fetched live on 2026-10-27 are listed. Anything I could not verify is stated as such.

| Item | Pin | Exact version | Release date | Source (checked 2026-10-27) |
|---|---|---|---|---|
| uv (Python package/venv manager, named in the rules above) | `0.13.6` (fallback 0.13.5, 2026-10-22) | 0.13.6 | 2026-10-27 | https://pypi.org/pypi/uv/json , https://github.com/astral-sh/uv/releases/tag/0.13.6 (prerelease: false). Container image `ghcr.io/astral-sh/uv:<tag>`: **tag not verified** (the registry needs a token and I did not authenticate). Install uv in Docker/CI with `pip install uv==0.13.6` or the `astral-sh/setup-uv` action (action version **not verified**, not pinned here) |
| Backend base image | `python:3.14.10-slim-trixie` | 3.14.10 | image pushed 2026-10-27 | https://hub.docker.com/v2/repositories/library/python/tags/3.14.10-slim-trixie (exists, amd64/arm64 etc.); matches the Python pin above |
| Frontend build image | `node:24.22.1-alpine` | 24.22.1 | image pushed 2026-10-22 | https://hub.docker.com/v2/repositories/library/node/tags/24.22.1-alpine (exists); matches the Node pin above |
| Frontend web server image (serves the Vite build; proxies `/api` in compose) | `nginx:1.30.6-alpine` | 1.30.6 | image pushed 2026-10-22 | https://hub.docker.com/v2/repositories/library/nginx/tags/1.30.6-alpine ; endoflife.date: nginx 1.30 latest 1.30.6, not EOL, 1.31 is the newer line (https://endoflife.date/api/nginx.json) |
| Backend linter/formatter: ruff | `~=0.17.3` | 0.17.3 | 2026-10-27 | https://pypi.org/pypi/ruff/json , https://github.com/astral-sh/ruff/releases/tag/0.17.3 (0.x: minor is breaking; fallback 0.17.2, 2026-10-22) |
| Backend type checker: mypy | `~=2.4.0` | 2.4.0 | 2026-10-01 | https://pypi.org/pypi/mypy/json (requires Python >=3.10; classifiers include 3.14 and 3.15). Alternatives not compared. pyright 1.1.414 (2026-09-10) and ty 0.0.93 (0.0.x, pre-1.0) exist but are not pinned |
| TanStack Query | `~5.105.0` (final) | 5.105.0 | 2026-10-26 | https://registry.npmjs.org/@tanstack/react-query : dist-tag `latest` = 5.105.0; `alpha`/`beta`/`rc` tags exist and are not used. **Final** |
| Vitest | `~5.0.5` (final) | 5.0.5 | 2026-10-15 | https://registry.npmjs.org/vitest : dist-tag `latest` = 5.0.5; `beta`/`rc` tags exist and are not used. **Final** |

**OpenAPI client generator for the frontend: none is pinned.** Findings (npm registry, 2026-10-27): `openapi-typescript` 7.13.0 (2026-02-11) declares peer `typescript ^5.x`, which conflicts with the confirmed TypeScript 6.0.3 pin (npm would refuse the install without `--legacy-peer-deps`); `@hey-api/openapi-ts` 0.99.0 (2026-06-22) accepts TypeScript 6 but is pre-1.0 (0.x, breaking changes between minors); `orval` 8.45.0 (2026-10-25) was not evaluated against TypeScript 6. Recommendation: frontend-bot writes the typed API client by hand from `api-contract.yaml` (18 operations) in the first scaffold task; if a generator is wanted later, it needs its own ADR with a compatibility test against TypeScript 6.0.3.

## Environment variables (single table, attempt 3)
Every environment variable defined by the ADRs, the contract and data-model.md is listed here; if a document and this table disagree, fix the document. Services: **backend** (FastAPI), **migrate** (Alembic, owner role), **nginx** (frontend container), **compose** (compose file or `.env.example`). Variables for the database container itself (for example `POSTGRES_PASSWORD` and the two role passwords) and for the Playwright harness are chosen by devops-bot in TASK-003/007/013 and are not defined here. "Prod-required" means the app must refuse to start when it is missing or invalid with `APP_ENV=production`. Secrets have only a non-random, rejected placeholder in `.env.example` (ADR-002).

| Variable | Type / format | Default | Read by | Prod-required | Meaning (owner) |
|---|---|---|---|---|---|
| `APP_ENV` | enum `development`, `test`, `production` | **none**: unset or any other value means the app refuses to start (fail closed) | backend | yes | switches the dev-only relaxations on or off (ADR-002, ADR-004); every relaxation is refused at startup unless this is `development` or `test` (and also when `FRONTEND_ORIGIN` is a non-local `https://` origin) |
| `JWT_SECRET` | unpadded base64url, decodes to at least 32 bytes, at least 16 distinct characters, no weak fragment | none (placeholder in `.env.example` is rejected on purpose) | backend | yes | HS256 signing key for access and refresh JWTs (ADR-002) |
| `INVITE_TOKEN_KEY` | same rule as `JWT_SECRET`; must differ from it; the HMAC key is the decoded bytes | none (rejected placeholder) | backend | yes | derives the invite token (ADR-003); rotation runbook in ADR-003 |
| `DATABASE_URL` | PostgreSQL URL of the **restricted, non-owner role** | none (compose sets it for the dev role) | backend | yes | runtime connection (ADR-004 section 5) |
| `DATABASE_MIGRATION_URL` | PostgreSQL URL of the **owner role** | none | migrate (never the backend at runtime) | yes, for deploys that migrate | Alembic migrations (ADR-004 section 5) |
| `FRONTEND_ORIGIN` | bare origin `scheme://host[:port]`, no path or trailing slash | none (dev example `http://localhost:8080`, devops-bot fixes the port) | backend (CSRF `Origin` check, CORS), compose | yes | the one allowed origin (ADR-004) |
| `COOKIE_SECURE` | boolean | `true` | backend | must be `true` | `Secure` flag of the refresh cookie; `false` only with `APP_ENV` `development` or `test`; startup exits otherwise (ADR-002 relaxation guard, ADR-004) |
| `TRUSTED_PROXY_IPS` | comma-separated exact IP addresses (no `*`, no `0.0.0.0/0`, no `::/0`) | compose sets the fixed nginx address, for example `172.28.0.10` | backend | yes, non-empty | peers whose `X-Forwarded-For` is believed (ADR-002) |
| `ARGON2_MAX_CONCURRENCY` | integer 1-64 | `4` | backend | no | concurrent Argon2 hashes per worker, at most 256 MiB at 4 (ADR-002) |
| `REFRESH_REUSE_LEEWAY_SECONDS` | integer 0-60 | `10` | backend | no | a refresh token revoked with reason `rotated` less than this many seconds ago gets 401 without revoking the family and without `Set-Cookie`; a token revoked by logout or eviction is never covered (ADR-002) |
| `RATE_LIMIT_ENABLED` | boolean | `true` | backend | must be `true` | switches all limits off for tests only (ADR-002); **e2e, load and CI test runs set it to `false`, except one e2e job and the TASK-010 rate-limit tests, which keep it `true`** (non-production only: startup exits non-zero with `APP_ENV=production`, unset or unknown, ADR-002 relaxation guard, ADR-004) |
| `RATE_LIMIT_SIGNUP_PER_IP` | `<max>/<window_seconds>` | `10/60` | backend | no | signup, per client IP (stories F1-2) |
| `RATE_LIMIT_LOGIN_PER_IP` | same | `10/60` | backend | no | login, per client IP (F1-2) |
| `RATE_LIMIT_REFRESH_PER_IP` | same | `10/60` | backend | no | refresh, per client IP (F1-2) |
| `RATE_LIMIT_INVITE_PREVIEW_PER_IP` | same | `10/60` | backend | no | invite preview, per client IP (F3-1) |
| `RATE_LIMIT_INVITE_ACCEPT_PER_IP` | same | `10/60` | backend | no | invite accept, per client IP (brief; not in a story) |
| `RATE_LIMIT_ORG_CREATE_PER_USER` | same | `10/60` | backend | no | organization create, per user id, checked after 415 and 401 (architect addition, ASSUMED) |

Removed in attempt 3: `RATE_LIMIT_LOGIN_PER_ACCOUNT` (no per-account limit or lockout: out of scope, not offered, F1-2) and `RATE_LIMIT_INVITE_ACCEPT_PER_USER` (accept is per IP). Cookie name, token lifetimes, the 10-family cap, the leeway of 30 s and the password limits are fixed in the ADRs and are not configurable.

Accepted risks and known limits that touch these settings (rate limits, `RATE_LIMIT_ENABLED`, `REFRESH_REUSE_LEEWAY_SECONDS`, `TRUSTED_PROXY_IPS`, `INVITE_TOKEN_KEY`) are recorded only in ADR-004 section 7 (register R1-R17); there is no second copy here. R7 (the SQL was never run on PostgreSQL) is a gate in three checkpoints, G1 at TASK-006 (migration on `postgres:18.6-alpine` and DDL constraint tests), G2 at TASK-010 (the four advisory-lock tests, each with a one-transaction assertion for the locking re-read and the writes, and the limiter tests for signup, login and refresh; the invite limiter tests are at TASK-017 and the nginx client-address test at TASK-007, ASSUMED assignment) and G3 at TASK-017 (key-rotation tests); it closes when G3 passes.

## Change log
- 2026-10-27: initial pinned set (TASK-001, architect-bot).
- 2026-10-27: attempt 2: Node 24 wording corrected (Maintenance LTS), TypeScript 6.0.3 confirmed, same-day-release risk note, addendum for uv, Docker images, ruff, mypy, TanStack Query, Vitest, generator.
- 2026-10-27: attempt 3: one environment-variable table (defaults, readers, production-required), rate-limit variables renamed to the 10/60 per IP rule.
