# Handoff: TASK-004 Backend skeleton
Bot: backend-bot   Attempt: 3 (logging follow-up)   Branch: fix/TASK-004-logging-followup

PR #26 merged to main as `16554277` without the R18 startup refusal. This follow-up builds that check, the logging fixes from the review of PR #26, the httpx2 test client, and the 503 dependency rule.

## Summary
The skeleton stays a uv project on Python 3.14.10 with `GET /api/v1/health`, startup refusal for a missing or short `JWT_SECRET`, and the contract error body. This branch adds:

- The R18 role check on every start, inside the ASGI lifespan, before uvicorn binds the port. There is no setting that turns it off.
- Log redaction on one shared handler attached to the app logger, the uvicorn loggers, and the root logger, including DSN, Bearer, JWT, and `password` patterns. uvicorn access logging is off.
- HTTP 503 `INTERNAL_ERROR` when the database stops accepting the app role after startup, with `Retry-After` and no `Set-Cookie`.
- The dev test client is `httpx2` 2.16.0 (`~=2.16.0`). The suite passes with it.

Pytest runs against real PostgreSQL 18.6 as `feedback_app`. `postgresql+psycopg://` still works with SQLAlchemy 2.1.6 and psycopg 3.3.6 (`binary` extra).

## Acceptance criteria
| Criterion | met / not met | Evidence |
|---|---|---|
| uv project on Python 3.14 with stack.md pins and a lock file | met | `tests/test_project_pins.py`. Runtime CPython 3.14.10, uv 0.13.6. `httpx2` replaces the stack.md `httpx` test pin; see Decisions. |
| `GET /api/v1/health` | met | `tests/test_health.py::test_health_ok`. 200 `{"status":"ok"}`. |
| App refuses to start if `JWT_SECRET` is missing or shorter than 32 characters | met | `tests/test_startup.py` subprocess tests. The value is not printed. |
| Every error uses `{error:{code,message,details}}`, and FastAPI 422 is remapped to 400 `VALIDATION_ERROR` | met | `tests/test_errors.py`. |
| Undefined edit route `PATCH /api/v1/posts/1` is 404 `NOT_FOUND`, not 415 | met | `tests/test_errors.py::test_undefined_edit_route_is_not_415`. |
| pytest runs against real PostgreSQL 18.6 | met | `tests/test_database_connection.py` asserts `"18.6"`. No database mock. |
| ruff and mypy clean | met | Outputs below. |
| `postgresql+psycopg://` works | met | Same connection test. Driver `psycopg`. Extra: `psycopg[binary]` only. |
| R18: refuse to start when `DATABASE_URL` is a superuser, has `BYPASSRLS`, is the owner role, or is the migration role; fail closed if the check cannot finish | **met** | `tests/test_runtime_role.py`, through `TestClient` (real lifespan). TASK-004 builds this in the logging follow-up. PR #26 (`16554277`) did not. |
| `/docs`, `/redoc`, `/openapi.json` are off | met | `tests/test_errors.py::test_interactive_docs_are_disabled`. |
| Dependency down answers 503 `INTERNAL_ERROR` with `Retry-After`, no `Set-Cookie`, no leaked driver text | met | `tests/test_health.py::test_health_is_503_when_the_database_rejects_the_app_role`. |

### R18 cases
| Case | Test |
|---|---|
| (1) `SUPERUSER NOBYPASSRLS` refuses | `test_superuser_without_bypassrls_refuses` |
| (2) `NOSUPERUSER BYPASSRLS` refuses | `test_nosuperuser_with_bypassrls_refuses` |
| (3) `feedback_owner` refuses | `test_feedback_owner_refuses` |
| (4) clean role (`NOSUPERUSER NOBYPASSRLS`, not owner, not migration) starts | `test_clean_role_starts` (`GET /api/v1/health` is 200). The normal fixtures use `feedback_app`, which also passes the check (`test_health_ok`). |
| (5) unreachable database fails closed | `test_unreachable_database_fails_closed` and `tests/test_errors.py::test_unreachable_database_fails_closed` |
| (6) refusal output has no password and no DSN | each refusal test joins the handler stream, stdout, stderr, and the exception text and asserts the password and the URL are absent |

## Files changed (this follow-up)
- `backend/feedback_board/logging_config.py` (handler filter, patterns, root logger)
- `backend/feedback_board/main.py` (`log_config=None`, `access_log=False`)
- `backend/feedback_board/role_check.py` (lifespan role check)
- `backend/feedback_board/app.py` (lifespan calls the check before the port opens)
- `backend/feedback_board/errors.py` (503 envelope and `Retry-After`)
- `backend/pyproject.toml`, `backend/uv.lock`, `backend/tests/test_project_pins.py` (`httpx2`)
- `backend/tests/test_logging.py`, `test_runtime_role.py`, `test_errors.py`, `test_health.py`
- `docs/project/handoffs/TASK-004-handoff.md` (this file)

