# Handoff: TASK-004 Backend skeleton
Bot: backend-bot   Attempt: 1   PR: https://github.com/Gopi-Git001/feedback_borard/pull/22   Branch: feature/TASK-004-backend-skeleton

Base: main commit `11497e9` (`11497e9a337fdad6d56582077ac3c529d77e3e44`).

## Summary
Adds the FastAPI backend skeleton under `backend/`: a uv project on Python 3.14.10 with the stack.md pins and a committed `uv.lock`, `GET /api/v1/health`, startup refusal when configuration is missing or too weak, and one JSON error body for validation, 404, 405, and unhandled 500. Pytest runs against real PostgreSQL 18.6 (not mocked). `postgresql+psycopg://` works with SQLAlchemy 2.1.6 and psycopg 3.3.6 (`binary` extra). No Alembic migrations, no auth endpoints, and no Dockerfile.

`TEAM-CONVENTIONS.md` and `backend-bot/skills/build-api-endpoint/SKILL.md` are not in this repo. `https://github.com/Gopi-Git001/Saas_Bot` returned 404 to the GitHub API, so the handoff follows section 5 as stated in the task and the layout of `TASK-003-handoff.md`. The skill rules that were in the task (layered route/service/repository, validate at the edge, contract error body, structured logs without secrets, one test per acceptance criterion, run build/tests/lint/type check) are what the code follows.

## Acceptance criteria
| Criterion (plan.md TASK-004, commit 11497e9) | met / not met | Evidence |
|---|---|---|
| uv project on Python 3.14 with stack.md pins and a lock file | met | `tests/test_project_pins.py` (`test_runtime_is_python_314`, `test_python_and_dependency_pins`, `test_lock_file_matches_pins`). Runtime: CPython 3.14.10, uv 0.13.6. Locked versions match the verified pins (FastAPI 0.162.0, SQLAlchemy 2.1.6, psycopg 3.3.6, ruff 0.17.3, mypy 2.4.0, and the rest of the backend table). |
| `GET /api/v1/health` | met | `tests/test_health.py::test_health_ok`. 200 `{"status":"ok"}` while PostgreSQL is up. The contract file has no health path; the shape is a decision below. |
| App refuses to start if `JWT_SECRET` is missing or shorter than 32 characters (clear error, non-zero exit) | met | `tests/test_startup.py::test_missing_jwt_secret_exits_nonzero` (exit code not 0, stderr `startup refused: JWT_SECRET is missing`). `test_short_jwt_secret_exits_nonzero_and_does_not_echo_it` (stderr `JWT_SECRET must be at least 32 characters`, the value is not printed). Both run `python -m feedback_board.main` in a subprocess. |
| Every error uses `{error:{code,message,details}}`, and FastAPI 422 is remapped to 400 `VALIDATION_ERROR` | met | `tests/test_errors.py::test_request_validation_is_400_and_drops_the_submitted_value` (400, not 422, code `VALIDATION_ERROR`, submitted value absent). `test_unknown_path_is_404` (`NOT_FOUND`). `test_wrong_method_is_405` (`METHOD_NOT_ALLOWED`). `test_unhandled_exception_is_500_without_the_message` (`INTERNAL_ERROR`, exception text not in the body). |
| pytest runs against real PostgreSQL 18 | met | `tests/test_database_connection.py::test_postgresql_psycopg_scheme_connects_to_postgres_18` and `tests/test_health.py` (health pings `SELECT 1`). No database mock. Server: PostgreSQL 18.6. How the server was started is under Test results (Docker was not available). |
| Backend lint and type check run clean (ruff `~=0.17.3`, mypy `~=2.4.0`) | met | `uv run ruff check .`, `uv run ruff format --check .`, and `uv run mypy` below. Not a pytest; the commands are the check. |
| `postgresql+psycopg://` works with the pinned driver and SQLAlchemy against real PostgreSQL 18 | met | Same connection test. drivername `postgresql+psycopg`, dialect driver `psycopg`, `SELECT 1` returned 1, `version()` is PostgreSQL 18.6. Extra required: `psycopg[binary]` (locked `psycopg-binary` 3.3.6). No further extra. |

