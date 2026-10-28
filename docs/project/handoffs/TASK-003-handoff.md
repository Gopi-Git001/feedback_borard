# Handoff: TASK-003 Repo layout, .gitignore, .env.example and compose `db` service
Bot: devops-bot   Attempt: 1   PR: #9 (merged at 6372059), follow-up PR #12 (merged at 8b7b121), hardening PR: #19   Branch: feature/TASK-003-hardening-db-roles

Task spec and plan row: `docs/project/plan.md` (row TASK-003, and the "TASK-003" acceptance line). Required reviewers: qa-bot and **security-bot (mandatory second reviewer)**.

## Summary
Attempt 1. History of this task on main: PR #9 (https://github.com/Gopi-Git001/feedback_borard/pull/9) was merged at `6372059` (merge commit `ec9df3d`) and PR #12 (https://github.com/Gopi-Git001/feedback_borard/pull/12, db init script, `APP_DB_*` variables, criterion 6) was merged at `8b7b121` (PR head `78b9752`). **Both were merged before qa-bot or security-bot reviewed them.** This hardening PR, on a new branch from main, addresses their findings: qa-bot's post-merge review of PR #12 (https://github.com/Gopi-Git001/feedback_borard/pull/12#issuecomment-6459409065) and security-bot's items M-1 and 2 to 5. The four files it changes were identical on main and at `78b9752` (checked through the GitHub connector against main `8b7b121`).

