# Handoff: TASK-003 Repo layout, .gitignore, .env.example and compose `db` service
Bot: devops-bot   Attempt: 1   PR: (not yet opened: see Open question 1)   Branch: feature/TASK-003-repo-layout-compose-db

Task spec and plan row: `docs/project/plan.md` (row TASK-003, and the "TASK-003" acceptance line). Required reviewers: qa-bot and **security-bot (mandatory second reviewer)**.

## Summary
Adds the top-level layout (`backend/`, `frontend/`, `e2e/` with README placeholders), a `.gitignore` that keeps `.env` and build/cache/IDE files out of git, a placeholders-only `.env.example` with every variable of the `stack.md` environment table, and a `docker-compose.yml` with one service, `db` (`postgres:18.6-alpine`, pg_isready healthcheck, named volume, no hard-coded password). Verified on a real Docker engine (29.9.2, Compose v5.6.1): `docker compose up -d db` reaches `healthy` from a `.env` copied from `.env.example`, and data survives `down` / `up`. No `docs/` file is changed except this handoff. No secrets anywhere.

## Acceptance criteria
| Criterion | met / not met | Evidence |
|---|---|---|
| 1. `backend/`, `frontend/`, `e2e/` exist with a README placeholder; `docs/` untouched except this handoff | met | `backend/README.md`, `frontend/README.md`, `e2e/README.md`; `git diff --name-only main` lists only the files under "Files changed" (docs/ only `docs/project/handoffs/TASK-003-handoff.md`) |
| 2. `.env` is ignored (also node_modules, Python caches, venvs, build outputs, Playwright reports, IDE files) | met | After `cp .env.example .env`, `git status --short` does not list `.env`; `git check-ignore -v` output below |
| 3. `.env.example` has placeholders only and lists every env var of ADR-002..004 and the contract | met | 17 application variables = every row of the `stack.md` "Environment variables" table (checked by script: 17 of 17 present) plus 4 db-container variables; source table below. JWT_SECRET and INVITE_TOKEN_KEY carry the generation command, the 32-byte minimum, and (INVITE_TOKEN_KEY) the "must not equal JWT_SECRET" rule; RATE_LIMIT_ENABLED carries the test-only note |
| 4. `docker compose config` is valid, no `version:` key, `db` uses `postgres:18.6-alpine` with healthcheck, named volume, no hard-coded passwords | met | output below. Without a `.env`, `docker compose config` fails on purpose (`${VAR:?}`); use `cp .env.example .env` or `--env-file .env.example` (Open question 8) |
| 5. With `.env` from `.env.example`, `docker compose up -d db` makes db healthy; evidence is `docker compose ps` | met | `docker compose ps` output below (run on this box, Docker 29.9.2) |
| Deliverable: PR opened with evidence | **not met** | The GitHub connector in this run has no file-write tool and the box has no git credentials, so the branch could not be pushed. See Open question 1 |

## Files changed
- `.gitignore` (new)
- `.env.example` (new)
- `docker-compose.yml` (new)
- `backend/README.md` (new, placeholder)
- `frontend/README.md` (new, placeholder)
- `e2e/README.md` (new, placeholder)
- `docs/project/handoffs/TASK-003-handoff.md` (new, this file)

## How to test locally
```
git clone https://github.com/Gopi-Git001/feedback_borard && cd feedback_borard
git checkout feature/TASK-003-repo-layout-compose-db
ls -d backend frontend e2e                       # criterion 1
cp .env.example .env && git status --short       # criterion 2: .env is not listed
git check-ignore -v .env node_modules/x .venv/x dist/x playwright-report/x .idea/x
docker compose config                            # criterion 4 (needs .env, or: docker compose --env-file .env.example config)
docker compose up -d db && docker compose ps     # criterion 5: STATUS "(healthy)"
docker compose down -v && rm .env                # clean up the throwaway volume and file
```

