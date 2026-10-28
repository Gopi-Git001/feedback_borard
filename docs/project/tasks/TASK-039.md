# TASK-039: Display name at signup and approved auth extras in the stories
Owner: ba-bot   Milestone: M0   Size: S   Attempt: 2
Blocked by: none (the contract on PR #2 was used as a reference)   Branch: fix/TASK-039-display-name-and-auth-extras
Note: this spec was written retroactively by ba-bot at the Orchestrator's request (TASK-040). The original instructions came from the Orchestrator's message; the work was delivered in PR #4 (merged to main) and its handoff is docs/project/handoffs/TASK-039-handoff.md.

Superseded in part by TASK-040 (PR #5): F1-2 was later split (F1-2 now has 6 criteria: #1 refresh and rotation, #2 invalid cookie 401, #3 7-day cap, #4 logout, #5 sign-up/login 429, #6 refresh 429; session hardening moved to F1-3), the invite preview became POST /invites/preview with the token in the body and the link /join#<token> (F3-1, F3-2), and there is no login lockout. The text below is TASK-039 as delivered.

## Goal
Bring the TASK-002 stories in line with what the human approved after the stories were first written: a required display name at signup, rate limiting, and the refresh and logout endpoints.

## Context (read these)
- docs/project/stories/ (TASK-002 stories, PR #1 and PR #3)
- api-contract.yaml on the TASK-001 branch (PR #2)
- Orchestrator message for TASK-039 and the qa-bot suggestions

## Scope
- F1-1 and E2E-1 (and every other story that signs up or names a user): signup takes email, password and display name; add a validation criterion (1-80 characters per the contract; the Orchestrator's first wording said 1-60) and show the display name wherever a user is named.
- Rate limiting (429) on login, signup, refresh and invite preview, and the extra endpoints /auth/refresh and /auth/logout, as a new story F1-2 and criterion 6 of F3-1; thresholds marked ASSUMED.
- F9-1: add a Cancel criterion (qa-bot suggestion).
- TASK-002 handoff: reference PR #3.
- Do not change scope beyond these items; contract-versus-request mismatches go to Open questions in the handoff.

## Acceptance criteria
- Given the signup story, then a criterion covers a valid display name (1 and 80 characters accepted) and an invalid one (empty, spaces-only, 81 characters).
- Given any story that names a user (post author, comment author, journey steps), then the display name is shown, never the email.
- Given login, signup, refresh and invite preview, then a Given/When/Then criterion covers the 429 response with code RATE_LIMITED, and every threshold is marked ASSUMED.
- Given F9-1, then a Cancel criterion exists and the existing criteria keep their numbers.
- Given the TASK-002 handoff, then it links PR #3.

## Out of scope
Code, changing brief.md, plan.md or board.md, the contract.

## Deliverables
- PR titled `TASK-039: ...` on the branch above (PR #4, merged)
- Handoff report docs/project/handoffs/TASK-039-handoff.md
- Use your skills: write-user-stories, review-story-readiness, write-handoff-report
