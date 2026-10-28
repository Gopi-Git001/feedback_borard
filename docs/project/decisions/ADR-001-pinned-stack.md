# ADR-001: Pinned technology stack for Team Feedback Board
Status: Accepted. Basis: Gopi approved the brief, stack and plan in chat on 2026-10-27 (relayed by the Orchestrator; reviewers have not verified it). It does not approve R7, A4-4 for the register rows that are not re-confirmed, or any rule labelled ASSUMED (ADR-004 section 7). Review state of the specs: ADR-004 section 7.
Date: 2026-10-27   Deciders: architect-bot (proposes), Orchestrator (approves)

## Context
The brief pre-approves the stack: FastAPI, PostgreSQL, SQLAlchemy + Alembic, React + TypeScript (Vite), built-in email/password + JWT, pytest, Playwright, docker compose, GitHub Actions. TASK-001 asks only for verified, pinned current stable versions, so frontend-bot and backend-bot build against the same set. Nothing may be beta, RC or EOL.

## Options considered
Alternatives to the stack were out of scope. The only real choices were *which stable line* of a few components:
1. **Python 3.14 vs 3.15.** Both stable. 3.15 is 18 days old; 3.14 has ten patch releases. Chose 3.14.
2. **Node 24 LTS vs Node 26.** 26 is "Current" until it becomes LTS on 2026-10-28; production should use LTS. Chose 24 (LTS since 2025-10-28; now Maintenance LTS per endoflife.date, supported to 2028-04-30). A Node 26 review is due in a later task.
3. **TypeScript 7.0.2 vs 6.0.3.** 7.0.2 is the latest stable, but typescript-eslint 8.72.1 only supports `<6.1.0`. Chose 6.0.3 so lint works. **Confirmed** (Orchestrator message 2026-10-27, relayed from the human).
4. **SQLAlchemy 2.1 vs 2.0.** 2.1.6 is current stable (GA 2026-09-24); 2.0.55 is the previous line. Chose 2.1.6 (current stable), 2.0.55 as fallback.
5. **Router package.** `react-router` 8.5.1 (single package) vs `react-router-dom` 7.18.5 (7.x line). Chose `react-router` 8.5.1, used in **Data mode** (`createBrowserRouter` from `react-router`, `RouterProvider` from `react-router/dom`). `react-router-dom` is not installed. (Earlier text called this "library mode"; reactrouter.com has no such mode.)
6. **Test HTTP client (attempt 12, ARCHITECT DECISION, not approved by Gopi).** `httpx` 0.28.1 (2024-12-06) vs `httpx2` 2.16.0 (2026-10-21, Pydantic's continuation of HTTPX). Starlette 1.10.0 documents plain httpx as deprecated for `TestClient` and warns about it. Chose `httpx2` `~=2.16.0`, tests only; backend-bot applies it in a follow-up. Details, sources and the re-check date (2026-11-10) are in stack.md note 3.

## Decision
Adopt the full pinned set in `docs/project/stack.md` (verified 2026-10-27). Headline pins:
Python 3.14 (3.14.10), PostgreSQL 18 (18.6), Node 24 LTS (24.22.1), FastAPI ~=0.162.0, Pydantic ~=2.14.1, Uvicorn ~=0.54.0, SQLAlchemy ~=2.1.6, Alembic ~=1.20.1, psycopg ~=3.3.6, React ~19.3.1, TypeScript ~6.0.3, Vite ~8.3.5, React Router ~8.5.1, @playwright/test ~1.64.1, pytest ~=9.2.0, Docker Compose v5.6.1, GitHub Actions on `ubuntu-24.04` with checkout/setup-python/setup-node/upload-artifact at v7. Password hashing and JWT are in ADR-002.
Rules: pin major.minor with lock files; no pre-release versions; a pin change needs a new ADR.

## Consequences
- Easier: one verified set for all bots; CI and docker use the same versions (`postgres:18.6-alpine`, Node 24, Python 3.14).
- Harder / risks: SQLAlchemy 2.1 and pytest 9.2 are very new (days to weeks old); a regression there is possible. Fallback for SQLAlchemy: 2.0.55 (Alembic 1.20.1 supports >=2.0). FastAPI and Uvicorn are 0.x, so minor bumps can break: pin `~=` to the minor and upgrade deliberately.
- Freshness exceptions (older than 12 months but the latest stable and not deprecated): argon2-cffi 25.1.0 and email-validator 2.3.0 (httpx 0.28.1 was a third exception until attempt 12; it is replaced by httpx2, see item 6 and stack.md note 3). See stack.md notes 1-3.
- TypeScript 7 upgrade is blocked until typescript-eslint supports it; revisit with a new ADR.
- PostgreSQL 18 gives native `uuidv7()` (mentioned in the 18.6 release notes), used for primary keys in data-model.md.
- Cost: all components are free and open source; no paid service.
- Fallbacks: Python 3.13 (security-only), Node 22 (LTS), PostgreSQL 17 (17.11).

## Sources (verified 2026-10-27)
See the per-row URLs in `docs/project/stack.md`. Main ones: https://www.python.org/downloads/ , https://www.postgresql.org/support/versioning/ , https://nodejs.org/en/about/previous-releases , https://pypi.org/pypi/<package>/json , https://registry.npmjs.org/<package>/latest , https://github.com/docker/compose/releases , https://github.com/actions/runner-images , https://endoflife.date (cross-check).