## Files changed
- `backend/pyproject.toml` (new)
- `backend/uv.lock` (new)
- `backend/.python-version` (new)
- `backend/README.md` (placeholder replaced with a pointer to this handoff)
- `backend/feedback_board/` (app factory, settings, health route/service/repository, errors, middleware, logging, entrypoint)
- `backend/tests/` (pins, startup, health, errors, database connection)
- `docs/project/handoffs/TASK-004-handoff.md` (this file)

## How to test locally
Docker path (the compose `db` service on main). The example `DATABASE_URL` uses role `feedback_app`, which TASK-003 does not create. Use the owner role the `db` service does create (`POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` from `.env.example`):

```
cp .env.example .env
docker compose up -d db
cd backend
# uv 0.13.6, then:
uv python install 3.14.10
uv sync
export DATABASE_URL='postgresql+psycopg://feedback_owner:change-me-owner-password@127.0.0.1:5432/feedback_board'
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

Do not export the `.env.example` `JWT_SECRET` into the pytest process. The tests set their own secrets. To boot the app itself, generate secrets (the placeholders are rejected):

```
export APP_ENV=test
export JWT_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
export INVITE_TOKEN_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
export FRONTEND_ORIGIN=http://localhost:8080
export TRUSTED_PROXY_IPS=127.0.0.1
export DATABASE_URL='postgresql+psycopg://feedback_owner:change-me-owner-password@127.0.0.1:5432/feedback_board'
uv run python -m feedback_board.main --check   # exit 0
uv run --env-file ../.env python -m feedback_board.main --check   # exit non-zero: placeholders
```

`--check` loads settings and exits. It does not listen. `python -m feedback_board.main` with a valid environment listens on `127.0.0.1:8000`.

This run did not use Docker. See Test results for the PostgreSQL 18.6 install that the suite actually used.

## Test results
Environment: Ubuntu 24.04.5, no Docker (no `docker` binary, no `/var/run/docker.sock`, pid 1 is `tini`, so there is no systemd). PostgreSQL was installed from the official PGDG apt repository and started by hand:

- package `postgresql-18` version `18.6-1.pgdg24.04+2` (PostgreSQL 18.6, the same version as the `postgres:18.6-alpine` image pin)
- `sudo pg_ctlcluster 18 main start` (`policy-rc.d` had denied the package's service start)
- role `feedback_owner` with the `.env.example` placeholder password, database `feedback_board`, port `127.0.0.1:5432` (same names as `docker-compose.yml`)

uv `0.13.6`. CPython `3.14.10`. Commands were run in `backend/`.

Connection evidence (`SELECT 1` and `SELECT version()` through SQLAlchemy, URL scheme `postgresql+psycopg`):

```
drivername postgresql+psycopg
dialect postgresql psycopg
select_1 1
PostgreSQL 18.6 (Ubuntu 18.6-1.pgdg24.04+2) on x86_64-pc-linux-gnu, compiled by gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0, 64-bit
```

`psycopg[binary]` is the extra that was installed (`psycopg` 3.3.6 and `psycopg-binary` 3.3.6). SQLAlchemy 2.1.6. The scheme works. No other driver extra was required.

**pytest** (`uv run pytest -q`):

```
.............................                                            [100%]
=============================== warnings summary ===============================
.venv/lib/python3.14/site-packages/fastapi/testclient.py:1
  /workspace/backend/.venv/lib/python3.14/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