## Test results
Environment: Debian 13 box, Docker Engine 29.9.2, Docker Compose v5.6.1 (matches the v5.6 pin), image `postgres:18.6-alpine` (PostgreSQL 18.6).

**Criterion 2 (`git check-ignore -v`, after `cp .env.example .env`):**
```
.gitignore:3:.env	.env
.gitignore:4:.env.*	.env.local
.gitignore:10:node_modules/	node_modules/x
.gitignore:19:__pycache__/	__pycache__/a.pyc
.gitignore:22:.venv/	.venv/x
.gitignore:25:.pytest_cache/	.pytest_cache/x
.gitignore:33:dist/	dist/x
.gitignore:41:playwright-report/	playwright-report/x
.gitignore:42:test-results/	test-results/x
.gitignore:48:.idea/	.idea/x
.gitignore:49:.vscode/	.vscode/x
.gitignore:5:!.env.example	.env.example      <- the template is NOT ignored (negated rule)
```
`git status --short` with `.env` present lists only `.env.example`, `.gitignore`, `backend/`, `docker-compose.yml`, `e2e/`, `frontend/`.

**Criterion 4 (`docker compose config`, with `.env` copied from `.env.example`; trimmed):**
```
name: feedback-board
services:
  db:
    restart: unless-stopped
    environment:
      POSTGRES_DB: feedback_board
      POSTGRES_PASSWORD: change-me-owner-password
      POSTGRES_USER: feedback_owner
    image: postgres:18.6-alpine
    volumes:
      - type: volume
        source: db_data
        target: /var/lib/postgresql
    healthcheck:
      test: [CMD-SHELL, pg_isready -h 127.0.0.1 -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"]
      timeout: 5s
      interval: 5s
      retries: 10
      start_period: 10s
    ports:
      - mode: ingress
        host_ip: 127.0.0.1
        target: 5432
        published: "5432"
volumes:
  db_data:
    name: feedback-board_db_data
```
`grep -n '^version' docker-compose.yml` finds nothing (no legacy key). With no `.env`, compose refuses to run (no hard-coded password and no default):
```
error while interpolating services.db.environment.POSTGRES_PASSWORD: required variable POSTGRES_PASSWORD is missing a value: Set POSTGRES_PASSWORD in .env (cp .env.example .env)
```
`docker compose --env-file .env.example config -q` exits 0.

**Criterion 5 (`docker compose up -d db`, then `docker compose ps`):**
```
NAME                  IMAGE                  COMMAND                  SERVICE   CREATED         STATUS                   PORTS
feedback-board-db-1   postgres:18.6-alpine   "docker-entrypoint.s…"   db        7 seconds ago   Up 6 seconds (healthy)   127.0.0.1:5432->5432/tcp
```
Extra checks: `select version()` returned `PostgreSQL 18.6 on x86_64-pc-linux-musl`; `PGDATA=/var/lib/postgresql/18/docker` (inside the volume mounted at `/var/lib/postgresql`); a table created before `docker compose down` was still there after `docker compose up -d db` (volume works). Cleanup: `docker compose down -v` removed the container, network and volume (`docker volume ls | grep feedback` is empty); the local `.env` was deleted. No real `.env` is committed.

## Environment variables in `.env.example` and where each name comes from
Sources: `stack.md` = `docs/project/stack.md`, section "Environment variables (single table, attempt 3)", table rows at lines 101-117; ADR-00x line numbers are in the file on `main` at commit 4a2e084.

