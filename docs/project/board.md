# Board - updated 2026-10-27 (TASK-001 merged; TASK-003 dispatched)
Current milestone: M0 - Foundation (plan approved by the human 2026-10-27)

| Task | Title | Owner | State | Attempt | PR | Updated | Note |
|------|-------|-------|-------|---------|----|---------|------|
| TASK-001 | Verify and pin stack; data model; OpenAPI contract | architect-bot | DONE | 7 | PR #2 (merged) | 2026-10-27 | PR #2 merged, merge commit 54f79e4; follow-up PR for Attempt 7 text fixes is open (see PR list). |
| TASK-002 | User stories with Given/When/Then for F1-F9 | ba-bot | DONE | 2 | PR #1 (merged) + PR #3 (merged) | 2026-10-27 | PR #1 merged early, merge commit 0567ef4; Attempt 2 review fixes merged in PR #3, merge commit b495550. |
| TASK-003 | Repo layout, .gitignore, .env.example and compose `db` service | devops-bot | IN_PROGRESS | 1 | - | 2026-10-27 | Attempt 1, devops-bot, dispatched. Reviewers: qa-bot, security-bot. Blocked by: TASK-001 (DONE). Branch: feature/TASK-003-repo-layout-compose-db. |
| TASK-004 | Backend skeleton: app factory, health, settings, error format, pytest + test DB | backend-bot | TODO | 0 | - | 2026-10-27 | Planned, M0; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-001, TASK-003. |
| TASK-005 | Frontend skeleton: Vite, React, TypeScript, lint, unit tests, router check, typed API types | frontend-bot | TODO | 0 | - | 2026-10-27 | Planned, M0; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-001, TASK-003. |
| TASK-006 | Alembic 0001_initial from data-model.md, with DDL constraint tests on PostgreSQL | backend-bot | TODO | 0 | - | 2026-10-27 | Planned, M0; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-004. |
| TASK-007 | Dockerfiles and compose wiring: db, backend, frontend | devops-bot | TODO | 0 | - | 2026-10-27 | Planned, M0; approved; dispatch when blockers are DONE. Reviewers: qa-bot, security-bot. Blocked by: TASK-004, TASK-005, TASK-006. |
| TASK-008 | GitHub Actions CI: backend and frontend jobs | devops-bot | TODO | 0 | - | 2026-10-27 | Planned, M0; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-004, TASK-005. |
| TASK-009 | Backend auth: signup and login with Argon2id and JWT | backend-bot | TODO | 0 | - | 2026-10-27 | Planned, M0; approved; dispatch when blockers are DONE. Reviewers: qa-bot, security-bot. Blocked by: TASK-006. |
| TASK-010 | Backend auth session: refresh, logout, me, current-user guard, rate limits | backend-bot | TODO | 0 | - | 2026-10-27 | Planned, M0; approved; dispatch when blockers are DONE. Reviewers: qa-bot, security-bot. Blocked by: TASK-009. |
| TASK-011 | Tenancy model: tenant context, org-scoped data access, role guards, two-org test fixtures | backend-bot | TODO | 0 | - | 2026-10-27 | Planned, M0; approved; dispatch when blockers are DONE. Reviewers: qa-bot, security-bot. Blocked by: TASK-010. |
| TASK-012 | Base UI shell: routing, layout, auth session provider, route guards, API client | frontend-bot | TODO | 0 | - | 2026-10-27 | Planned, M0; approved; dispatch when blockers are DONE. Reviewers: qa-bot, security-bot. Blocked by: TASK-005. |
| TASK-013 | Playwright harness and smoke test | frontend-bot | TODO | 0 | - | 2026-10-27 | Planned, M0; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-005, TASK-007. |
| TASK-014 | CI job: compose up and Playwright e2e | devops-bot | TODO | 0 | - | 2026-10-27 | Planned, M0; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-007, TASK-008, TASK-013. |
| TASK-015 | Release notes M0 | docs-bot | TODO | 0 | - | 2026-10-27 | Planned, M0; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-011, TASK-012, TASK-014. |
| TASK-016 | Backend organizations: create and get current | backend-bot | TODO | 0 | - | 2026-10-27 | Planned, M1; approved; dispatch when blockers are DONE. Reviewers: qa-bot, security-bot. Blocked by: TASK-011. |
| TASK-017 | Backend invites: get-or-create token, public preview, accept | backend-bot | TODO | 0 | - | 2026-10-27 | Planned, M1; approved; dispatch when blockers are DONE. Reviewers: qa-bot, security-bot. Blocked by: TASK-016. |
| TASK-018 | Backend posts: create and get | backend-bot | TODO | 0 | - | 2026-10-27 | Planned, M1; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-011. |
| TASK-019 | Backend board: list with sort and filters | backend-bot | TODO | 0 | - | 2026-10-27 | Planned, M1; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-018. |
| TASK-020 | Backend votes: toggle upvote | backend-bot | TODO | 0 | - | 2026-10-27 | Planned, M1; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-018. |
| TASK-021 | Backend comments: list and create | backend-bot | TODO | 0 | - | 2026-10-27 | Planned, M1; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-018. |
| TASK-022 | Backend status change (admin) | backend-bot | TODO | 0 | - | 2026-10-27 | Planned, M1; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-018. |
| TASK-023 | Backend post delete (admin) | backend-bot | TODO | 0 | - | 2026-10-27 | Planned, M1; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-018. |
| TASK-024 | UI: sign up and log in screens | frontend-bot | TODO | 0 | - | 2026-10-27 | Planned, M1; approved; dispatch when blockers are DONE. Reviewers: qa-bot, security-bot. Blocked by: TASK-012. |
| TASK-025 | UI: create organization (onboarding) | frontend-bot | TODO | 0 | - | 2026-10-27 | Planned, M1; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-024. |
| TASK-026 | UI: invite link (admin) and join page | frontend-bot | TODO | 0 | - | 2026-10-27 | Planned, M1; approved; dispatch when blockers are DONE. Reviewers: qa-bot, security-bot. Blocked by: TASK-025. |
| TASK-027 | UI: board with sort display, filters and empty states | frontend-bot | TODO | 0 | - | 2026-10-27 | Planned, M1; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-012. |
| TASK-028 | UI: new post form and post detail page | frontend-bot | TODO | 0 | - | 2026-10-27 | Planned, M1; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-027. |
| TASK-029 | UI: upvote control | frontend-bot | TODO | 0 | - | 2026-10-27 | Planned, M1; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-028. |
| TASK-030 | UI: comments list and form | frontend-bot | TODO | 0 | - | 2026-10-27 | Planned, M1; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-028. |
| TASK-031 | UI: admin status selector | frontend-bot | TODO | 0 | - | 2026-10-27 | Planned, M1; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-028. |
| TASK-032 | UI: admin delete with confirmation | frontend-bot | TODO | 0 | - | 2026-10-27 | Planned, M1; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-028. |
| TASK-033 | E2E: owner journey (sign up, org, invite, post, vote, comment, status) | frontend-bot | TODO | 0 | - | 2026-10-27 | Planned, M1; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-014, TASK-016, TASK-017, TASK-019, TASK-020, TASK-021, TASK-022, TASK-024, TASK-026, TASK-028, TASK-029, TASK-030, TASK-031. |
| TASK-034 | E2E: permissions, isolation and failure paths | frontend-bot | TODO | 0 | - | 2026-10-27 | Planned, M1; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-033, TASK-023, TASK-032. |
| TASK-035 | Security review of auth, tenancy, invites and secrets | security-bot | TODO | 0 | - | 2026-10-27 | Planned, M1; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-034. |
| TASK-036 | README: how to run, test and troubleshoot | docs-bot | TODO | 0 | - | 2026-10-27 | Planned, M1; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-034. |
| TASK-037 | M1 acceptance run from a clean clone | qa-bot | TODO | 0 | - | 2026-10-27 | Planned, M1; approved; dispatch when blockers are DONE. Reviewers: qa-bot, Orchestrator (qa-bot cannot review its own task). Blocked by: TASK-034, TASK-035, TASK-036. |
| TASK-038 | Release notes M1 | docs-bot | TODO | 0 | - | 2026-10-27 | Planned, M1; approved; dispatch when blockers are DONE. Reviewers: qa-bot. Blocked by: TASK-037. |
| TASK-039 | Display name at signup and approved auth extras in the stories | ba-bot | DONE | 2 | PR #4 (merged) | 2026-10-27 | PR #4 merged, merge commit 2240765. |
| TASK-040 | Align stories with the revised auth and invite design | ba-bot | IN_REVIEW | 5 | PR #5 (merged) + PR #6 (open) | 2026-10-27 | PR #5 merged, merge commit 057fb19; follow-up PR #6 open. |