What changes: `.env.example` has **no usable default passwords** (both password variables are empty and compose refuses to start `db` while either is empty); the init script `db/init/01-roles.sh` revokes all `PUBLIC` access to the database, is idempotent, takes the passwords through `\getenv` (nothing in psql's argument list or the process list), keeps the password out of the server log and psql's error output even when a statement fails, and refuses `APP_DB_USER` equal to `POSTGRES_USER`; a new helper `db/ops/revoke-app-on-alembic-version.sh` takes the app role's access to `alembic_version` away; this handoff is corrected (stale PR text removed, `change-me-*` text removed, review findings recorded). The rest of the task (layout, `.gitignore`, `.env.example` with every `stack.md` variable plus the db-container variables, compose service `db` with `postgres:18.6-alpine`) is unchanged from PR #9 and PR #12. Verified on a real Docker engine (29.9.2, Compose v5.6.1) on a fresh volume. No `docs/` file is changed except this handoff. No secrets anywhere.

**Deviation from the TASK-003 spec (AC5), see Open question 8:** copying `.env.example` to `.env` alone no longer starts `db`; both passwords must be generated first (security-bot M-1).

## Acceptance criteria
| Criterion | met / not met | Evidence |
|---|---|---|
| 1. `backend/`, `frontend/`, `e2e/` exist with a README placeholder; `docs/` untouched except this handoff | met | `backend/README.md`, `frontend/README.md`, `e2e/README.md` (on main since PR #9); this PR changes only the files under "Files changed in this PR" (docs/ only `docs/project/handoffs/TASK-003-handoff.md`) |
| 2. `.env` is ignored (also node_modules, Python caches, venvs, build outputs, Playwright reports, IDE files) | met | After `cp .env.example .env`, `git status --short` does not list `.env`; `git check-ignore -v` output below |
| 3. `.env.example` has placeholders only and lists every env var of ADR-002..004 and the contract | met | 17 application variables = every row of the `stack.md` "Environment variables" table (checked by script: 17 of 17 present) plus 6 db-container variables (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST_PORT`, `APP_DB_USER`, `APP_DB_PASSWORD`; 23 in all); source table below. No usable password anywhere: `POSTGRES_PASSWORD=` and `APP_DB_PASSWORD=` are empty, `JWT_SECRET` and `INVITE_TOKEN_KEY` are `REPLACE_WITH_...` text that the backend rejects, and the passwords inside `DATABASE_URL` / `DATABASE_MIGRATION_URL` are `REPLACE_WITH_...` text that cannot log in |
| 4. `docker compose config` is valid, no `version:` key, `db` uses `postgres:18.6-alpine` with healthcheck, named volume, no hard-coded passwords | met | output below, with passwords filled from `openssl rand -hex 24` (redacted here). With the unchanged `.env.example` copy compose fails on purpose (criterion 8), because the passwords are empty; the `.env` needs both passwords (Open question 9) |
| 5. With `.env` from `.env.example`, `docker compose up -d db` makes db healthy; evidence is `docker compose ps` | met **with a deviation from the AC5 text** | after `cp .env.example .env` and filling both passwords (`openssl rand -hex 24`), `docker compose ps` below shows db healthy; with the unchanged copy `up` is refused (criterion 8). Open question 8 |
| 6. After a fresh `docker compose up -d db` (`down -v` first, `.env` from `.env.example` with both passwords filled): both roles exist, both can connect with their real passwords, and the app role cannot create tables (permission denied) while the owner can | met | commands and outputs under "Criterion 6" below; `docker compose ps` shows db healthy |
| 7. (PR #12 review hardening) Database access is closed to everybody except the owner and the app role: `REVOKE ALL ON DATABASE ... FROM PUBLIC`, then `CONNECT` granted to the app role (a third role is refused, the app role has no TEMPORARY); `db/init/01-roles.sh` is idempotent: run again on the live db it succeeds, leaves every privilege unchanged and re-syncs the app password | met | outputs under "Criterion 7" below |
| 8. (security-bot M-1) No usable default password: `.env.example` has empty `POSTGRES_PASSWORD` and `APP_DB_PASSWORD` (comments give `openssl rand -hex 24`); compose fails on empty values with a clear message; with generated values it works | met | outputs under "Criterion 8" below |
| 9. (security-bot 3) The app role has no privilege on `alembic_version`; idempotent helper `db/ops/revoke-app-on-alembic-version.sh`, safe when the table is missing | met | outputs under "Criterion 9" below; TASK-006 must call it (Suggested follow-up tasks) |
| 10. (security-bot 4) No password in psql's argument list or the process list | met | outputs under "Criterion 10" below |
| 11. (qa-bot 4, security-bot) A failing password-bearing statement does not put the password into `docker compose logs db` | met, residual limits listed | control run versus real script under "Criterion 11" below |
| Deliverable: PR opened with evidence | met | hardening PR #19 (branch `feature/TASK-003-hardening-db-roles`) carries criteria 7 to 11 and this handoff; PR #9 (`6372059`, merge commit `ec9df3d`) carried criteria 1 to 5 and PR #12 (`8b7b121`, head `78b9752`) criterion 6, both merged before review |

## Files changed in this PR (vs main `8b7b121`)
- `.env.example`: empty `POSTGRES_PASSWORD` and `APP_DB_PASSWORD` with generation comments; URL placeholders `REPLACE_WITH_*`; comments on Alembic-only-as-owner and on the port in the URLs
- `docker-compose.yml`: `${VAR:?}` messages for both passwords (they fail on empty values), mount `./db/ops` read-only at `/opt/db-ops`, header comment
- `db/init/01-roles.sh` (mode 755): idempotent (role created only if missing, attributes, password and grants always re-applied); `REVOKE ALL ON DATABASE ... FROM PUBLIC`, then `GRANT CONNECT` to the app role; `\getenv` instead of `-v` for the password; session `SET log_min_error_statement = panic` and `log_statement = 'none'` and terse psql errors; guard `APP_DB_USER` differs from `POSTGRES_USER`
- `db/ops/revoke-app-on-alembic-version.sh` (new, mode 755): manual, idempotent helper
- `docs/project/handoffs/TASK-003-handoff.md` (this file)

Already on main from PR #9 and PR #12 (not changed here): `.gitignore`, `backend/README.md`, `frontend/README.md`, `e2e/README.md`, the first versions of `.env.example`, `docker-compose.yml`, `db/init/01-roles.sh` and this handoff.

## How to test locally
```
git clone https://github.com/Gopi-Git001/feedback_borard && cd feedback_borard
git checkout feature/TASK-003-hardening-db-roles       # or main once the PR is merged
ls -d backend frontend e2e                       # criterion 1
cp .env.example .env && git status --short       # criterion 2: .env is not listed
git check-ignore -v .env node_modules/x .venv/x dist/x playwright-report/x .idea/x
docker compose config -q                         # criterion 8: FAILS, both passwords are empty (on purpose)
sed -i "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$(openssl rand -hex 24)/; s/^APP_DB_PASSWORD=.*/APP_DB_PASSWORD=$(openssl rand -hex 24)/" .env
docker compose config                            # criterion 4 (valid now)
docker compose down -v                           # init scripts run only on an EMPTY volume, so start fresh
docker compose up -d db && docker compose ps     # criterion 5: STATUS "(healthy)"
# criterion 6: connect from another container on the compose network (see the NOTE below), real passwords:
set -a; . ./.env; set +a
C() { u=$1; p=$2; shift 2; docker run --rm --network feedback-board_default -e PGPASSWORD="$p" postgres:18.6-alpine psql -h db -U "$u" -d "$POSTGRES_DB" "$@"; }
C "$POSTGRES_USER" "$POSTGRES_PASSWORD" -c "select rolname, rolsuper, rolbypassrls from pg_roles where rolname in ('feedback_owner','feedback_app')"
C "$POSTGRES_USER" "$POSTGRES_PASSWORD" -c "create table probe(id serial primary key, v text)"   # owner: CREATE TABLE
C "$APP_DB_USER" "$APP_DB_PASSWORD" -c "create table app_made(id int)"                            # app: permission denied for schema public
C "$APP_DB_USER" "$APP_DB_PASSWORD" -c "insert into probe(v) values ('x')" -c "select * from probe"  # app: DML works
C "$POSTGRES_USER" "$POSTGRES_PASSWORD" -c "create role throwaway login password 'throwaway-test-pw'"
C throwaway throwaway-test-pw -c "select 1"        # criterion 7: FATAL permission denied for database (no CONNECT)
docker compose exec db sh /docker-entrypoint-initdb.d/01-roles.sh   # criterion 7: manual re-run on the live db, exits 0
C "$POSTGRES_USER" "$POSTGRES_PASSWORD" -c "create table alembic_version(version_num text)"      # criterion 9
docker compose exec db sh /opt/db-ops/revoke-app-on-alembic-version.sh
C "$APP_DB_USER" "$APP_DB_PASSWORD" -c "select * from alembic_version"   # permission denied for table alembic_version
C "$POSTGRES_USER" "$POSTGRES_PASSWORD" -c "drop table probe, alembic_version" -c "drop role throwaway"
docker compose down -v && rm .env                # clean up the throwaway volume and file
```
NOTE: in the official image `pg_hba.conf` trusts loopback (`127.0.0.1`, `::1`, unix socket) and requires `scram-sha-256` only for other addresses. A `psql -h 127.0.0.1` run inside the db container therefore accepts any password; to test the real passwords connect from another container on the compose network (as above) or from the host through the published port.


## Test results
Environment: Debian 13 box, Docker Engine 29.9.2, Docker Compose v5.6.1 (matches the v5.6 pin), image `postgres:18.6-alpine` (PostgreSQL 18.6). Everything below is one complete evidence run on a fresh volume with the final files (script `/workspace/evidence-pr12.sh` on the devops-bot box, log of the same name). Passwords were generated with `openssl rand -hex 24` for the run and are shown as `<owner-pw>` / `<app-pw>`; throwaway test values are labelled.

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

**Criterion 8 (M-1): the unchanged template is refused, a filled one works.** `.env` = `cp .env.example .env`, nothing edited:
```
$ docker compose config -q
error while interpolating services.db.environment.APP_DB_PASSWORD: required variable APP_DB_PASSWORD is missing a value: Set APP_DB_PASSWORD in .env (cp .env.example .env, then openssl rand -hex 24)
error while interpolating services.db.environment.POSTGRES_PASSWORD: required variable POSTGRES_PASSWORD is missing a value: Set POSTGRES_PASSWORD in .env (cp .env.example .env, then openssl rand -hex 24)
exit=1
$ docker compose up -d db
error while interpolating services.db.environment.APP_DB_PASSWORD: required variable APP_DB_PASSWORD is missing a value: Set APP_DB_PASSWORD in .env (cp .env.example .env, then openssl rand -hex 24)
error while interpolating services.db.environment.POSTGRES_PASSWORD: required variable POSTGRES_PASSWORD is missing a value: Set POSTGRES_PASSWORD in .env (cp .env.example .env, then openssl rand -hex 24)
exit=1
$ (only POSTGRES_PASSWORD filled) docker compose config -q
error while interpolating services.db.environment.APP_DB_PASSWORD: required variable APP_DB_PASSWORD is missing a value: Set APP_DB_PASSWORD in .env (cp .env.example .env, then openssl rand -hex 24)
exit=1
-- grep for literal default passwords in .env.example, docker-compose.yml, db/:
none
```
Both passwords are `VAR=` (empty) in the template (`.env.example` lines 58 and 67). `${VAR:?msg}` fails on empty values as well as unset ones, so a copied template cannot start the database with a guessable password. Note for TASK-007 / TASK-008: CI must generate or inject both passwords (see Open question 9).

**Criterion 4 (`docker compose config`, passwords filled; trimmed):**
```
name: feedback-board
services:
  db:
    restart: unless-stopped
    environment:
      APP_DB_PASSWORD: <app-pw>
      APP_DB_USER: feedback_app
      POSTGRES_DB: feedback_board
      POSTGRES_PASSWORD: <owner-pw>
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
      - type: bind
        source: <checkout>/db/ops
        target: /opt/db-ops
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
The password values are interpolated by compose from `.env`; `docker-compose.yml` itself holds only `${VAR:?...}` references. `grep -n '^version' docker-compose.yml` finds nothing (no legacy key). A grep for password text outside comments in compose and the scripts finds only the `${...}` references and the psql variable `:'app_password'` and its `\getenv` line (no literal password). `docker compose config` prints the passwords in clear text, so do not paste its output into logs or CI output (Open question 11).

**Criterion 3 (re-run):** `.env.example` defines 23 variables; the 17 names of the `stack.md` table are all present (script: 0 missing), the other 6 are the db-container variables listed below. No password has a usable value (see the criterion table).

**Criterion 5 (`docker compose up -d db`, then `docker compose ps`, fresh volume, passwords filled):**
```
NAME                  IMAGE                  COMMAND                  SERVICE   CREATED         STATUS                   PORTS
feedback-board-db-1   postgres:18.6-alpine   "docker-entrypoint.s…"   db        6 seconds ago   Up 6 seconds (healthy)   127.0.0.1:5432->5432/tcp
```
Extra checks (first run, before the init script existed): `select version()` returned `PostgreSQL 18.6 on x86_64-pc-linux-musl`; `PGDATA=/var/lib/postgresql/18/docker` (inside the volume mounted at `/var/lib/postgresql`); a table created before `docker compose down` was still there after `docker compose up -d db` (volume works).

**Criterion 6 (fresh volume; trimmed):**

Init log (`docker compose logs db`): the entrypoint ran the script once and every statement succeeded. (The three `SET` tags of the log-protection settings are filtered out of this listing; no `ERROR` or `NOTICE` line appears.)
```
CREATE DATABASE
/usr/local/bin/docker-entrypoint.sh: running /docker-entrypoint-initdb.d/01-roles.sh
CREATE ROLE
ALTER ROLE
REVOKE
REVOKE
GRANT
GRANT
REVOKE
REVOKE
ALTER DEFAULT PRIVILEGES
ALTER DEFAULT PRIVILEGES
```
The checks below connect from a second container on the compose network (`docker run --network feedback-board_default ... psql -h db`), because loopback inside the db container is `trust` in this image and would accept any password.
```
### roles
    rolname     | rolsuper | rolcreatedb | rolcreaterole | rolbypassrls | rolcanlogin
----------------+----------+-------------+---------------+--------------+-------------
 feedback_app   | f        | f           | f             | f            | t
 feedback_owner | t        | t           | t             | t            | t
(2 rows)

### wrong pw
psql: error: connection to server at "db" (172.18.0.2), port 5432 failed: FATAL:  password authentication failed for user "feedback_app"
psql: error: connection to server at "db" (172.18.0.2), port 5432 failed: FATAL:  password authentication failed for user "feedback_owner"
### owner
  current_user  | tcp
----------------+-----
 feedback_owner | t
(1 row)

CREATE TABLE
### app
 current_user | non_loopback
--------------+--------------
 feedback_app | t
(1 row)

INSERT 0 1
 id | v
----+---
  1 | x
(1 row)

### app create
ERROR:  permission denied for schema public
LINE 1: create table app_made(id int)
                     ^
```
Further checks: as `feedback_app`, `ALTER TABLE` and `DROP TABLE` on the owner's table fail with `must be owner of table probe` (below); `CREATE SCHEMA` fails with `permission denied for database feedback_board`, `CREATE ROLE` fails with `permission denied to create role` (earlier run). Default privileges of `feedback_owner`: tables `feedback_app=arwd`, sequences `feedback_app=U`; schema `public` has `pg_database_owner=UC`, `=U` and `feedback_app=U`. The app role was tested only against throwaway objects; the real tables arrive with the TASK-006 migration (data-model.md R7 gate G1).

**Criterion 7 (REVOKE ALL on the database from PUBLIC, idempotent script; same run):**
```
### app temp table
ERROR:  permission denied to create temporary tables in database "feedback_board"
LINE 1: create temp table t(id int)
                          ^
### app alter/drop
ERROR:  must be owner of table probe
ERROR:  must be owner of table probe
### owner DDL
CREATE TABLE
DROP TABLE
### throwaway role cannot connect
CREATE ROLE
psql: error: connection to server at "db" (172.18.0.2), port 5432 failed: FATAL:  permission denied for database "feedback_board"
DETAIL:  User does not have CONNECT privilege.
### database ACL
    datname     |                              datacl
----------------+-------------------------------------------------------------------
 feedback_board | {feedback_owner=CTc/feedback_owner,feedback_app=c/feedback_owner}
(1 row)

### rerun init script twice on live db
SET SET SET ALTER ROLE REVOKE REVOKE GRANT GRANT REVOKE REVOKE ALTER DEFAULT PRIVILEGES ALTER DEFAULT PRIVILEGES exit=0
exit2=0
PRIVILEGES UNCHANGED
db|{feedback_owner=CTc/feedback_owner,feedback_app=c/feedback_owner}
schema|pg_database_owner|{pg_database_owner=UC/pg_database_owner,=U/pg_database_owner,feedback_app=U/pg_database_owner}
defacl|feedback_owner|S|{feedback_app=U/feedback_owner}
defacl|feedback_owner|r|{feedback_app=arwd/feedback_owner}
role|feedback_app|f|f|f|f|f|t
tableacl|probe|{feedback_owner=arwdDxtm/feedback_owner,feedback_app=arwd/feedback_owner}
### app works after rerun; throwaway refused
 count
-------
     1
(1 row)

psql: error: connection to server at "db" (172.18.0.2), port 5432 failed: FATAL:  permission denied for database "feedback_board"
DETAIL:  User does not have CONNECT privilege.
```
**Criterion 10 (no password in psql argv or the process list).** The scripts call `psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB"` with the SQL on stdin; the passwords are read inside psql with `\getenv app_password APP_DB_PASSWORD` and used as `:'app_password'`. A sampler read `/proc/*/cmdline` inside the container 300 times while the script ran 10 times:
```
psql -v ON_ERROR_STOP=1 --username feedback_owner --dbname feedback_board
lines containing the app password: 0
lines containing the owner password: 0
```
(The sampler's own `sh -c` text contains the word `psql`, which is why the positive-control count is large; the real command line captured is the single `psql -v ON_ERROR_STOP=1 --username feedback_owner --dbname feedback_board` line, and no captured line contains either password.)

**Criterion 7 (password re-sync):**
```
### password resync
 ?column?
-----------
 new pw ok
(1 row)

psql: error: connection to server at "db" (172.18.0.2), port 5432 failed: FATAL:  password authentication failed for user "feedback_app"
       ?column?
----------------------
 original pw restored
(1 row)
```
**Criterion 11 (the password does not reach the server log, also on failure).** Failure forced with `PGOPTIONS="-c default_transaction_read_only=on"`: every statement that changes a role then fails (`cannot execute ALTER ROLE in a read-only transaction`) while the session `SET` commands still work. The control is a copy of the script with the three `SET log_*` lines removed. The failing statement is `ALTER ROLE ... PASSWORD :'app_password'`; the `CREATE ROLE` statement carries no password. Each run used its own random test password (control `ctl-...`, real script `real-...`).
```
-- control (script copy WITHOUT the SET log_* lines), forced failure with PGOPTIONS=-c default_transaction_read_only=on:
script exit=3
ERROR:  cannot execute ALTER ROLE in a read-only transaction
server log lines containing the control password: 1
db-1  | 2026-10-28 02:58:25.885 UTC [3571] STATEMENT:  ALTER ROLE "feedback_app" WITH LOGIN PASSWORD '<control-pw>'
-- real script (with the SET log_* lines), same forced failure:
script exit=3
SET
SET
SET
ERROR:  cannot execute ALTER ROLE in a read-only transaction
server log lines containing the real-script password: 0
last 3 server log lines (the control's STATEMENT, then the real script's ERROR with no STATEMENT line after it):
db-1  | 2026-10-28 02:58:25.885 UTC [3571] STATEMENT:  ALTER ROLE "feedback_app" WITH LOGIN PASSWORD 'ctl-52e410d890e882277dd3a548'
db-1  | 	  NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
db-1  | 2026-10-28 02:58:27.161 UTC [3586] ERROR:  cannot execute ALTER ROLE in a read-only transaction
-- whole server log, every password used in this run (owner, app, resync, control, real-script):
  0 <owner-pw>
  0 <app-pw>
  0 resync-test-pw
  1 ctl-52e410d890e882277dd3a548
  0 real-52e410d890e882277dd3a548
-- guard: APP_DB_USER equal to POSTGRES_USER is refused before psql runs:
01-roles.sh: APP_DB_USER must differ from POSTGRES_USER (the owner role)
exit=2
-- state unchanged after the failed runs:
PRIVILEGES UNCHANGED
```
Result: without the settings the failed statement is written to the server log together with the plaintext password (`STATEMENT: ALTER ROLE ... PASSWORD '...'`, qa-bot's finding reproduced); with the final script the log has the `ERROR` line only, no `STATEMENT` line and no password. Across the whole run, `docker compose logs db` contains neither the owner password, the app password nor the re-sync test password (0 matches each). What is NOT covered (residual exposure):
- The password is visible in the container environment: `docker inspect`, `docker compose config` and `/proc/<pid>/environ` of the db container (see Open question 11).
- The `SET`s are session-level: they protect the init script's and the re-run's own session. A different client that sends the password in SQL (for example a human running `ALTER ROLE ... PASSWORD` by hand) is logged on error as usual unless that client sets the same options.
- `pg_stat_statements` is not loaded in this image; if added later it can keep statement text, so role-password statements should not be run through a monitored session.
- psql prints its own error to the terminal or to `docker compose exec` output: `\set VERBOSITY terse` removes the `LINE n:` excerpt, so the password is not echoed there either, but anyone who redirects other output is on their own.

**Criterion 9 (alembic_version helper; the owner creates `alembic_version`, then the helper runs):**
```
-- before the table exists:
public.alembic_version does not exist yet: nothing to revoke (run again after the first migration)
exit=0
CREATE TABLE
INSERT 0 1
-- default privileges let the app role touch it (the problem):
 version_num
-------------
 0001
(1 row)

UPDATE 1
UPDATE 1
-- run helper:
REVOKE
revoked all privileges of feedback_app on public.alembic_version
exit=0
app: select * from alembic_version
ERROR:  permission denied for table alembic_version
app: insert into alembic_version values ('9')
ERROR:  permission denied for table alembic_version
app: update alembic_version set version_num='x'
ERROR:  permission denied for table alembic_version
app: delete from alembic_version
ERROR:  permission denied for table alembic_version
-- other tables still accessible to app:
INSERT 0 1
 count
-------
     2
(1 row)

UPDATE 2
DELETE 0
-- helper again (idempotent) and owner still full access:
REVOKE
revoked all privileges of feedback_app on public.alembic_version
exit=0
 version_num
-------------
 0001
(1 row)

     relname     |                                  relacl
-----------------+---------------------------------------------------------------------------
 alembic_version | {feedback_owner=arwdDxtm/feedback_owner}
 probe           | {feedback_owner=arwdDxtm/feedback_owner,feedback_app=arwd/feedback_owner}
(2 rows)

-- tables created later (new migration) are accessible again as designed:
CREATE TABLE
 count
-------
     0
(1 row)

DROP TABLE
DROP ROLE
Did not find any tables.
```
The default privileges (`ALTER DEFAULT PRIVILEGES FOR ROLE <owner>`) give the app role DML on every table the owner creates, `alembic_version` included, so without the helper the app could rewrite the migration version. The helper revokes all privileges on that one table (idempotent, no error when the table is missing). It must be called after the first migration and again whenever the table is recreated (TASK-006: Suggested follow-up tasks). `docker compose exec db sh /opt/db-ops/revoke-app-on-alembic-version.sh`.

**Cleanup:**
```
### cleanup
 Network feedback-board_default Removing
 Volume feedback-board_db_data Removed
 Network feedback-board_default Removed
no feedback volumes
no feedback networks
ls: cannot access '.env': No such file or directory (deleted)
```
Throwaway objects (`probe`, `alembic_version`, role `throwaway`) were dropped; throwaway passwords (`throwaway-test-pw`, `ctl-...`, `real-...`, the re-sync value) are test values that exist only in the test commands, not in the repo.


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
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | **chosen by devops-bot** (names accepted by the Orchestrator; `POSTGRES_PASSWORD` is empty in the template on purpose): stack.md l.97 ("variables for the database container itself ... are chosen by devops-bot in TASK-003"); names are those of the official postgres image |
| `POSTGRES_HOST_PORT` | **chosen by devops-bot** (not in any document), accepted by the Orchestrator: host port for db, bound to 127.0.0.1 |
| `APP_DB_USER`, `APP_DB_PASSWORD` | **chosen by devops-bot** (not in any document): name and password of the restricted application role, read by `db/init/01-roles.sh`; `APP_DB_PASSWORD` is empty in the template on purpose; the user and password must match `DATABASE_URL` |

Not included on purpose: `RATE_LIMIT_LOGIN_PER_ACCOUNT` and `RATE_LIMIT_INVITE_ACCEPT_PER_USER` (removed in attempt 3, stack.md l.120). The contract (`api-contract.yaml`) names no variable of its own; it points to ADR-002.

## Operating conditions (security-bot item 5; read before relying on the roles)
- **Init scripts run only on a fresh volume.** The official image skips `/docker-entrypoint-initdb.d` when the data directory exists. Recovery or change of the roles or passwords: `docker compose down -v` (deletes the data), or run the idempotent script by hand on the live db: `docker compose exec db sh /docker-entrypoint-initdb.d/01-roles.sh` (re-applies attributes, password and grants; a changed `APP_DB_USER` creates a new role and does not rename or drop the old one).
- **Alembic runs only as the owner role** (`DATABASE_MIGRATION_URL`), never as the app role: the default privileges for the app role cover only tables the owner creates, and the app role has no `CREATE` on schema `public`. After the first migration (and whenever `alembic_version` is recreated) run `db/ops/revoke-app-on-alembic-version.sh`.
- **The owner is the image's bootstrap superuser**: a local-MVP risk for Gopi to accept (not devops-bot's call), Open question 1.
- Role passwords are two different values from `openssl rand -hex 24`; hex is URL-safe. `openssl rand -base64` also works for the variables, but `/`, `+` and `=` must then be percent-encoded inside `DATABASE_URL`.

## Decisions made (and why)
- **Volume mount `/var/lib/postgresql`, not `/var/lib/postgresql/data`.** The PostgreSQL 18 image sets `PGDATA=/var/lib/postgresql/18/docker` (confirmed in the pinned image) and declares `/var/lib/postgresql` as its volume; this layout supports later major-version upgrades.
- **Healthcheck uses TCP (`-h 127.0.0.1`).** During first start the image runs a temporary server that listens on the unix socket only; a socket check can report healthy before the real server is up.
- **`${VAR:?message}` for user, password and database name, and both passwords are empty in the template.** No default password exists anywhere; a missing or empty value stops compose with a message that names the variable and the generation command (security-bot M-1).
- **Database port published on `127.0.0.1` only**, so host-side pytest and Alembic (TASK-004, TASK-006) can reach it without exposing it on other interfaces.
- **Top-level `name: feedback-board`** keeps the project, network and volume names stable (`feedback-board_db_data`) whatever the checkout directory is called.
- **`.env.*` is ignored with `!.env.example` re-included**, plus `*.pem` and `*.key` as a guard against committed keys. Lock files (`uv.lock`, `package-lock.json`) are not ignored (stack.md requires them).
- **`COOKIE_SECURE=false` and `APP_ENV=development` in `.env.example`**: the local stack is plain http (`http://localhost:8080`), and ADR-002 says `.env.example` sets `APP_ENV=development`. Both are refused by the backend in production.
- **Rate-limit, tuning and proxy values are the documented defaults.**
- **Accepted by the Orchestrator and to be used by TASK-004, TASK-006 and TASK-007:** the variable `POSTGRES_HOST_PORT`, the role names `feedback_owner` (owner, `DATABASE_MIGRATION_URL`) and `feedback_app` (restricted, `DATABASE_URL`) and the database name `feedback_board`.
- **Roles are created by `db/init/01-roles.sh` (ADR-004 section 5: "the compose `db` init creates both roles").** The owner is the role the image creates from `POSTGRES_USER`/`POSTGRES_DB` (it owns the database); the script creates the app role. Passwords never appear in the script or in compose files: compose passes `APP_DB_USER` / `APP_DB_PASSWORD` from `.env`, psql reads them with `\getenv` (never in argv) and quotes them (`:'app_password'`, `:"app_user"`), so no shell expansion touches SQL. The role is created with `CREATE ROLE ... LOGIN` (no password in that statement) only if it is missing, through `SELECT NOT EXISTS (...) \gset` and `\if`; `ALTER ROLE ... PASSWORD` then always sets password and attributes.
- **Privileges are exactly the ADR-004 section 5 list and nothing more:** `LOGIN`, `NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS`; `REVOKE ALL ON DATABASE ... FROM PUBLIC` and from the app role, then `GRANT CONNECT` to the app role (so only the owner and the app role can connect, and nobody has `TEMPORARY`; ADR-004 section 5 does not ask for temporary tables); `USAGE` (not `CREATE`) on schema `public`, with `CREATE` on `public` also revoked from `PUBLIC` and from the app role (the "no DDL" rule); `SELECT, INSERT, UPDATE, DELETE` on tables and `USAGE` on sequences, granted as `ALTER DEFAULT PRIVILEGES FOR ROLE <owner> IN SCHEMA public` because the tables do not exist yet and Alembic creates them as the owner; `alembic_version` is then excluded with the helper. No RLS, no other grants (see Open questions 1 and 2).
- **Init directory mounted read-only** (`./db/init:/docker-entrypoint-initdb.d:ro`) and **helper directory mounted read-only** (`./db/ops:/opt/db-ops:ro`, never run automatically); the scripts are `.sh` files (they need the environment, which a `.sql` file cannot read) and are committed executable (mode 755).
- **Log protection by session settings, not by a pre-hashed password.** `SET log_min_error_statement = panic`, `log_statement = 'none'`, `log_min_duration_statement = -1` and psql `VERBOSITY terse` run before any statement that carries the password; they need superuser, which the init session has. A pre-hashed `SCRAM-SHA-256$...` verifier would also work but needs a client-side hashing step and a secret that is no longer the value in `.env`.
- **`APP_DB_USER` must differ from `POSTGRES_USER`** (guard in the script, exit 2): the script would otherwise try to demote the bootstrap superuser.

## Open questions
1. **The owner role is a PostgreSQL superuser: a local-MVP risk for Gopi to accept (not devops-bot's call).** In the official image the role named by `POSTGRES_USER` is the bootstrap superuser and cannot be demoted. `feedback_owner` therefore is a superuser, and `DATABASE_MIGRATION_URL` (Alembic) runs with more rights than ADR-004 section 5 asks for (that section requires non-superuser and no `BYPASSRLS` only for the app role). The app role, the one the backend uses, is restricted as required. A least-privilege owner would need a separate bootstrap superuser and a second password variable (the script would then create a non-superuser owner and the database). Please accept the risk for the local MVP or decide on that follow-up; devops-bot did not change it because it changes the accepted `POSTGRES_USER` meaning.
2. **ADR-004 section 5 gaps, filled minimally.** The text lists SELECT/INSERT/UPDATE/DELETE on the application tables, USAGE on sequences, "no DDL", no `BYPASSRLS`, and "the compose `db` init creates both roles". It does not say: (a) how the table grants are applied, so I used `ALTER DEFAULT PRIVILEGES FOR ROLE <owner> IN SCHEMA public`, which covers tables and sequences created later by migrations **only when the owner role creates them** (if Alembic ever runs as another role, grants must be added by the migration); (b) that `CREATE` on schema `public` is revoked from `PUBLIC` and the app role (the ADR only says "no DDL"; PostgreSQL 15+ already withholds it from `PUBLIC` by default, the explicit `REVOKE` makes the rule independent of defaults); (c) whether database privileges are withheld from `PUBLIC` (the ADR does not say; done here: `REVOKE ALL ON DATABASE ... FROM PUBLIC`, then `CONNECT` for the app role; this is no longer a gap, only a choice to confirm); (d) who owns schema `public` (left as PostgreSQL's default, `pg_database_owner`, i.e. the database owner `feedback_owner`); (e) that the app role has no access to `alembic_version` (helper, criterion 9). Please confirm or amend; the grants cannot be tested against the real tables before the TASK-006 migration (data-model.md R7 gate G1).
3. **New variable names `APP_DB_USER` and `APP_DB_PASSWORD`** are devops-bot's choice (not in any document); the app role user and password must match `DATABASE_URL` (the password appears twice in a filled `.env`, as `APP_DB_PASSWORD` and inside `DATABASE_URL`, and the owner password twice as `POSTGRES_PASSWORD` and inside `DATABASE_MIGRATION_URL`; change both together; compose services will build the URLs from the variables in TASK-007). Confirm or rename.
4. **URL scheme:** the documents say "PostgreSQL URL" only. I used `postgresql+psycopg://` (SQLAlchemy 2.1 with psycopg 3, both pinned). backend-bot should confirm in TASK-004 (the Orchestrator left it as is until then).
5. **`INVITE_TOKEN_KEY` placeholder text:** ADR-002 fixes the placeholder only for `JWT_SECRET`. For `INVITE_TOKEN_KEY` I used the analogous non-random text `REPLACE_WITH_OUTPUT_OF_secrets_token_bytes_32_base64url`; it contains `REPLACE`, so ADR-002 check (c) rejects it, and it differs from the `JWT_SECRET` placeholder.
6. **`COOKIE_SECURE=false` in the template:** ADR-002/004 define the default as `true` and say `.env.example` sets `APP_ENV=development`, but do not say what `.env.example` holds for `COOKIE_SECURE`. `false` is needed for plain-http local use; confirm that is intended.
7. **Fixed values that later tasks must honour:** `FRONTEND_ORIGIN=http://localhost:8080` (the frontend service in TASK-007 must publish 8080) and `TRUSTED_PROXY_IPS=172.28.0.10` (TASK-007 must create the compose network, for example `172.28.0.0/24`, and give nginx that address).
8. **Deviation from TASK-003 AC5 (security-bot M-1).** `docs/project/tasks/TASK-003.md` AC5 says that with `.env` from `.env.example`, `docker compose up -d db` makes db healthy. With empty default passwords a plain copy no longer starts db: both passwords must be generated first (`openssl rand -hex 24`). This is deliberate and follows security-bot's M-1; the Orchestrator should amend the AC5 wording (devops-bot does not edit `tasks/`) or reject the change.
9. **`docker compose config` and `up` need a `.env` with both passwords filled** (no default, by design). CI (TASK-008) and the compose services (TASK-007) must generate or inject both passwords (for example `openssl rand -hex 24` at the start of each job, written to `.env` or passed as environment) before any compose command; copying `.env.example` alone makes `docker compose config -q` fail. Note for the TASK-007 and TASK-008 specs; no change in this PR.
10. **Loopback is `trust` inside the db container** (official image `pg_hba.conf`: `local`, `127.0.0.1` and `::1` are `trust`; other addresses `scram-sha-256`). The healthcheck and anything run with `docker compose exec db psql -h 127.0.0.1` need no password. Not a problem for the host-published port or other containers (verified: wrong passwords are refused from another container), but tests of the real passwords must not run inside the db container.
11. **Passwords are visible in the container environment.** Compose passes them as environment variables, so anyone with Docker access on the host can read them with `docker inspect` or `docker compose config`, and a process in the container sees them in `/proc/<pid>/environ`. This is normal for the official image and acceptable for a local single-user stack; a hosted deployment must use secrets files or the platform's secret store instead. Not changed here.
12. **Tooling note:** Docker was not installed on the box. I installed Docker Engine 29.9.2 and Compose v5.6.1 (the `stack.md` pin is v5.6) from Docker's apt repository to run the evidence; the daemon runs with legacy iptables.

(Resolved since the first version: the names `feedback_owner`, `feedback_app`, `feedback_board` and `POSTGRES_HOST_PORT` are accepted; the path differences are fixed in this file: `data-model.md` and `api-contract.yaml` live under `docs/project/architecture/`, and `TEAM-CONVENTIONS.md` is not in this repository.)

## Suggested follow-up tasks
- **TASK-006: call `db/ops/revoke-app-on-alembic-version.sh` right after the first migration (`0001_initial`) and in the migration runner after every migration run** (and after any step that drops and recreates `alembic_version`), as the owner: `docker compose exec db sh /opt/db-ops/revoke-app-on-alembic-version.sh`, or the equivalent `REVOKE ALL ON TABLE public.alembic_version FROM <APP_DB_USER>`. Also re-run the privilege checks against the real tables as `feedback_app` (DML works, DDL refused) and confirm the tables are owned by `feedback_owner` so the default privileges apply. Alembic runs only as the owner.
- TASK-004 / TASK-006 / TASK-007: use `feedback_owner`, `feedback_app`, `feedback_board`, `POSTGRES_HOST_PORT`, `APP_DB_USER` and `APP_DB_PASSWORD` as listed here.
- Gopi (via the Orchestrator): accept or reject the superuser owner role (Open question 1).
- **Owner of `stack.md`: add the database-container variables `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST_PORT`, `APP_DB_USER` and `APP_DB_PASSWORD` to the environment-variable table** (stack.md does not list them; devops-bot did not edit that file).
- Orchestrator: amend TASK-003 AC5 wording (Open question 8) and add criteria 6 to 11 to `docs/project/tasks/TASK-003.md` if wanted (devops-bot does not edit `tasks/`).
- Reviewers (qa-bot, security-bot): check `db/init/01-roles.sh` privileges against ADR-004 section 5 and the log and argv evidence above.
- TASK-007: compose network with the fixed nginx address, frontend on port 8080, backend and migrate services reading `DATABASE_URL` / `DATABASE_MIGRATION_URL` (host `db`); the migrate service must call the alembic_version helper.
- **TASK-007 / TASK-008: CI generates or injects both db passwords** (Open question 9), then runs `docker compose config -q` and a `docker compose up -d --wait db` smoke check with the role checks.
- A startup test that the `.env.example` placeholders for `JWT_SECRET` and `INVITE_TOKEN_KEY` are rejected by the backend settings check (TASK-004).
