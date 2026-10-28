# TASK-004: Backend skeleton: app factory, health, settings, error format, pytest + test DB
Owner: backend-bot   Milestone: M0   Size: M   Attempt: 1
Blocked by: TASK-001 (DONE)   Branch: feature/TASK-004-backend-skeleton
Reviewers: qa-bot
State: IN_REVIEW

## Goal
A uv backend on Python 3.14 that serves `GET /api/v1/health`, refuses to start when `JWT_SECRET` is missing or too short, returns one JSON error shape, and runs pytest against real PostgreSQL 18.

## Context (read these)
- docs/project/plan.md (TASK-004)
- docs/project/stack.md (backend pins and the Attempt 2 tooling addendum)
- docs/project/decisions/ADR-002-password-hashing-and-jwt.md
- docs/project/decisions/ADR-004-security-baseline.md (section 3, P10-2; R18 condition 3, the startup refusal)
- docs/project/architecture/api-contract.yaml
- docs/project/handoffs/TASK-004-handoff.md

## Scope
1. uv project on Python 3.14 with the stack.md pins and a lock file. Do not invent versions. Attempt 2 pins: uv 0.13.6, ruff ~=0.17.3, mypy ~=2.4.0, python:3.14.10-slim-trixie.
2. `GET /api/v1/health`.
3. The app refuses to start if `JWT_SECRET` is missing or shorter than 32 characters.
4. Every error uses `{error:{code,message,details}}`. FastAPI 422 is remapped to 400 `VALIDATION_ERROR`.
5. pytest runs against real PostgreSQL 18. Backend lint and type checks run clean.
6. P10-2 scope: a per-operation 415 on the eight body operations, written into ADR-004 section 3 by architect-bot; table-driven from `api-contract.yaml`; exclude `PATCH /posts/{id}/status`; cover undefined edit routes with JSON and `text/plain` bodies. Those undefined routes (the contract has no post or comment edit endpoint) answer 404 or 405, not 415.
7. R18 startup refusal, reported by security-bot and not yet verified. On every start, through the real ASGI lifespan, before the port opens, the process fails closed. No environment variable switches the check off. It refuses to start when the role in `DATABASE_URL` is a superuser, has `BYPASSRLS`, or is the owner or migration role. Test on real PostgreSQL 18 with a role created `SUPERUSER NOBYPASSRLS`, a role created `NOSUPERUSER BYPASSRLS`, the owner role `feedback_owner`, and a clean control role (`NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS`). The first three exit non-zero and print neither a password nor the full connection string. The control role starts. An unreachable database also exits non-zero. Delivered in `fix/TASK-004-logging-followup` after merged PR #26 (`16554277`).

## Evidence
- PR #22: https://github.com/Gopi-Git001/feedback_borard/pull/22 merged 10:08:56 PM CDT as `364d9b9` (head `5b11647`) before the QA comment. Merged by the shared Gopi-Git001 account; who pressed merge is unknown.
- PR #26 (`TASK-004: review fixes`) merged as `16554277` after qa-bot APPROVE and security-bot PASS, both on head `732451b`. TASK-004 stays IN_REVIEW. The R18 refusal follow-up is in progress on `fix/TASK-004-logging-followup`.

## Acceptance criteria
1. Given the uv project, then it uses Python 3.14, the stack.md pins, and a committed lock file.
2. Given a running database, when `GET /api/v1/health` is called, then the response is OK.
3. Given a missing or too-short `JWT_SECRET`, when the process starts, then it exits non-zero and does not print the secret.
4. Given a validation failure, then the body is `{error:{code,message,details}}` and FastAPI 422 is 400 `VALIDATION_ERROR`.
5. Given pytest, then it runs against real PostgreSQL 18, and ruff and mypy are clean.
6. Given an undefined post or comment edit route, when the body is JSON and when it is `text/plain`, then the answer is 404 or 405, not 415. `PATCH /posts/{id}/status` is excluded from that undefined-route check.
7. Given a real PostgreSQL 18 start through the ASGI lifespan, before the port opens, then a superuser, a `BYPASSRLS` role, and `feedback_owner` each exit non-zero with no password and no connection string in the output. A clean control role starts. An unreachable database exits non-zero. No environment variable switches the check off.

## Out of scope
Alembic migrations (TASK-006), Dockerfiles (TASK-007), auth endpoints (TASK-009).

## Deliverables
- PR https://github.com/Gopi-Git001/feedback_borard/pull/22 (merged)
- Handoff docs/project/handoffs/TASK-004-handoff.md
- Required reviewer: qa-bot
