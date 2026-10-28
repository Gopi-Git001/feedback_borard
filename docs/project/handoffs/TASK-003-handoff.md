# Handoff: TASK-003 Repo layout, .gitignore, .env.example and compose `db` service
Bot: devops-bot   Attempt: 1   PR: #9 (merged), follow-up PR: https://github.com/Gopi-Git001/feedback_borard/pull/12   Branch: feature/TASK-003-followup-db-roles-init

Task spec and plan row: `docs/project/plan.md` (row TASK-003, and the "TASK-003" acceptance line). Required reviewers: qa-bot and **security-bot (mandatory second reviewer)**.

## Summary
Attempt 1, follow-up to the merged PR #9 (Orchestrator decisions on that PR; PR #9 was merged before these commits, so they come on a new branch from main): the db init now also creates the restricted application role (criterion 6). Adds the top-level layout (`backend/`, `frontend/`, `e2e/` with README placeholders), a `.gitignore` that keeps `.env` and build/cache/IDE files out of git, a placeholders-only `.env.example` with every variable of the `stack.md` environment table plus the db-container variables, and a `docker-compose.yml` with one service, `db` (`postgres:18.6-alpine`, pg_isready healthcheck, named volume, no hard-coded password) and `db/init/01-roles.sh`, which creates the restricted `feedback_app` role next to the owner role `feedback_owner` that the image creates (ADR-004 section 5). Verified on a real Docker engine (29.9.2, Compose v5.6.1): `docker compose up -d db` reaches `healthy` from a `.env` copied from `.env.example`, and data survives `down` / `up`; on a fresh volume both roles exist, both log in with their real passwords, the app role is refused `CREATE TABLE` and the owner is not. No `docs/` file is changed except this handoff. No secrets anywhere.