29 passed, 1 warning in 3.51s
```

The warning is Starlette 1.10.0 (pulled in by FastAPI 0.162.0) asking for `httpx2`. `httpx2` is not pinned in stack.md. The suite stays on the pinned `httpx` 0.28.1. Tests passed.

**ruff** (`uv run ruff check .` and `uv run ruff format --check .`):

```
All checks passed!
23 files already formatted
```

**mypy** (`uv run mypy`, strict, Python 3.14):

```
Success: no issues found in 22 source files
```

## Decisions made
- **`JWT_SECRET` check is the ADR-002 rule, which includes the plan's length check.** plan.md still says "missing or <32 chars". ADR-002 and `.env.example` require unpadded base64url that decodes to at least 32 bytes, at least 16 distinct characters, and no weak or placeholder fragment. A 32-character string does not decode to 32 bytes, and the `.env.example` placeholder is longer than 32 characters and is documented as rejected on purpose. The length check runs first, so a short value still produces `JWT_SECRET must be at least 32 characters` and a non-zero exit. The placeholder, a 32-character value, a missing value, and a valid `token_urlsafe(48)` secret are all tested. The same rule is applied to `INVITE_TOKEN_KEY`, and the two values must differ, because `.env.example` says the process refuses otherwise.
- **Other fail-closed settings from stack.md / ADR-002 / ADR-004 are enforced at startup** (`APP_ENV`, `DATABASE_URL` scheme `postgresql+psycopg`, bare `FRONTEND_ORIGIN`, `COOKIE_SECURE=false` and `RATE_LIMIT_ENABLED=false` only in `development` or `test` and not with a non-local `https` origin, `TRUSTED_PROXY_IPS` with no `*` / `0.0.0.0/0` / `::/0` and non-empty in production, rate-limit strings `<max>/<window_seconds>`). Error text names the variable and does not print the value. `DATABASE_MIGRATION_URL` is not read (Alembic is out of scope).
- **Health response is `{"status":"ok"}`.** `api-contract.yaml` does not define `/health`. The route calls the repository, which runs `SELECT 1`. If that fails the status is 503 with `INTERNAL_ERROR` and message `Database unavailable` (still the standard error body). 503 is not in the contract's status list.
- **404 and 405 codes are `NOT_FOUND` and `METHOD_NOT_ALLOWED`.** Those strings are not in the contract's `ErrorResponse.code` enum (that enum is the domain codes). The body shape matches the contract. Unhandled exceptions are 500 `INTERNAL_ERROR` with a fixed message; the exception text is not returned or logged.
- **Validation `details` use Pydantic's rule text (`msg`) and drop `input` and `ctx`.** Field names drop the `body` / `query` / `path` prefix. The envelope message is `Request validation failed.`, matching the contract example.
- **Logs are JSON** on the `feedback_board` logger: method, route template, status, duration, request id. `JWT_SECRET`, `INVITE_TOKEN_KEY`, the database URL, and its password are redacted if they appear. Unmatched paths are logged as `unmatched`, not as the raw path.
- **Security headers from ADR-004** are set on API responses, including errors: `Cache-Control: no-store`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'`, `Permissions-Policy: camera=(), microphone=(), geolocation=()`. No `Strict-Transport-Security` (plain HTTP). uvicorn is started with `proxy_headers=False`.
- **The process listens on `127.0.0.1:8000`.** TASK-007 owns the container and will need `0.0.0.0` there. This task does not add a Dockerfile.
- **Alembic, argon2-cffi, PyJWT, and email-validator are dependencies** so `uv.lock` pins the stack.md backend table. They are not used yet (TASK-006 and TASK-009).
- **Tests connect as `feedback_owner`.** The restricted `feedback_app` role does not exist (TASK-003 open question 2). The scheme test is about the URL driver, not that role split.
- **`hatchling` is not used.** `tool.uv.package = false`. No build-backend version was invented.

## Open questions
1. Should `api-contract.yaml` gain `GET /health` with `{"status":"ok"}`, and should a database failure stay 503 `INTERNAL_ERROR`? Changing the contract needs an ADR.
2. Should `NOT_FOUND` and `METHOD_NOT_ALLOWED` be added to the error-code enum?
3. Starlette 1.10 warns that `TestClient` wants `httpx2`, which is not pinned. Stay on `httpx` 0.28.1 unless architect-bot pins a replacement.
4. The CORS relaxation in ADR-002 (a cross-origin dev origin) is not implemented. There is no CORS middleware in this skeleton. The `COOKIE_SECURE` and `RATE_LIMIT_ENABLED` guards are in place. Vite's CSP is frontend.
5. Confirm TASK-007 binds the container on `0.0.0.0` and creates the restricted database role before the app is pointed at `feedback_app`.

## Suggested follow-up tasks
- TASK-006: Alembic `0001_initial` and the DDL tests. The dependency is already locked.
- TASK-007: Dockerfile `python:3.14.10-slim-trixie`, listen on `0.0.0.0`, create the restricted role, set `DATABASE_URL` to that role.
- TASK-008: CI pytest against `postgres:18.6-alpine`. `DATABASE_URL` must use a role that exists. Generate `JWT_SECRET` with `secrets.token_urlsafe(48)` (the `.env.example` placeholder must fail startup).
- TASK-009: auth. Do not log passwords, hashes, or tokens; the redaction filter is the place to extend.
- Architect: add `/api/v1/health` to the contract, or say the skeleton shape is accepted as-is.
