# TASK-005: Frontend skeleton: Vite, React, TypeScript, lint, unit tests, router check, typed API types
Owner: frontend-bot   Milestone: M0   Size: M   Attempt: 1
Blocked by: TASK-001 (DONE)   Branch: feature/TASK-005-frontend-skeleton
Reviewers: qa-bot
State: IN_REVIEW

## Goal
A Vite + React + TypeScript skeleton whose typecheck, lint, vitest, and build scripts pass on Node 24, using React Router 8.5.1 Data mode and hand-written API types from the contract. TanStack Query is deferred.

## Context (read these)
- docs/project/plan.md (TASK-005 and the TASK-012 follow-ups)
- docs/project/stack.md
- docs/project/architecture/api-contract.yaml
- docs/project/handoffs/TASK-005-handoff.md

## Scope
1. Vite ~8.3, React ~19.3, TypeScript ~6.0.3 strict, from stack.md. Node 24 is required (stack pin 24.22.1). Installed versions on the merged skeleton: Vite 8.3.5, React 19.3.1, TypeScript 6.0.3.
2. Scripts `typecheck`, `lint` (eslint + typescript-eslint), `test` (vitest), and `build` pass.
3. react-router 8.5.1 Data mode (`createBrowserRouter`), confirmed against reactrouter.com. Do not switch routers silently.
4. API types are hand-written from `api-contract.yaml`. No OpenAPI generator. TanStack Query is deferred: it is not installed in this skeleton. The pin stays in stack.md for TASK-012.
5. `package-lock.json` is committed. vitest 5.0.5.
6. Frontend follow-ups from qa-bot's PR #20 review are TASK-012, not more scope on this skeleton: extend the contract-drift test, pin `@types/node` and drop the `vite-env.d.ts` stubs, add lint rules, and consider an `engines` field.

## Evidence
- PR #20: merged 10:07:05 PM CDT as 53458a8 before QA comment; qa-bot post-merge review CHANGES_REQUESTED (one false sentence in the handoff, engines field; fix PR with frontend-bot) https://github.com/Gopi-Git001/feedback_borard/pull/20#issuecomment-6459608148.
- PR #23 (TASK-005 handoff fixes, head `90fbbd1`) merged at 10:12 PM CDT as `a6eaaaf` before qa-bot's re-review.
- PR #25 (TASK-005: handoff Node wording, head `d3c0921`) merged 10:16:01 PM CDT as `d2e2fdc`. qa-bot APPROVE. No security review needed.
- Each of those merges was by the shared Gopi-Git001 account; who pressed merge is unknown.
- TASK-005 stays IN_REVIEW. PR #25's APPROVE covers the Node wording only. The PR #20 post-merge review is CHANGES_REQUESTED, and the fix PR is with frontend-bot.

## Acceptance criteria
1. Given the frontend package, then Vite 8.3.5, React 19.3.1, and TypeScript 6.0.3 strict match stack.md, and `package-lock.json` is committed.
2. Given the four scripts, then typecheck, lint, vitest, and build pass.
3. Given the router, then it is react-router 8.5.1 Data mode (`createBrowserRouter`).
4. Given `frontend/src/api/types.ts`, then the types are hand-written from `api-contract.yaml`. TanStack Query is deferred. Node 24 is required.

## Out of scope
Pages, auth screens, the API client, and the TASK-012 follow-ups (contract-drift field renames, enum additions, status-code changes, `@types/node`, lint rules, `engines`).

## Deliverables
- PRs #20, #23, and #25 (merged)
- Handoff docs/project/handoffs/TASK-005-handoff.md
- Required reviewer: qa-bot
