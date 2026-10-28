# Handoff: TASK-004 Backend skeleton
Bot: backend-bot   Attempt: 2 (review fixes)   PR: (link filled after open)   Branch: fix/TASK-004-review-fixes

Original delivery merged as `364d9b9` (PR #22) before review. This attempt answers qa-bot's post-merge review (https://github.com/Gopi-Git001/feedback_borard/pull/22#issuecomment-6459670465) and security-bot P22-2 and P22-3. P22-1 is not built here.

## Summary
The skeleton on main is unchanged in scope: uv project on Python 3.14.10, `GET /api/v1/health`, startup refusal for a missing or short `JWT_SECRET`, and the contract error body. This fix branch changes how tests connect, what the handoff claims, the docs routes, and log redaction.

Pytest still runs against real PostgreSQL 18.6. The default connection is the restricted role `feedback_app`. Passwords come only from the environment. `postgresql+psycopg://` still works with SQLAlchemy 2.1.6 and psycopg 3.3.6 (`binary` extra).

## Acceptance criteria
| Criterion | met / not met | Evidence |
|---|---|---|
| uv project on Python 3.14 with stack.md pins and a lock file | met | `tests/test_project_pins.py`. Runtime CPython 3.14.10, uv 0.13.6. |
| `GET /api/v1/health` | met | `tests/test_health.py::test_health_ok`. 200 `{"status":"ok"}`. The contract has no health path. |
| App refuses to start if `JWT_SECRET` is missing or shorter than 32 characters | met | `tests/test_startup.py::test_missing_jwt_secret_exits_nonzero` and `test_short_jwt_secret_exits_nonzero_and_does_not_echo_it` (subprocess, non-zero exit, value not printed). |
| Every error uses `{error:{code,message,details}}`, and FastAPI 422 is remapped to 400 `VALIDATION_ERROR` | met | `tests/test_errors.py`. |
| Undefined edit route `PATCH /api/v1/posts/1` is 404 or 405, not 415 | met | `tests/test_errors.py::test_undefined_edit_route_is_not_415` (text/plain body). |
| pytest runs against real PostgreSQL 18.6 | met | `tests/test_database_connection.py` asserts `"18.6"` in `server_version`. No database mock. |
| ruff and mypy clean | met | Outputs below. |
| `postgresql+psycopg://` works | met | Same connection test. driver `psycopg`, `SELECT 1` is 1, server is PostgreSQL 18.6. Extra: `psycopg[binary]` only. |
| Backend refuses to start on a superuser, `BYPASSRLS`, or owner app role (R18 condition 3) | **not met here** | Owned by TASK-006. ADR-004 R18 condition 3 says the check is tested at TASK-006 with the real roles. Not built in this PR. It must land before any later task builds on the app role. |
| `/docs`, `/redoc`, `/openapi.json` are off | met | `tests/test_errors.py::test_interactive_docs_are_disabled`. All three return 404 with the standard error body. |

## Files changed (this fix)
- `backend/feedback_board/logging_config.py` (redaction filter on the handler; uvicorn loggers share it)
- `backend/feedback_board/main.py` (`uvicorn.run(..., log_config=None)`)
- `backend/feedback_board/app.py` (`docs_url`, `redoc_url`, `openapi_url` are `None`)
- `backend/tests/support.py` (app role by default; passwords from the environment; owner URL helper)
- `backend/tests/conftest.py` (`owner_database_url` and `owner_engine` fixtures for later DDL)
- `backend/tests/test_database_connection.py`, `test_errors.py`, `test_health.py`, `test_logging.py`
- `docs/project/handoffs/TASK-004-handoff.md` (this file)

## How to test locally
`feedback_app` is created by `db/init/01-roles.sh` (PR #19). `.env.example` leaves `POSTGRES_PASSWORD` and `APP_DB_PASSWORD` empty on purpose. `scripts/init-env.sh` is not on main yet (devops-bot). Until that script lands, generate the two passwords with `openssl rand -hex 24` (two different values). Do not commit them.

```
openssl rand -hex 24    # POSTGRES_PASSWORD
openssl rand -hex 24    # APP_DB_PASSWORD
cp .env.example .env
# Put those values in POSTGRES_PASSWORD and APP_DB_PASSWORD.
# Replace REPLACE_WITH_APP_DB_PASSWORD and REPLACE_WITH_POSTGRES_PASSWORD
# in the two URLs with the same values. Hex needs no percent-encoding.
docker compose up -d db
cd backend
uv python install 3.14.10
uv sync
export APP_DB_USER=feedback_app
export APP_DB_PASSWORD='…'          # the value you generated
export POSTGRES_USER=feedback_owner
export POSTGRES_PASSWORD='…'        # the other value; only the owner fixture reads it
export POSTGRES_DB=feedback_board
export POSTGRES_HOST=127.0.0.1
export POSTGRES_HOST_PORT=5432
unset DATABASE_URL                  # the suite then builds the feedback_app URL
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

The suite's default `DATABASE_URL` is `postgresql+psycopg://feedback_app:<APP_DB_PASSWORD>@127.0.0.1:5432/feedback_board`. `owner_engine` is a separate fixture for later DDL (TASK-006). It is not the app connection.

JWT and invite secrets for pytest are generated in `tests/support.py`. Do not export the `.env.example` placeholders into that process. To boot the app, generate `JWT_SECRET` and `INVITE_TOKEN_KEY` with `secrets.token_urlsafe(48)` and export `DATABASE_URL` for `feedback_app`. `python -m feedback_board.main --check` exits 0 when that set is valid. A copied `.env.example` still fails `--check` because the JWT placeholder is rejected.

This run did not use Docker. PostgreSQL 18.6 was the PGDG package `postgresql-18` `18.6-1.pgdg24.04+2`, started with `pg_ctlcluster 18 main start`. The app role was created with the same SQL as `db/init/01-roles.sh`. Passwords were `openssl rand -hex 24` and were not committed.

## Test results
uv 0.13.6. CPython 3.14.10. Commands run in `backend/` against PostgreSQL 18.6 as `feedback_app` (`rolsuper` false, `rolbypassrls` false).

**pytest** (`uv run pytest -q`): 33 passed, 1 warning in 3.46s.

The warning is Starlette's `StarletteDeprecationWarning`: `Using httpx with starlette.testclient is deprecated; install httpx2 instead.` It is raised from the installed `fastapi/testclient.py`. `httpx2` is not pinned in stack.md, so the suite stays on `httpx` 0.28.1. The warning's filename is that local virtualenv file; the machine path is not copied here.

**ruff** (`uv run ruff check .` and `uv run ruff format --check .`):

```
All checks passed!
24 files already formatted
```

**mypy** (`uv run mypy`, strict):

```
Success: no issues found in 23 source files
```

## Decisions made
- **Interactive docs are off.** `api-contract.yaml` does not define `/docs`, `/redoc`, or `/openapi.json` (`openapi: 3.0.3` is the document version, not a route). `FastAPI(..., docs_url=None, redoc_url=None, openapi_url=None)`. A test requires 404 and the standard error body for all three.
- **Redaction filter is on the handler, not the logger.** Python does not apply a logger's filters to records that propagate from a child. `feedback_board`, `uvicorn`, `uvicorn.error`, and `uvicorn.access` share that handler and formatter, and do not propagate. `uvicorn.run` is called with `log_config=None` so uvicorn does not replace the handler. `tests/test_logging.py` captures that handler's output for a child logger and the three uvicorn loggers and asserts the secret is replaced with `[redacted]`.
- **Tests default to `feedback_app`.** Passwords are read from `APP_DB_PASSWORD` and `POSTGRES_PASSWORD` only. There is no password literal in the backend tree. `owner_database_url` / `owner_engine` stay available for TASK-006 DDL and are not the default app URL.
- **R18 startup refusal is not implemented.** ADR-004 R18 condition 3 places that check and its test at TASK-006 (owner role and a `BYPASSRLS` role exit non-zero and print no password; `feedback_app` starts). plan.md also lists it on TASK-004. This PR follows ADR-004 and the orchestrator: do not build it here. It must land in TASK-006 before any later task builds on the app role.
- **404 `NOT_FOUND`, 405 `METHOD_NOT_ALLOWED`, and the health 503 status are outside the contract.** 503 still uses code `INTERNAL_ERROR`, which is in the enum; the status and the other two codes are not. The orchestrator is asking architect-bot. This PR does not invent contract codes.
- **`JWT_SECRET` still uses the ADR-002 rule**, which includes the plan's "missing or shorter than 32 characters" check as the first failure. The value is never printed.

## Open questions
1. Architect-bot: add `NOT_FOUND` and `METHOD_NOT_ALLOWED` to the error-code enum, or pick other codes, and decide whether a database failure on health stays HTTP 503. The orchestrator has asked.
2. Starlette 1.10 wants `httpx2`. It is not pinned. Stay on `httpx` 0.28.1 unless architect-bot pins a replacement.
3. The CORS relaxation in ADR-002 is still not implemented. There is no CORS middleware in this skeleton.

## Suggested follow-up tasks
- **TASK-006, before any later task builds on the app role:** the R18 condition 3 startup refusal (superuser or `BYPASSRLS` exits non-zero, no password in the output; `feedback_app` starts), plus Alembic `0001_initial`. Use `owner_engine` for DDL, not the app URL. Then run `db/ops/revoke-app-on-alembic-version.sh`.
- TASK-007: Dockerfile, listen on `0.0.0.0`. The restricted role already exists via `db/init/01-roles.sh`.
- devops-bot: `scripts/init-env.sh`. Until it is on main, generate passwords with `openssl rand -hex 24`.