## Acceptance criteria
| Criterion | met / not met | Evidence |
|---|---|---|
| 1. `backend/`, `frontend/`, `e2e/` exist with a README placeholder; `docs/` untouched except this handoff | met | `backend/README.md`, `frontend/README.md`, `e2e/README.md`; `git diff --name-only main` lists only the files under "Files changed" (docs/ only `docs/project/handoffs/TASK-003-handoff.md`) |
| 2. `.env` is ignored (also node_modules, Python caches, venvs, build outputs, Playwright reports, IDE files) | met | After `cp .env.example .env`, `git status --short` does not list `.env`; `git check-ignore -v` output below |
| 3. `.env.example` has placeholders only and lists every env var of ADR-002..004 and the contract | met | 17 application variables = every row of the `stack.md` "Environment variables" table (checked by script: 17 of 17 present) plus 6 db-container variables (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST_PORT`, `APP_DB_USER`, `APP_DB_PASSWORD`; 23 in all); source table below. JWT_SECRET and INVITE_TOKEN_KEY carry the generation command, the 32-byte minimum, and (INVITE_TOKEN_KEY) the "must not equal JWT_SECRET" rule; RATE_LIMIT_ENABLED carries the test-only note |
| 4. `docker compose config` is valid, no `version:` key, `db` uses `postgres:18.6-alpine` with healthcheck, named volume, no hard-coded passwords | met | re-verified after the init script was added; output below. Without a `.env`, `docker compose config` fails on purpose (`${VAR:?}`); use `cp .env.example .env` or `--env-file .env.example` (Open question 8) |
| 5. With `.env` from `.env.example`, `docker compose up -d db` makes db healthy; evidence is `docker compose ps` | met | `docker compose ps` output below (run on this box, Docker 29.9.2) |
| 6. After a fresh `docker compose up -d db` (`down -v` first, `.env` copied from `.env.example`): both roles exist, both can connect with their real passwords, and the app role cannot create tables (permission denied) while the owner can | met | commands and outputs under "Criterion 6" below; `docker compose ps` shows db healthy |
| Deliverable: PR opened with evidence | met | PR #9 (https://github.com/Gopi-Git001/feedback_borard/pull/9, merged) carried criteria 1-5. This follow-up (criterion 6) is on branch `feature/TASK-003-followup-db-roles-init`; follow-up PR: https://github.com/Gopi-Git001/feedback_borard/pull/12. The commits were produced on the box (no credentials) and are pushed by the Orchestrator or Gopi (Open question 1) |

## Files changed
- `.gitignore` (new)
- `.env.example` (new; follow-up adds `APP_DB_USER`, `APP_DB_PASSWORD` and updates the comments of the db block and `DATABASE_URL`)
- `docker-compose.yml` (new; follow-up adds the read-only `./db/init` mount and the `APP_DB_USER` / `APP_DB_PASSWORD` variables)
- `db/init/01-roles.sh` (new, follow-up): creates the restricted application role and its privileges
- `backend/README.md` (new, placeholder)
- `frontend/README.md` (new, placeholder)
- `e2e/README.md` (new, placeholder)
- `docs/project/handoffs/TASK-003-handoff.md` (new, this file)

## How to test locally
```
git clone https://github.com/Gopi-Git001/feedback_borard && cd feedback_borard
git checkout feature/TASK-003-followup-db-roles-init
ls -d backend frontend e2e                       # criterion 1
cp .env.example .env && git status --short       # criterion 2: .env is not listed
git check-ignore -v .env node_modules/x .venv/x dist/x playwright-report/x .idea/x
docker compose config                            # criterion 4 (needs .env, or: docker compose --env-file .env.example config)
docker compose down -v                           # init scripts run only on an EMPTY volume, so start fresh
docker compose up -d db && docker compose ps     # criterion 5: STATUS "(healthy)"
# criterion 6: connect from another container on the compose network (see the NOTE below), real passwords:
set -a; . ./.env; set +a
C() { u=$1; p=$2; shift 2; docker run --rm --network feedback-board_default -e PGPASSWORD="$p" postgres:18.6-alpine psql -h db -U "$u" -d "$POSTGRES_DB" "$@"; }
C "$POSTGRES_USER" "$POSTGRES_PASSWORD" -c "select rolname, rolsuper, rolbypassrls from pg_roles where rolname in ('feedback_owner','feedback_app')"
C "$POSTGRES_USER" "$POSTGRES_PASSWORD" -c "create table probe(id serial primary key, v text)"   # owner: CREATE TABLE
C "$APP_DB_USER" "$APP_DB_PASSWORD" -c "create table app_made(id int)"                            # app: permission denied for schema public
C "$APP_DB_USER" "$APP_DB_PASSWORD" -c "insert into probe(v) values ('x')" -c "select * from probe"  # app: DML works
C "$POSTGRES_USER" "$POSTGRES_PASSWORD" -c "drop table probe"
docker compose down -v && rm .env                # clean up the throwaway volume and file
```
NOTE: in the official image `pg_hba.conf` trusts loopback (`127.0.0.1`, `::1`, unix socket) and requires `scram-sha-256` only for other addresses. A `psql -h 127.0.0.1` run inside the db container therefore accepts any password; to test the real passwords connect from another container on the compose network (as above) or from the host through the published port.

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

**Criterion 4 (`docker compose config`, with `.env` copied from `.env.example`; trimmed; re-run after the init script was added):**
```
name: feedback-board
services:
  db:
    restart: unless-stopped
    environment:
      APP_DB_PASSWORD: change-me-app-password
      APP_DB_USER: feedback_app
      POSTGRES_DB: feedback_board
      POSTGRES_PASSWORD: change-me-owner-password
      POSTGRES_USER: feedback_owner
    image: postgres:18.6-alpine
    volumes:
      - type: volume
        source: db_data
        target: /var/lib/postgresql
      - type: bind
        source: <checkout>/db/init
        target: /docker-entrypoint-initdb.d
        read_only: true
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
The values shown are the `.env.example` placeholders, interpolated by compose from `.env`; `docker-compose.yml` itself holds only `${VAR:?...}` references. `grep -n '^version' docker-compose.yml` finds nothing (no legacy key). `grep -in password docker-compose.yml db/init/01-roles.sh` outside comments shows only `${...}` references and the psql variable `:'app_password'` (no literal password). With no `.env`, compose refuses to run (no hard-coded password and no default):
```
error while interpolating services.db.environment.POSTGRES_PASSWORD: required variable POSTGRES_PASSWORD is missing a value: Set POSTGRES_PASSWORD in .env (cp .env.example .env)
```
`docker compose --env-file .env.example config -q` exits 0.

**Criterion 3 (re-run):** `.env.example` defines 23 variables; the 17 names of the `stack.md` table are all present (script: 0 missing), the other 6 are the db-container variables listed below. Every secret-like value is a placeholder: `JWT_SECRET` and `INVITE_TOKEN_KEY` are `REPLACE_WITH_...` text that the backend rejects, `POSTGRES_PASSWORD=change-me-owner-password`, `APP_DB_PASSWORD=change-me-app-password`, and both URLs carry the same `change-me-*` placeholders as their password variables.

**Criterion 5 (`docker compose up -d db`, then `docker compose ps`; re-run on a fresh volume with the init script mounted):**
```
NAME                  IMAGE                  COMMAND                  SERVICE   CREATED         STATUS                   PORTS
feedback-board-db-1   postgres:18.6-alpine   "docker-entrypoint.s…"   db        7 seconds ago   Up 6 seconds (healthy)   127.0.0.1:5432->5432/tcp
```
Extra checks (first run, before the init script): `select version()` returned `PostgreSQL 18.6 on x86_64-pc-linux-musl`; `PGDATA=/var/lib/postgresql/18/docker` (inside the volume mounted at `/var/lib/postgresql`); a table created before `docker compose down` was still there after `docker compose up -d db` (volume works). Cleanup: `docker compose down -v` removed the container, network and volume (`docker volume ls | grep feedback` is empty); the local `.env` was deleted. No real `.env` is committed.

**Criterion 6 (fresh volume: `docker compose down -v`, `cp .env.example .env`, `docker compose up -d db`; trimmed):**

Init log (`docker compose logs db`): the entrypoint ran the script once and every statement succeeded.
```
/usr/local/bin/docker-entrypoint.sh: running /docker-entrypoint-initdb.d/01-roles.sh
CREATE ROLE
GRANT
GRANT
REVOKE
REVOKE
ALTER DEFAULT PRIVILEGES
ALTER DEFAULT PRIVILEGES
```
The checks below connect from a second container on the compose network (`docker run --network feedback-board_default ... psql -h db`), because loopback inside the db container is `trust` in this image and would accept any password. Passwords are the `.env` values (placeholders).
```
### both roles exist (pg_roles)
    rolname     | rolsuper | rolcreatedb | rolcreaterole | rolbypassrls | rolcanlogin
 feedback_app   | f        | f           | f             | f            | t
 feedback_owner | t        | t           | t             | t            | t        <- image bootstrap role (Open question 2)

### wrong passwords are refused (over the network)
psql: error: connection to server at "db" (172.18.0.2), port 5432 failed: FATAL:  password authentication failed for user "feedback_app"
psql: error: connection to server at "db" (172.18.0.2), port 5432 failed: FATAL:  password authentication failed for user "feedback_owner"

### owner connects with its real password and creates a table
 current_user   | tcp
 feedback_owner | t
CREATE TABLE

### app role connects with its real password, non-loopback, and can use DML (incl. serial sequence) on the owner's table
 current_user | non_loopback
 feedback_app | t
INSERT 0 1
 id | v
  1 | x

### app role cannot create a table
ERROR:  permission denied for schema public
LINE 1: create table app_made(id int)

### owner can create a table
CREATE TABLE   (then DROP TABLE)
```
Further checks run in the same session through the db container: as `feedback_app`, `ALTER TABLE` and `DROP TABLE` on the owner's table fail with `must be owner of table probe`, `CREATE SCHEMA` fails with `permission denied for database feedback_board`, `CREATE ROLE` fails with `permission denied to create role`. Resulting ACLs: schema `public` has `pg_database_owner=UC`, `=U` (PUBLIC: usage only, no create) and `feedback_app=U`; default privileges of `feedback_owner`: tables `feedback_app=arwd` (insert, select, update, delete), sequences `feedback_app=U`.

`docker compose ps` of the same run:
```
NAME                  IMAGE                  COMMAND                  SERVICE   CREATED         STATUS                   PORTS
feedback-board-db-1   postgres:18.6-alpine   "docker-entrypoint.s…"   db        7 seconds ago   Up 6 seconds (healthy)   127.0.0.1:5432->5432/tcp
```
Cleanup after the run: `docker compose down -v` removed container, network and volume; `docker volume ls | grep feedback` and `docker network ls | grep feedback` are empty; `.env` deleted. Throwaway tables (`probe`, `owner_made`) were dropped. The app role was tested only against these throwaway objects; the real tables arrive with the TASK-006 migration (data-model.md R7 gate G1).

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
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | **chosen by devops-bot** (names and values accepted by the Orchestrator): stack.md l.97 ("variables for the database container itself ... are chosen by devops-bot in TASK-003"); names are those of the official postgres image |
| `POSTGRES_HOST_PORT` | **chosen by devops-bot** (not in any document), accepted by the Orchestrator: host port for db, bound to 127.0.0.1 |
| `APP_DB_USER`, `APP_DB_PASSWORD` | **chosen by devops-bot** (not in any document): name and password of the restricted application role, read by `db/init/01-roles.sh`; must match the user and password in `DATABASE_URL` |

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
- **Accepted by the Orchestrator and to be used by TASK-004, TASK-006 and TASK-007:** the variable `POSTGRES_HOST_PORT`, the role names `feedback_owner` (owner, `DATABASE_MIGRATION_URL`) and `feedback_app` (restricted, `DATABASE_URL`) and the database name `feedback_board`.
- **Roles are created by `db/init/01-roles.sh` (ADR-004 section 5: "the compose `db` init creates both roles").** The owner is the role the image creates from `POSTGRES_USER`/`POSTGRES_DB` (it owns the database); the script creates the app role. Passwords never appear in the script or in compose: compose passes `APP_DB_USER` / `APP_DB_PASSWORD` from `.env`, and the script hands them to psql as variables (`-v`, used as `:'app_password'` and `:"app_user"`), so psql quotes them and no shell expansion touches SQL.
- **Privileges are exactly the ADR-004 section 5 list and nothing more:** `LOGIN`, `NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS`; `CONNECT` on the database; `USAGE` (not `CREATE`) on schema `public`, with `CREATE` on `public` also revoked from `PUBLIC` and from the app role (the "no DDL" rule); `SELECT, INSERT, UPDATE, DELETE` on tables and `USAGE` on sequences, granted as `ALTER DEFAULT PRIVILEGES FOR ROLE <owner> IN SCHEMA public` because the tables do not exist yet and Alembic creates them as the owner. No RLS, no other grants (see Open questions 2 and 3).
- **Init scripts run only on a fresh volume.** This is how the official image works (an existing data directory skips `/docker-entrypoint-initdb.d`). Changing the script, `APP_DB_USER` or `APP_DB_PASSWORD` later needs `docker compose down -v` (deletes the data) or a manual `ALTER ROLE ... PASSWORD`. This is stated in the script, in `.env.example` and in "How to test locally".
- **Init directory mounted read-only** (`./db/init:/docker-entrypoint-initdb.d:ro`); the script is a `.sh` file (needs the environment, which a `.sql` file cannot read) and is committed executable.

## Open questions
1. **PR #9 was merged at its old head (`6372059`) without the follow-up commits**, so the follow-up (db init script, `APP_DB_*` variables, this handoff update) is a second PR from `feature/TASK-003-followup-db-roles-init`, branched from main. The GitHub connector offers no file-write tool and the box has no GitHub credentials, so the commits were produced on the box and have to be pushed by the Orchestrator or Gopi; the header records follow-up PR: https://github.com/Gopi-Git001/feedback_borard/pull/12. Request qa-bot and security-bot (mandatory second reviewer) if they are valid GitHub users.
2. **The owner role is a PostgreSQL superuser.** In the official image the role named by `POSTGRES_USER` is the bootstrap superuser and cannot be demoted. `feedback_owner` therefore is a superuser, and `DATABASE_MIGRATION_URL` (Alembic) runs with more rights than ADR-004 section 5 asks for (that section requires non-superuser and no `BYPASSRLS` only for the app role). The app role, the one the backend uses, is restricted as required. A least-privilege owner would need a separate bootstrap superuser and a second password variable (the script would then create a non-superuser owner and the database). Decide whether that is wanted; devops-bot did not do it because it changes the accepted `POSTGRES_USER` meaning.
3. **ADR-004 section 5 gaps, filled minimally.** The text lists SELECT/INSERT/UPDATE/DELETE on the application tables, USAGE on sequences, "no DDL", no `BYPASSRLS`, and "the compose `db` init creates both roles". It does not say: (a) how the table grants are applied, so I used `ALTER DEFAULT PRIVILEGES FOR ROLE <owner> IN SCHEMA public`, which covers tables and sequences created later by migrations **only when the owner role creates them** (if Alembic ever runs as another role, grants must be added by the migration); (b) that `CREATE` on schema `public` is revoked from `PUBLIC` and the app role (the ADR only says "no DDL"; PostgreSQL 15+ already withholds it from `PUBLIC` by default, the explicit `REVOKE` makes the rule independent of defaults); (c) whether `CONNECT` on the database is withheld from `PUBLIC` (not done, since the ADR does not ask for it; the host port is bound to 127.0.0.1 and `pg_hba` requires scram for non-loopback); (d) who owns schema `public` (left as PostgreSQL's default, `pg_database_owner`, i.e. the database owner `feedback_owner`). Please confirm or amend; the grants cannot be tested against the real tables before the TASK-006 migration (data-model.md R7 gate G1).
4. **New variable names `APP_DB_USER` and `APP_DB_PASSWORD`** are devops-bot's choice (not in any document); the app role password and the user must match `DATABASE_URL` (the placeholder password appears twice in `.env.example`, as `APP_DB_PASSWORD` and inside `DATABASE_URL`; change both together). Confirm or rename.
5. **URL scheme:** the documents say "PostgreSQL URL" only. I used `postgresql+psycopg://` (SQLAlchemy 2.1 with psycopg 3, both pinned). backend-bot should confirm in TASK-004 (the Orchestrator left it as is until then).
6. **`INVITE_TOKEN_KEY` placeholder text:** ADR-002 fixes the placeholder only for `JWT_SECRET`. For `INVITE_TOKEN_KEY` I used the analogous non-random text `REPLACE_WITH_OUTPUT_OF_secrets_token_bytes_32_base64url`; it contains `REPLACE`, so ADR-002 check (c) rejects it, and it differs from the `JWT_SECRET` placeholder.
7. **`COOKIE_SECURE=false` in the template:** ADR-002/004 define the default as `true` and say `.env.example` sets `APP_ENV=development`, but do not say what `.env.example` holds for `COOKIE_SECURE`. `false` is needed for plain-http local use; confirm that is intended.
8. **Fixed values that later tasks must honour:** `FRONTEND_ORIGIN=http://localhost:8080` (the frontend service in TASK-007 must publish 8080) and `TRUSTED_PROXY_IPS=172.28.0.10` (TASK-007 must create the compose network, for example `172.28.0.0/24`, and give nginx that address).
9. **`docker compose config` needs a `.env`.** By design it fails without one. CI (TASK-008) must copy `.env.example` to `.env` (or pass `--env-file .env.example`) before any compose command (noted for the TASK-007 and TASK-008 specs; no change in this PR).
10. **Placeholder DB passwords are weak on purpose** (`change-me-*`), and PostgreSQL does not reject them. They are acceptable only because the port is bound to 127.0.0.1 and the stack is local-only (R16); anyone exposing the db must change them. The owner password appears twice in `.env.example` (`POSTGRES_PASSWORD` and inside `DATABASE_MIGRATION_URL`); change both together.
11. **Loopback is `trust` inside the db container** (official image `pg_hba.conf`: `local`, `127.0.0.1` and `::1` are `trust`; other addresses `scram-sha-256`). The healthcheck and anything run with `docker compose exec db psql -h 127.0.0.1` need no password. Not a problem for the host-published port or other containers (verified: wrong passwords are refused from another container), but tests of the real passwords must not run inside the db container.
12. **Tooling note:** Docker was not installed on the box. I installed Docker Engine 29.9.2 and Compose v5.6.1 (the `stack.md` pin is v5.6) from Docker's apt repository to run the evidence; the daemon runs with legacy iptables.

(Resolved since the first version: the names `feedback_owner`, `feedback_app`, `feedback_board` and `POSTGRES_HOST_PORT` are accepted; the path differences are fixed in this file: `data-model.md` and `api-contract.yaml` live under `docs/project/architecture/`, and `TEAM-CONVENTIONS.md` is not in this repository.)

## Suggested follow-up tasks
- TASK-006: when `0001_initial` is applied (R7 gate G1), re-run the privilege checks against the real tables as `feedback_app` (DML works, DDL refused) and confirm the tables are owned by `feedback_owner` so the default privileges apply.
- TASK-004 / TASK-006 / TASK-007: use `feedback_owner`, `feedback_app`, `feedback_board`, `POSTGRES_HOST_PORT`, `APP_DB_USER` and `APP_DB_PASSWORD` as listed here.
- Decide on a non-superuser owner role (Open question 2).
- Reviewers (qa-bot, security-bot): check `db/init/01-roles.sh` privileges against ADR-004 section 5.
- TASK-007: compose network with the fixed nginx address, frontend on port 8080, backend and migrate services reading `DATABASE_URL` / `DATABASE_MIGRATION_URL` (host `db`).
- TASK-008: CI step that runs `cp .env.example .env && docker compose config -q` and a `docker compose up -d --wait db` smoke check.
- A startup test that the `.env.example` placeholders for `JWT_SECRET` and `INVITE_TOKEN_KEY` are rejected by the backend settings check (TASK-004).
