# Handoff: TASK-039 Display name at signup and auth extras in stories
Bot: ba-bot   Attempt: 1   PR: to be set when opened   Branch: fix/TASK-039-display-name-and-auth-extras

Open questions: see the "Open questions" section below (9 items, all ASSUMED or contract mismatches).

## Summary
Sign-up now takes email, password and a required display name (1-80 characters, from the API contract) in F1-1 and E2E-1; posts and comments show the author's display name, never the email (F4-1, F6-1, E2E-1). A new story F1-2 covers token refresh, log out and the 429 rate limit on sign-up, login and refresh; the invite-preview rate limit is criterion 6 of F3-1. F9-1 got a Cancel criterion, and the TASK-002 handoff now links PR #3. The TASK-039 spec file was not found in the repo (no docs/project/tasks/TASK-039.md on any origin branch); the instructions came from the Orchestrator message and its relayed summary. The TEAM-CONVENTIONS.md file could not be fetched (private repo), so this report uses the format in the write-handoff-report skill, which cites section 5.

## Acceptance criteria
| Criterion | Status (met / not met) | Test that proves it |
|-----------|------------------------|---------------------|
| 1. Sign-up takes email, password and display name; display name validation (empty, spaces-only, 81 chars; 1 and 80 accepted) | met | F1-1 #1 and #3; E2E-1 #1, #3, #9 |
| 1. Display name shown wherever a user is named (post and comment authors, journey steps) | met | F4-1 #1 and #5; F6-1 #1; E2E-1 #1, #4, #6; F3-1 #4 (Dan); F2-1 UI note |
| 2. Rate limit 429 on login, sign-up, refresh | met | F1-2 #4 and #5 |
| 2. Rate limit 429 on invite preview | met | F3-1 #6 |
| 2. Refresh and logout criteria, as far as the contract defines them | met, see Decisions on logout | F1-2 #1, #2, #3 |
| 3. TASK-002 handoff references PR #3 | met | TASK-002-handoff.md line 4 ("Review history") |
| 4. F9-1 Cancel criterion, within 6 criteria, nothing lost | met | F9-1 #6 (criteria 1-5 unchanged: cascade #1, member 403 #2, cross-org 404 #3, repeat delete 404 #4, 401 #5) |
| 5. This handoff in the section 5 format | met | this file |

