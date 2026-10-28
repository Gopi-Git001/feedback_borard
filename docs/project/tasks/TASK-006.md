# TASK-006: Alembic 0001_initial from data-model.md, with DDL constraint tests on PostgreSQL
Owner: backend-bot   Milestone: M0   Size: M   Attempt: 0
Blocked by: TASK-004, TASK-003 (DB roles on main via PR #19; `scripts/init-env.sh` PR pending, not on main)
Branch: feature/TASK-006-alembic-initial-ddl-tests
Reviewers: qa-bot, security-bot
State: TODO

## Goal
The first Alembic revision creates the nine tables from data-model.md on real PostgreSQL 18.6, the DDL and privilege checks pass, and the backend refuses to start when `DATABASE_URL` is not the restricted app role.

## Context (read these)
- docs/project/plan.md (TASK-006, TASK-007, TASK-008)
- docs/project/architecture/data-model.md
- docs/project/decisions/ADR-004-security-baseline.md (R7 G1, R18; the refusal test is the one ADR-004 says is tested at TASK-006)
- docs/project/stack.md (`postgres:18.6-alpine`; `DATABASE_MIGRATION_URL` is only for the migrate service)
- db/init/01-roles.sh
- db/ops/revoke-app-on-alembic-version.sh (on main this script exits 0 and only echoes when `public.alembic_version` is absent)

## Scope
1. Revision `0001_initial` creates all nine tables, including `refresh_tokens` and `rate_limit_hits`, with their constraints and indexes, on clean `postgres:18.6-alpine`.
2. Invites store the SHA-256 of an HMAC-derived token (`token_hash`), with `UNIQUE(organization_id)` and `UNIQUE(token_hash)`. No plaintext token and no token-length column check.
3. R7 gate G1, including the two re-checks ADR-004 marks ASSUMED: default privileges for the app role, and no INSERT, UPDATE, or DELETE on `alembic_version`.
4. The migrate step runs `db/ops/revoke-app-on-alembic-version.sh` after `alembic upgrade head`. A `--require` style check fails when the table is missing, so a missing table does not silently pass.
5. Fixtures and the test database connect as a restricted role created with the same SQL as `db/init/01-roles.sh`. DDL and migrations use a separate fixture engine. CI (TASK-008) uses that same restricted role. Neither connects as a superuser.
6. R18 startup-refusal test, assumed security-bot condition. The owner role stays the image's bootstrap superuser. Acceptance of that superuser-owner risk is a relayed quote, per Orchestrator, unverified.
7. R18 condition 2 (loopback-only db, no host networking) is tested at TASK-007. Condition 4 (FORCE ROW LEVEL SECURITY for any later RLS) is the tripwire in the plan's Deferred section. Condition 5 (must change before any shared staging) is a known limit in TASK-015.

## Acceptance criteria
1. Given a clean `postgres:18.6-alpine`, when `0001_initial` is applied, then all nine tables, constraints, and indexes from data-model.md exist. Tests prove `UNIQUE(user_id,post_id)` on votes, unique `lower(email)`, memberships `UNIQUE(user_id)`, the invite uniques, CHECKs (role, type, status, counts >= 0), a composite FK blocks a cross-org vote or comment, and post delete cascades votes and comments. Upgrade and downgrade round-trip. Any DDL defect is reported to the Orchestrator (a model change needs an ADR).
2. Given G1, when the migration has been applied as the owner, then as the app role every migrated table grants SELECT, INSERT, UPDATE, and DELETE only (no TRUNCATE, REFERENCES, or TRIGGER), sequences grant USAGE only, and DDL is refused. This re-check is ASSUMED, as ADR-004 marks it.
3. Given `alembic upgrade head` and `db/ops/revoke-app-on-alembic-version.sh` in the migrate step, when the app role tries INSERT, UPDATE, or DELETE on `alembic_version`, then PostgreSQL denies each one. The revoke script is tracked with a `--require` style check: if `public.alembic_version` is missing, the step fails and does not pass by echoing and exiting 0.
4. Given the test database, then pytest does not connect as a superuser. The app-role fixture is created with the same SQL as `db/init/01-roles.sh`. A separate engine runs DDL and migrations.
5. Assumed security-bot condition. The backend refuses to start when the database role in DATABASE_URL is a superuser, has BYPASSRLS, or is the owner/migration role (ADR-004 R18 condition 3). The check runs on every start, through the real ASGI lifespan, before the port opens, and fails closed: if the role query errors, returns no row, or the db is unreachable, the process exits non-zero. No environment variable switches the check off. Test on real PostgreSQL 18 (no mock of pg_roles), with four starts of the real entry point: (a) a role created SUPERUSER NOBYPASSRLS; (b) a role created NOSUPERUSER BYPASSRLS; (c) the real owner role feedback_owner; (d) a control role created NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS. For (a), (b) and (c): exit non-zero, nothing listens on the port, /api/v1/health is unreachable, and stdout, stderr and the log file contain neither a unique sentinel password nor the full connection string (traceback and exception text included). For (d): the process starts, health is OK, and the log shows the role name only. One more run with an unreachable db also exits non-zero.

## Out of scope
Compose wiring (TASK-007), the CI workflow (TASK-008), auth (TASK-009), and enabling row-level security. `scripts/init-env.sh` is not on main; its PR is pending.

## Deliverables
- PR on the branch above titled `TASK-006: ...`, commits `TASK-006: ...`
- Handoff report docs/project/handoffs/TASK-006-handoff.md
- Required reviewers: qa-bot and security-bot
