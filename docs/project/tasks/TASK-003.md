# TASK-003: Repo layout, .gitignore, .env.example and compose `db` service
Owner: devops-bot   Milestone: M0   Size: S   Attempt: 1
Blocked by: TASK-001 (merged)   Branch: feature/TASK-003-repo-layout-compose-db
Reviewers: qa-bot, security-bot

## Goal
A clean clone has the top-level layout (`backend/`, `frontend/` and `e2e/`, each with a short README placeholder), a safe `.gitignore`, an `.env.example` with placeholders only, and a compose `db` service.

## Context (read these)
- docs/project/plan.md (TASK-003 row)
- docs/project/stack.md (`postgres:18.6-alpine`, note 10, the environment-variable table, the Attempt 2 tooling addendum)
- docs/project/decisions/ADR-001-pinned-stack.md
- docs/project/decisions/ADR-002-password-hashing-and-jwt.md
- docs/project/decisions/ADR-003-invite-token-handling.md
- docs/project/decisions/ADR-004-security-baseline.md
- docs/project/architecture/data-model.md
- docs/project/architecture/api-contract.yaml

## Scope
1. Top-level directories `backend/`, `frontend/` and `e2e/`, each with a short README placeholder. No application code.
2. A root `.gitignore` that ignores `.env`, `node_modules`, Python caches (`__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`), virtualenvs (`.venv/`, `venv/`), build outputs (`dist/`, `build/`, `*.egg-info/`), Playwright reports (`playwright-report/`, `test-results/`) and IDE files (`.idea/`, `.vscode/`). `.env.example` stays tracked.
3. A root `.env.example` with placeholders only. Copy every environment-variable name that ADR-002, ADR-003, ADR-004 and the contract name, and invent none. The checklist is the environment-variable table in stack.md (that table is the single list of those names; if a source and the table disagree, follow the table and record it in the handoff). Application names, and only these:
   - `APP_ENV`
   - `JWT_SECRET`
   - `INVITE_TOKEN_KEY`
   - `DATABASE_URL`
   - `DATABASE_MIGRATION_URL`
   - `FRONTEND_ORIGIN`
   - `COOKIE_SECURE`
   - `TRUSTED_PROXY_IPS`
   - `ARGON2_MAX_CONCURRENCY`
   - `REFRESH_REUSE_LEEWAY_SECONDS`
   - `RATE_LIMIT_ENABLED`
   - `RATE_LIMIT_SIGNUP_PER_IP`
   - `RATE_LIMIT_LOGIN_PER_IP`
   - `RATE_LIMIT_REFRESH_PER_IP`
   - `RATE_LIMIT_INVITE_PREVIEW_PER_IP`
   - `RATE_LIMIT_INVITE_ACCEPT_PER_IP`
   - `RATE_LIMIT_ORG_CREATE_PER_USER`
   Do not add the removed names `RATE_LIMIT_LOGIN_PER_ACCOUNT` or `RATE_LIMIT_INVITE_ACCEPT_PER_USER`.
   `JWT_SECRET` and `INVITE_TOKEN_KEY` are non-random placeholders the startup rule rejects (ADR-002: unpadded base64url, decodes to at least 32 bytes, at least 16 distinct characters, no weak fragment). `INVITE_TOKEN_KEY` uses that same rule and must not equal `JWT_SECRET` (ADR-003). Comments in the file give the generation commands and do not contain a generated secret: `JWT_SECRET` with `python -c "import secrets; print(secrets.token_urlsafe(48))"` (ADR-002); `INVITE_TOKEN_KEY` with `python -c "import secrets,base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=').decode())"` (ADR-003).
   Each `RATE_LIMIT_*` limit is the documented default `10/60`. `RATE_LIMIT_ENABLED` is `true`. A comment records the note from ADR-002, ADR-004 and stack.md: e2e, load and CI test runs set `RATE_LIMIT_ENABLED=false`, except one e2e job and the TASK-010 rate-limit tests, which keep it `true`; `false` is allowed only when `APP_ENV` is `development` or `test`, and startup exits non-zero when `APP_ENV` is `production`, unset or unknown.
   The database container's own settings are not in that table. stack.md assigns them to this task (for example `POSTGRES_PASSWORD`, the user and database name, and the two role passwords). Put local placeholders for those in `.env.example` so copying it to `.env` can start `db`. They are placeholders, not production secrets, and they are not extra application variables. ADR-004 section 5: the compose `db` init creates the restricted role (`DATABASE_URL`) and the owner role (`DATABASE_MIGRATION_URL`); passwords come from the environment, never as literals in the compose file.
4. A root compose file whose service for this task is `db`: image `postgres:18.6-alpine` (stack.md), a healthcheck, a named volume for the data directory, and no hard-coded password. No legacy top-level `version:` key (stack.md note 10). Do not add the backend or frontend services (TASK-007).
5. Database roles from ADR-004 section 5, created by the compose `db` init in `db/init/01-roles.sh`. The owner role is the migration role (`DATABASE_MIGRATION_URL`). The restricted app role is the runtime role (`DATABASE_URL`): non-owner, non-superuser, no DDL, no `BYPASSRLS`, with SELECT, INSERT, UPDATE and DELETE on the owner's tables and USAGE on sequences. The restricted app role cannot create, alter or drop. The owner can. Passwords come from the environment only, never as literals in the compose file or the script.

## Acceptance criteria
1. Given a fresh clone, then `backend/`, `frontend/` and `e2e/` exist and each contains a README.
2. Given the `.gitignore`, then `.env` is ignored.
3. Given `.env.example`, then it holds placeholders only and lists every environment variable ADR-002, ADR-003, ADR-004 and the contract name, and no application variable those documents do not name. Database-container placeholders that stack.md assigns to this task are the only addition.
4. Given the compose file, then `docker compose config` is valid, there is no legacy `version:` key, and the `db` service uses `postgres:18.6-alpine` with a healthcheck, a named volume and no hard-coded password.
5. Given `.env` copied from `.env.example`, when `docker compose up -d db` is run, then the db service becomes healthy. Evidence: `docker compose ps`.
6. Given `.env` copied from `.env.example` and a fresh volume, when `docker compose up -d db` is run, then `db/init/01-roles.sh` has created the owner role and the restricted app role and both can connect. The restricted app role cannot create, alter or drop. The owner can.

## Out of scope
Dockerfiles, application code, CI (TASK-007 and TASK-008), real secrets, cloud deploy.

## Deliverables
- PR on the branch above titled `TASK-003: ...`, commits `TASK-003: ...`
- Evidence for each acceptance criterion, recorded in the handoff (criterion 5 includes the output of `docker compose ps`)
- Handoff report docs/project/handoffs/TASK-003-handoff.md (format in TEAM-CONVENTIONS.md section 5)
- Required reviewers: qa-bot and security-bot
