# TASK-001: Verify and pin stack; data model; OpenAPI contract
Owner: architect-bot   Milestone: M0   Size: M   Attempt: 1
Blocked by: none   Branch: feature/TASK-001-stack-and-contracts

## Goal
docs/project/stack.md with verified current stable pinned versions, an ADR, the data model, and the OpenAPI contract, so frontend and backend can build in parallel.

## Context (read these)
- docs/project/brief.md (all features F1-F9 and the ASSUMED list)
- TEAM-CONVENTIONS.md (github.com/Gopi-Git001/Saas_Bot) sections 1, 3, 5

## Scope
1. stack.md: the stack is PRE-APPROVED and fixed (FastAPI, PostgreSQL, SQLAlchemy + Alembic, React + TypeScript with Vite, built-in email/password + JWT, pytest, Playwright, docker compose, GitHub Actions). Do NOT compare alternatives. Only verify from official sources the current stable version of each (plus Python, Node, passlib/argon2 or bcrypt choice, a JWT library, Pydantic, Uvicorn, React Router, a data-fetching lib if proposed), record last release date, and pin major.minor. Reject anything beta/RC/EOL. Include a short ADR-001 for the pinned set and an ADR-002 for password hashing and JWT approach (access token lifetime, where the token is stored in the browser, and why).
2. architecture/data-model.md: tables, columns, constraints, indexes for users, organizations, memberships (role admin|member), invites, posts (type idea|bug, status New|Planned|In Progress|Done), votes (UNIQUE user_id+post_id), comments. Every tenant table carries organization_id; state how tenant isolation is enforced.
3. architecture/api-contract.yaml (OpenAPI 3.x): auth (signup, login, me), organizations (create, get current), invites (create, preview, accept), posts (list with sort by votes + filter type/status, create, get, update status [admin], delete [admin]), votes (add, remove), comments (list, create). Define error format and status codes, 401/403/404 rules (404 not 403 for other-org resources), pagination.

## Acceptance criteria
- Given the stack.md, then every row has version, last-release date, and an official source link, and no pre-release versions.
- Given the data model, then votes are unique per user+post and every tenant table has organization_id.
- Given the OpenAPI file, then it validates with an OpenAPI linter and covers every feature F1-F9.
- Given a cross-org request, then the contract specifies a 404 response.

## Out of scope
Any application code, docker or CI files.

## Deliverables
- PR on the branch above titled `TASK-001: ...`, commits `TASK-001: ...`
- Handoff report docs/project/handoffs/TASK-001-handoff.md (format in TEAM-CONVENTIONS.md section 5)
- Use your skills: tech-research, write-adr, design-data-model, design-api-contract, write-handoff-report