## Files changed
Only under docs/project/stories/ and docs/project/handoffs/:
- docs/project/stories/F1-1-signup-login.md (display name in criteria 1-3, rules, UI, data; out of scope points to F1-2)
- docs/project/stories/F1-2-session-and-rate-limits.md (NEW)
- docs/project/stories/F2-1-organization-create-join.md (one UI note: sign-up includes display name)
- docs/project/stories/F3-1-invite-link.md (criterion 6 invite-preview rate limit; Dan's display name)
- docs/project/stories/F4-1-posts.md (author shown by display name)
- docs/project/stories/F6-1-comments.md (author shown by display name)
- docs/project/stories/F9-1-delete-post.md (Cancel criterion 6)
- docs/project/stories/E2E-1-owner-journey.md (display names in steps 1, 3, 4, 6, 9)
- docs/project/handoffs/TASK-002-handoff.md (one "Review history" line)
- docs/project/handoffs/TASK-039-handoff.md (NEW)
Not touched: brief.md, plan.md, board.md, code, F5-1, F7-1, F8-1.

## How to test locally
Docs-only, nothing to run. Review: (1) each changed criterion can be turned into a test with the stated values; (2) every ASSUMED item below is marked ASSUMED in the story; (3) values from the contract match `git show origin/feature/TASK-001-stack-and-contracts:docs/project/architecture/api-contract.yaml`; (4) `git diff --name-only origin/main` lists only docs/project/stories/ and docs/project/handoffs/ files.

## Test results
No automated tests (docs task). I re-ran the review-story-readiness checklist on each changed story myself (not an independent review; qa-bot reviews). Criteria counted with a script; no `QUESTION:` item remains in any story.

| Story | Ready? | Gaps / questions |
|-------|--------|------------------|
| F1-1 signup-login (6 criteria) | READY | Display name spaces-only = empty is ASSUMED (Q2). #3 bundles four validation groups, as F4-1 #2 does. Q1 brief gate |
| F1-2 session-and-rate-limits (5 criteria) NEW | READY | Threshold 10 per 60 s per IP ASSUMED (Q3); 429 body and header are contract-sourced; no role permission case exists for public auth endpoints, the 401 on refresh (#2) is the access case; logout limit (Q5); test-environment rate limits (Q4); not in brief.md (Q1) |
| F2-1 organization-create-join (6) | READY | Only a UI note changed; criteria unchanged |
| F3-1 invite-link (6) | READY | Preview threshold ASSUMED (Q3); preview is the invitee-side page inside the admin-sharing story, kept here because the contract tags it F2 and F3 |
| F4-1 posts (6) | READY | Criteria unchanged in count; author by display name |
| F6-1 comments (6) | READY | Criteria unchanged in count; author by display name |
| F9-1 delete-post (6) | READY | Cancel button text and dialog are ASSUMED (already in story) |
| E2E-1 owner-journey (9) | READY | Above 6 on purpose (justified in the story); header as display-name location ASSUMED |

Definition of Ready boxes are checked for all rows except "traces to an APPROVED brief" (conditional on the brief approval, TASK-002 Q1) and, for F1-2, "traces to brief": it traces to F1 plus the human approval relayed by the Orchestrator (Q1). The "no conflict with the API contract" box was checked against api-contract.yaml on the TASK-001 branch, which is not on main yet; the changed stories carry a "Contract check (TASK-039)" line.

## Decisions made (and why)
- **Display name limits: 1-80, not 1-60.** The contract (SignupRequest, User, UserPublic) and data-model.md say 1-80, so I used them as instructed. 61 characters is therefore valid; the boundary tests are 80 accepted and 81 rejected.
- **Display name trimming is marked ASSUMED.** data-model.md says "length 1-80 after trim", but the contract's trimming note names only title, description, body and name. Spaces-only is treated as empty (ASSUMED) until the contract says so.
- **F1-1 stays at 6 criteria.** Display name validation is added to criterion 3 (the existing bundle) instead of a 7th criterion. Session, logout and rate limits went to the new F1-2, as the Orchestrator allowed.
- **Logout criterion follows the contract, not the request wording.** The request said "after logout the refresh token no longer works". The contract and ADR-002 say logout only clears the cookie, tokens are stateless, and a refresh token copied before logout stays valid up to 7 days. So F1-2 #3 tests: 204, cookie cleared, a later refresh without the cookie gives 401, repeat logout gives 204. The stolen-token limit is written as a known limit in the story. I did not claim server-side revocation.
- **Refresh criteria** use the contract: 900-second access token, the cookie is replaced, 401 for missing, invalid or expired (7 days). I did not add a criterion that the old, rotated refresh token is rejected, because the stateless design does not do that.
- **Rate limit format is contract-sourced** (429, code RATE_LIMITED, message "Too many requests. Try again later.", Retry-After in seconds). The numeric threshold is ASSUMED: 10 requests per rolling 60 seconds per IP, per endpoint, successful or not. One number for all four endpoints to keep assumptions few.
- **Invite preview** is the contract's public GET /invites/{token}: returns only the organization name, 404 for an unknown token (already covered by F2-1 #4), 429 rate limited. Added as F3-1 #6 (F3-1 had 5 criteria).
- **Endpoint paths** are named only in F1-2/F3-1 context where the Orchestrator named them; criteria are still written as user and response behaviour.
- **F9-1 Cancel** appended as #6 so existing references to F9-1 #2-#5 stay valid.
- **Footers of unchanged stories** (F5-1, F7-1, F8-1, and the old footer lines in changed stories) still say the contract did not exist; I added a contract-check line only to the changed stories. 401 is now contract-confirmed (Unauthorized response), the old ASSUMED marker is left in place.
- **Not added:** author display name on the board row in F7-1 (not requested; the contract's Post object includes the author, so it is available).

## Open questions
1. **brief.md does not list the approved additions** (display name, rate limiting, refresh, logout). I cannot edit brief.md. Orchestrator: update the brief and change log, or confirm that this handoff plus the contract is the record. Also still open: TASK-002 Q1 (brief approval).
2. **Display name trimming** (ASSUMED): spaces-only treated as empty. data-model.md says trimmed, the contract's trimming note omits display_name. architect-bot to align the contract note.
3. **Rate-limit threshold** (ASSUMED): 10 per rolling 60 seconds per IP per endpoint for sign-up, login, refresh and invite preview. The contract and ADR-002 give no number. Confirm or give the real values; whether failed and successful requests both count, and whether invalid invite tokens count, are ASSUMED too.
4. **Test environments** (ASSUMED): the Playwright run signs up several users from one IP, so rate limits must be configurable or relaxed for tests. Not specified anywhere; backend-bot and qa-bot need to know.
5. **Logout has a 429 in the contract** but the approved scope lists only login, sign-up, refresh and invite preview. F1-2 does not test a logout limit. Confirm which is right.
6. **429 user-facing text** in the UI ("try again later") is ASSUMED; the API message is contract-sourced.
7. **UI texts newly ASSUMED:** "Log out" label, silent renewal and redirect to the login form after a failed refresh or logout, the app header as the place that shows my display name, the "Cancel" button text in F9-1.
8. **Display names are not unique** (ASSUMED); two members may share one, which makes two authors look identical on the board. Confirm.
9. **Logout does not revoke tokens** (contract and ADR-002 limit, not a story question): an issued access token lives up to 15 minutes and a stolen refresh token up to 7 days. Confirm the human accepts this for the MVP; it is already a follow-up in ADR-002.

## Suggested follow-up tasks
- Orchestrator: update brief.md (display name, rate limiting, refresh, logout) and put Q2, Q3, Q5, Q8, Q9 in front of the human.
- architect-bot: align the contract's trimming note with data-model.md for display_name, and decide the logout 429.
- backend-bot and qa-bot: make rate limits configurable for the e2e run; derive tests from F1-2 and F3-1 #6.
- ba-bot (small): refresh the contract footers of F5-1, F7-1 and F8-1 once api-contract.yaml is on main; optionally show the author display name on the board row (F7-1).
