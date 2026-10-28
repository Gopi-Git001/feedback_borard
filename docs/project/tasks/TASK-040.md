# TASK-040: Align stories with the revised auth and invite design
Owner: ba-bot   Milestone: M0   Size: M   Attempt: 1
Blocked by: PR #2 (architect-bot's revised design, still under review)   Branch: fix/TASK-040-auth-and-invite-redesign
Note: this spec was written retroactively by ba-bot at the Orchestrator's request, from the Orchestrator's TASK-040 message and the local instruction that relayed it.

## Goal
Make the stories match the revised design in api-contract.yaml, ADR-002, ADR-003 and the TASK-001 handoff (Attempt 2 and 2b) on PR #2, so the implementation and tests are written against one version.

## Context (read these)
- docs/project/stories/ (F1-1, F1-2, F2-1, F3-1, E2E-1)
- On PR #2: docs/project/architecture/api-contract.yaml, docs/project/decisions/ADR-002 and ADR-003, docs/project/handoffs/TASK-001-handoff.md
- docs/project/brief.md (approved additions)

## Scope
- F1-2: logout revokes the whole token family; refresh rotates; reuse of an old refresh token gives 401 and revokes the family; session ends 7 days after login; refresh and logout need the X-Requested-With header and a valid Origin; no 429 on logout; split into F1-3 if more than 6 criteria are needed.
- F3-1: invite link is /join#<token>; preview and accept are POST /invites/preview and /invites/accept with {token} in the body; only a hash is stored; the admin sees the same link every time; no token in any request URL; split into F3-2 if needed.
- F2-1: joining uses POST preview and accept; the token is held in sessionStorage while the user signs up or logs in; a bad or missing token shows "Invite link is invalid".
- E2E-1: step 3 uses /join#<token>; add a check that no request URL contains the token; run with RATE_LIMIT_ENABLED=false.
- F1-1: remove the out-of-scope line that conflicts with display name and the approved extras; display name 1-80, trimmed.
- Handoffs: TASK-039 says the repo is public, not private; keep Q11 (403 ORG_REQUIRED) as a leftover; keep ASSUMED labels.
- Mark F1-2, F3-1, F2-1, E2E-1 (and any new F1-3 or F3-2) as touching authentication, so security-bot reviews them.
- Add the missing docs/project/tasks/TASK-039.md and TASK-040.md.
- F4-1 to F9-1 are not changed.

## Acceptance criteria
- Given F1-2 and its split F1-3, then criteria cover rotation, reuse detection, the 7-day cap, logout revoking the family, the missing-header and bad-Origin 403, and no 429 on logout.
- Given F3-1 and F3-2, then criteria cover the /join#<token> link, POST preview and accept, hash-only storage, the same link every time, and no token in any request URL.
- Given F2-1, then criteria cover POST preview and accept and the "Invite link is invalid" message, and the sessionStorage flow is specified (F3-2 criterion 4).
- Given E2E-1, then step 3 uses /join#<token> and a criterion checks that no request URL contains the token.
- Given every changed story, then it has 3-6 criteria (the journey is the justified exception), no QUESTION: items, and the security-review line.
- Given the handoff, then it states the PR #2 head checked, lists conflicts with the Orchestrator's list, and keeps all ASSUMED labels.

## Out of scope
Code, brief.md, plan.md, board.md, api-contract.yaml, ADRs, F4-1 to F9-1.

## Deliverables
- PR titled `TASK-040: ...` on the branch above (do not merge)
- Handoff report docs/project/handoffs/TASK-040-handoff.md
- Use your skills: write-user-stories, review-story-readiness, write-handoff-report