## How to test locally
`feedback_app` is created by `db/init/01-roles.sh` (PR #19). `.env.example` leaves `POSTGRES_PASSWORD` and `APP_DB_PASSWORD` empty. `scripts/init-env.sh` is not on main yet. Until it lands, generate the two passwords with `openssl rand -hex 24`. Do not commit them.

`POSTGRES_PASSWORD` is required for a normal pytest run. `test_owner_engine_is_separate_from_the_app_role` runs by default and reads it through the `owner_engine` fixture. It is not an unused fixture.

```
openssl rand -hex 24    # POSTGRES_PASSWORD
openssl rand -hex 24    # APP_DB_PASSWORD
cp .env.example .env
# Fill both passwords and the two URL placeholders. Hex needs no percent-encoding.
docker compose up -d db
cd backend
uv python install 3.14.10
uv sync
export APP_DB_USER=feedback_app
export APP_DB_PASSWORD='…'
export POSTGRES_USER=feedback_owner
export POSTGRES_PASSWORD='…'
export POSTGRES_DB=feedback_board
export POSTGRES_HOST=127.0.0.1
export POSTGRES_HOST_PORT=5432
unset DATABASE_URL
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

The suite's default `DATABASE_URL` is the `feedback_app` URL. `owner_engine` is a separate connection for DDL and for the owner-role refusal test.

This evidence run did not use Docker. PostgreSQL 18.6 was the PGDG package `postgresql-18` `18.6-1.pgdg24.04+2`, started with `pg_ctlcluster 18 main start`. The app role was created by copying the SQL from `db/init/01-roles.sh` into `psql` as the local postgres superuser. The script file itself was not executed. Passwords were `openssl rand -hex 24` and were not committed. No password literal is stored in the backend tree; tests generate password values at runtime.

## Test results
uv 0.13.6. CPython 3.14.10. Commands run in `backend/` against PostgreSQL 18.6 as `feedback_app` (`rolsuper` false, `rolbypassrls` false). `httpx2` 2.16.0 is installed.

**pytest** (`uv run pytest -q`):

```
........................................                                 [100%]
40 passed in 3.62s
```

The Starlette warning about installing `httpx2` is gone.

**ruff** (`uv run ruff check .` and `uv run ruff format --check .`):

```
All checks passed!
26 files already formatted
```

**mypy** (`uv run mypy`, strict):

```
Success: no issues found in 25 source files
```

## Decisions made
- **R18 is implemented here.** The check is `assert_runtime_role`, called from the FastAPI lifespan. uvicorn 0.54 runs that lifespan before `create_server`, so the port is not opened when the check fails. A bad role, an unreachable database, or any other failure of the check raises `StartupRefused` with a fixed message and `from None`, so the driver error is not chained. There is no environment flag that skips it. `feedback_owner` is both the database owner and the migration role in this project; a set `DATABASE_MIGRATION_URL` also contributes its username, and that URL is never logged.
- **TASK-004 builds the startup refusal in this follow-up.** PR #26 (`16554277`) merged without it. TASK-006 keeps the R7 G1 re-checks (default privileges and no DML on `alembic_version` for the app role) and the `alembic_version` revoke test.
- **503 when the database later rejects the app role.** Message is `Service temporarily unavailable`, code `INTERNAL_ERROR`, `details` is `[]`, `Retry-After` is `1`. The response does not set `Set-Cookie`. The driver error is not copied into the body. Startup with an unreachable database still fails closed instead of serving 503.
- **httpx2 was adopted.** Starlette 1.10 imports `httpx2` and warns on `httpx`. `uv lock` resolved `httpx2` 2.16.0. The full suite passed. `httpx` 0.28.1 was removed from the dev group.
- **Redaction.** `getMessage()` is wrapped so a bad format string cannot escape the logging call; the unformatted arguments are dropped. The filter also redacts `scheme://user:password@host`, `Bearer` tokens, JWT-shaped strings, `password=` text, and an `extra` key named `password`. The same handler is on the root logger. `access_log=False` because the middleware already logs the request and uvicorn would log raw query strings.
- **Interactive docs stay off.** The contract does not define those routes.
- **404 `NOT_FOUND` and 405 `METHOD_NOT_ALLOWED` are still outside the contract enum.** 503 uses `INTERNAL_ERROR`, which is in the enum. Architect-bot still has to decide the other two codes. The 405 `Allow` header is not in this PR.

## Open questions
1. Architect-bot: add `NOT_FOUND` and `METHOD_NOT_ALLOWED` to the error-code enum, or name the codes to use. The 503 status uses `INTERNAL_ERROR` as specified for this follow-up.
2. `httpx2 ~=2.16.0` is not in stack.md. It is pinned here because the installed Starlette imports it. A stack addendum can record it.

## Suggested follow-up tasks
- **TASK-006:** Alembic `0001_initial`, the R7 G1 privilege re-checks, and `db/ops/revoke-app-on-alembic-version.sh`. Use `owner_engine` for DDL. The startup refusal is already in TASK-004.
- TASK-007: Dockerfile, listen on `0.0.0.0`. The restricted role already exists via `db/init/01-roles.sh`.
- devops-bot: `scripts/init-env.sh`. Until it is on main, generate passwords with `openssl rand -hex 24`.