Counts: M0 = 17 tasks (3 DONE, 1 in review, 1 in progress, 12 TODO), including follow-ups TASK-039 and TASK-040. M1 = 23 tasks (all TODO). Total 40. TASK-001 is merged and the plan is approved. TASK-003 is dispatched. Other tasks stay TODO until their blockers are DONE.

## Needs human
- None right now. Approved 2026-10-27: brief, stack, plan; TypeScript 6.0.3; extra /auth/refresh and /auth/logout; display name at signup; rate limiting kept; standing OK for the Orchestrator to merge PRs that pass qa-bot review (and security-bot where required).
## Blocked
- None. Open follow-ups, not blockers: TASK-001 Attempt 7 text fixes (see PR list); TASK-040 follow-up PR #6.
## Recently done
- TASK-001, TASK-002 and TASK-039.
## Log
- 2026-10-27: TASK-001 set DONE (PR #2 merged, merge commit 54f79e4; Attempt 7 follow-up open). TASK-002 set DONE from its merged PRs (PR #1 merge commit 0567ef4; PR #3 merge commit b495550). TASK-039 set DONE (PR #4 merged, merge commit 2240765). TASK-040 set IN_REVIEW (PR #5 merged, merge commit 057fb19; follow-up PR #6 open). TASK-003 dispatched IN_PROGRESS (Attempt 1, devops-bot).