| Variable | Source |
|---|---|
| `APP_ENV` | stack.md l.101; ADR-002 l.33 (`.env.example` sets `development`); ADR-004 l.35 |
| `JWT_SECRET` | stack.md l.102; ADR-002 l.31 (rule, generation command, rejected placeholder text) |
| `INVITE_TOKEN_KEY` | stack.md l.103; ADR-003 l.32 and l.39 (rule, generation command, differs from JWT_SECRET) |
| `DATABASE_URL` | stack.md l.104; ADR-004 l.44 (section 5, restricted non-owner role) |
| `DATABASE_MIGRATION_URL` | stack.md l.105; ADR-004 l.44 (owner role, Alembic) |
| `FRONTEND_ORIGIN` | stack.md l.106; ADR-004 l.34 (bare origin; dev port fixed to 8080 by devops-bot) |
| `COOKIE_SECURE` | stack.md l.107; ADR-002 l.33; ADR-004 l.35 |
| `TRUSTED_PROXY_IPS` | stack.md l.108; ADR-002 l.66 (`172.28.0.10`) |
| `ARGON2_MAX_CONCURRENCY` | stack.md l.109; ADR-002 l.27 |
| `REFRESH_REUSE_LEEWAY_SECONDS` | stack.md l.110; ADR-002 l.39 |
| `RATE_LIMIT_ENABLED` | stack.md l.111; ADR-002 l.65; ADR-004 section 6 |
| `RATE_LIMIT_SIGNUP_PER_IP`, `RATE_LIMIT_LOGIN_PER_IP`, `RATE_LIMIT_REFRESH_PER_IP`, `RATE_LIMIT_INVITE_PREVIEW_PER_IP`, `RATE_LIMIT_INVITE_ACCEPT_PER_IP`, `RATE_LIMIT_ORG_CREATE_PER_USER` | stack.md l.112-117; ADR-002 table l.54-59 |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | **chosen by devops-bot**: stack.md l.97 ("variables for the database container itself ... are chosen by devops-bot in TASK-003"); names are those of the official postgres image |
| `POSTGRES_HOST_PORT` | **chosen by devops-bot** (not in any document): host port for db, bound to 127.0.0.1 |

Not included on purpose: `RATE_LIMIT_LOGIN_PER_ACCOUNT` and `RATE_LIMIT_INVITE_ACCEPT_PER_USER` (removed in attempt 3, stack.md l.120). The contract (`api-contract.yaml`) names no variable of its own; it points to ADR-002.

## Decisions made (and why)
- **Volume mount `/var/lib/postgresql`, not `/var/lib/postgresql/data`.** The PostgreSQL 18 image sets `PGDATA=/var/lib/postgresql/18/docker` (confirmed in the pinned image) and declares `/var/lib/postgresql` as its volume; this layout supports later major-version upgrades.
- **Healthcheck uses TCP (`-h 127.0.0.1`).** During first start the image runs a temporary server that listens on the unix socket only; a socket check can report healthy before the real server is up.
- **`${VAR:?message}` for user, password and database name.** No default password exists anywhere; a missing `.env` stops compose with a clear message.
- **Database port published on `127.0.0.1` only**, so host-side pytest and Alembic (TASK-004, TASK-006) can reach it without exposing it on other interfaces.
- **Top-level `name: feedback-board`** keeps the project, network and volume names stable (`feedback-board_db_data`) whatever the checkout directory is called.
- **`.env.*` is ignored with `!.env.example` re-included**, plus `*.pem` and `*.key` as a guard against committed keys. Lock files (`uv.lock`, `package-lock.json`) are not ignored (stack.md requires them).
- **`COOKIE_SECURE=false` and `APP_ENV=development` in `.env.example`**: the local stack is plain http (`http://localhost:8080`), and ADR-002 says `.env.example` sets `APP_ENV=development`. Both are refused by the backend in production.
- **Rate-limit, tuning and proxy values are the documented defaults.**

