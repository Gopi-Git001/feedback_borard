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
   The database container's own settings are not in that table. stack.md assigns them to this task (for example `POSTGRES_PASSWORD`, the user and database name, and the two role passwords). Put local placeholders for those in `.env.example`. `POSTGRES_PASSWORD` and `APP_DB_PASSWORD` are empty on purpose, so a plain `cp .env.example .env` does not start `db` (the error includes the openssl hint, `openssl rand -hex 24`). They are placeholders, not production secrets, and they are not extra application variables. ADR-004 section 5: `db/init/01-roles.sh` creates only the restricted app role (`DATABASE_URL`). The owner is `POSTGRES_USER`, the image's bootstrap superuser, and that is the role `DATABASE_MIGRATION_URL` uses. Passwords come from the environment, never as literals in the compose file.
4. A root compose file whose service for this task is `db`: image `postgres:18.6-alpine` (stack.md), a healthcheck, a named volume for the data directory, and no hard-coded password. No legacy top-level `version:` key (stack.md note 10). Do not add the backend or frontend services (TASK-007).
5. Database roles from ADR-004 section 5. `db/init/01-roles.sh` creates only the app role (`APP_DB_USER`, password `APP_DB_PASSWORD`). The owner is `POSTGRES_USER`, the image's bootstrap superuser (relayed quote, per Orchestrator, unverified). The script uses `ALTER DEFAULT PRIVILEGES` so tables and sequences the owner creates later grant the app role SELECT, INSERT, UPDATE and DELETE on those tables and USAGE on those sequences. The app role is non-owner, non-superuser, has no DDL and no `BYPASSRLS`. Passwords come from the environment only, never as literals in the compose file or the script.

## Acceptance criteria
1. Given a fresh clone, then `backend/`, `frontend/` and `e2e/` exist and each contains a README.
2. Given the `.gitignore`, then `.env` is ignored.
3. Given `.env.example`, then it holds placeholders only and lists every environment variable ADR-002, ADR-003, ADR-004 and the contract name, and no application variable those documents do not name. Database-container placeholders that stack.md assigns to this task are the only addition.
4. Given the compose file, then `docker compose config` is valid, there is no legacy `version:` key, and the `db` service uses `postgres:18.6-alpine` with a healthcheck, a named volume and no hard-coded password.
5. After generating secrets with `scripts/init-env.sh` (copies `.env.example` to `.env`, generates the db and JWT secrets, and never overwrites an existing `.env`), `docker compose up -d db` shows the db healthy. Evidence: `docker compose ps`. `scripts/init-env.sh` is not on main; devops-bot's PR is pending. A plain `cp .env.example .env` fails clearly, and the error includes the openssl hint (`openssl rand -hex 24`). `POSTGRES_PASSWORD` and `APP_DB_PASSWORD` are empty on purpose (security-bot M-1).
6. Restricted app role. After a fresh `docker compose up -d db` with secrets from `scripts/init-env.sh` (that script is not on main; PR pending), the owner (`POSTGRES_USER`, the image's bootstrap superuser) and the app role (`APP_DB_USER`, created only by `db/init/01-roles.sh`) can connect. `ALTER DEFAULT PRIVILEGES` is in effect: the app role can SELECT, INSERT, UPDATE and DELETE on a table the owner creates later, and gets permission denied on CREATE, ALTER and DROP. The owner can create, alter and drop. A plain `cp .env.example .env` does not reach this check: compose fails first, and the error includes the openssl hint.
7. `PUBLIC` CONNECT is revoked: `REVOKE ALL ON DATABASE ... FROM PUBLIC`, then `CONNECT` is granted to the app role. A third role cannot connect, and the app role has no `TEMPORARY`.
8. `alembic_version` DML is revoked by `db/ops/revoke-app-on-alembic-version.sh` (`REVOKE ALL`, so SELECT, INSERT, UPDATE and DELETE are denied after it runs). TASK-006 runs that script in the migrate step and adds a `--require` style check so a missing table does not silently pass. The copy of the script on main is safe when the table does not exist yet: it echoes and exits 0.
9. Passwords are not in process arguments or server logs. The init script reads them with `\getenv`, not psql `-v`. A failing password-bearing statement does not put the password in `docker compose logs db`.
10. The init script is re-runnable. Running `db/init/01-roles.sh` again on the live database exits 0, leaves privileges unchanged, and re-syncs the app password.
11. Empty passwords fail with a clear error. With the empty `POSTGRES_PASSWORD` and `APP_DB_PASSWORD` from `.env.example`, `docker compose up -d db` refuses to start, names the missing variable, and includes the openssl hint (`openssl rand -hex 24`).

## Out of scope
Dockerfiles, application code, CI (TASK-007 and TASK-008), real secrets, cloud deploy.

## Deliverables
- PR on the branch above titled `TASK-003: ...`, commits `TASK-003: ...`
- Evidence for each acceptance criterion, recorded in the handoff (criterion 5 includes the output of `docker compose ps`)
- Handoff report docs/project/handoffs/TASK-003-handoff.md (format in TEAM-CONVENTIONS.md section 5)
- Required reviewers: qa-bot and security-bot