## Open questions
1. **PR not opened (blocker for the deliverable).** In this run the GitHub connector offers no tool that writes files or commits (only branch, PR, review and read tools), and the box has no GitHub credentials (`git push` fails: could not read Username). The work is committed locally on the branch as a single commit, `TASK-003: Add repo layout, .gitignore, .env.example and compose db service`, plus this handoff. The Orchestrator or Gopi needs to push it (or give devops-bot a credential or a write-capable tool), then open the PR titled `TASK-003: Repo layout, .gitignore, .env.example and compose db service`, request qa-bot and security-bot, and fill in the PR link in this file's header.
2. **Restricted database role.** ADR-004 section 5 says "the compose `db` init creates both roles" (owner and restricted non-owner). TASK-003 acceptance does not include it, so no init script exists. `DATABASE_URL` therefore names a role (`feedback_app`) that does not exist yet. Suggested follow-up (TASK-006 or TASK-007): an init script in `/docker-entrypoint-initdb.d` that creates the role (`NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS`), plus `ALTER DEFAULT PRIVILEGES FOR ROLE <owner>` granting SELECT, INSERT, UPDATE, DELETE and sequence USAGE, and one more password variable. The names `feedback_owner`, `feedback_app` and `feedback_board` are devops-bot's choice.
3. **Names not in any document:** `POSTGRES_HOST_PORT`, the db and role names above. Confirm or rename.
4. **URL scheme:** the documents say "PostgreSQL URL" only. I used `postgresql+psycopg://` (SQLAlchemy 2.1 with psycopg 3, both pinned). backend-bot should confirm in TASK-004.
5. **`INVITE_TOKEN_KEY` placeholder text:** ADR-002 fixes the placeholder only for `JWT_SECRET`. For `INVITE_TOKEN_KEY` I used the analogous non-random text `REPLACE_WITH_OUTPUT_OF_secrets_token_bytes_32_base64url`; it contains `REPLACE`, so ADR-002 check (c) rejects it, and it differs from the `JWT_SECRET` placeholder.
6. **`COOKIE_SECURE=false` in the template:** ADR-002/004 define the default as `true` and say `.env.example` sets `APP_ENV=development`, but do not say what `.env.example` holds for `COOKIE_SECURE`. `false` is needed for plain-http local use; confirm that is intended.
7. **Fixed values that later tasks must honour:** `FRONTEND_ORIGIN=http://localhost:8080` (the frontend service in TASK-007 must publish 8080) and `TRUSTED_PROXY_IPS=172.28.0.10` (TASK-007 must create the compose network, for example `172.28.0.0/24`, and give nginx that address).
8. **`docker compose config` needs a `.env`.** By design it fails without one. CI (TASK-008) must copy `.env.example` to `.env` (or pass `--env-file .env.example`) before any compose command.
9. **Placeholder DB passwords are weak on purpose** (`change-me-*`), and PostgreSQL does not reject them. They are acceptable only because the port is bound to 127.0.0.1 and the stack is local-only (R16); anyone exposing the db must change them. The owner password appears twice in `.env.example` (`POSTGRES_PASSWORD` and inside `DATABASE_MIGRATION_URL`); change both together.
10. **Path differences in the task text:** `data-model.md` and `api-contract.yaml` are under `docs/project/architecture/`, not `docs/project/`. `TEAM-CONVENTIONS.md` is not in this repository (it lives in the private `Saas_Bot` repo), so the conventions were taken from the task message and `plan.md`.
11. **Tooling note:** Docker was not installed on the box. I installed Docker Engine 29.9.2 and Compose v5.6.1 (the `stack.md` pin is v5.6) from Docker's apt repository to run the evidence; the daemon runs with legacy iptables.

## Suggested follow-up tasks
- Create the restricted DB role and default privileges in the db init (Open question 2); owner: devops-bot with backend-bot, security-bot review.
- TASK-007: compose network with the fixed nginx address, frontend on port 8080, backend and migrate services reading `DATABASE_URL` / `DATABASE_MIGRATION_URL` (host `db`).
- TASK-008: CI step that runs `cp .env.example .env && docker compose config -q` and a `docker compose up -d --wait db` smoke check.
- A startup test that the `.env.example` placeholders for `JWT_SECRET` and `INVITE_TOKEN_KEY` are rejected by the backend settings check (TASK-004).
