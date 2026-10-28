# Handoff: TASK-002 User stories with testable acceptance criteria for F1-F9
Bot: ba-bot   Attempt: 2   PR: https://github.com/Gopi-Git001/feedback_borard/pull/1   Branch: feature/TASK-002-user-stories

Review history: the Attempt 2 fixes (qa-bot review of PR #1, comment 6457628659) were merged via PR #3: https://github.com/Gopi-Git001/feedback_borard/pull/3

Open questions: see the "Open questions" section below. 10 items: 1 resolved (Q2); 9 are ASSUMED items that need an answer or confirmation (Q1 is the gate: brief approval).

## Summary
Ten story files in docs/project/stories/: one per feature F1-F9 and one end-to-end journey (E2E-1). Each has Given/When/Then criteria with concrete values, covering happy path, validation, duplicate email, wrong password, invalid invite, invalid filter value, 403 for members on admin actions, 404 for cross-organization access, empty board and newest-first tie-break. This attempt fixes the seven findings of the qa-bot Attempt 1 review (PR comment 6457628659). All ten stories are READY (conditional on brief approval, Q1).

## Acceptance criteria
| Criterion | Status (met / not met) | Test that proves it |
|-----------|------------------------|---------------------|
| Each feature F1-F9 has a story with at least one happy path and one failure-path criterion | met | Review: each F*-1 file; failure criteria listed in the Test results table |
| At least one isolation criterion per data-reading feature | met | F3-1 #4, F4-1 #4, F5-1 #4, F6-1 #4, F7-1 #4, F8-1 #5, F9-1 #3, E2E-1 #9 (F1 and F2 read no organization data) |
| Journey story maps step by step to the done definition | met, with caveat (Q8) | E2E-1 criteria 1-7 map to the step list; 8-9 add permission and isolation |
| PR opened | met | https://github.com/Gopi-Git001/feedback_borard/pull/1 |

## Files changed
Only files under docs/project/stories/ and docs/project/handoffs/. Created in Attempt 1 and edited in Attempt 2 (review fixes):
- docs/project/stories/F1-1-signup-login.md
- docs/project/stories/F2-1-organization-create-join.md
- docs/project/stories/F3-1-invite-link.md
- docs/project/stories/F4-1-posts.md
- docs/project/stories/F5-1-upvotes.md (footer only)
- docs/project/stories/F6-1-comments.md
- docs/project/stories/F7-1-board.md
- docs/project/stories/F8-1-status-change.md (footer only)
- docs/project/stories/F9-1-delete-post.md
- docs/project/stories/E2E-1-owner-journey.md
- docs/project/handoffs/TASK-002-handoff.md

## How to test locally
Docs-only task, nothing to run. To review: open each story and check (1) every criterion can be turned into a test with the stated values, (2) the failure and permission cases in the Test results table are present, (3) ASSUMED items match the brief's ASSUMED list or are flagged in Open questions, (4) every exact UI or error text is marked ASSUMED. Confirm that `git diff --name-only main` lists only files under docs/project/stories/ and docs/project/handoffs/.

## Test results
No automated tests (docs task). Manual review-story-readiness run on each story, repeated after the Attempt 2 edits (I did this myself, not an independent review; qa-bot does the independent review):

| Story | Ready? | Criteria | Gaps / questions |
|-------|--------|----------|------------------|
| F1-1 signup-login | READY | 6 | Limits and message texts ASSUMED (Q3, Q5). Failure: duplicate email #2, validation #3, wrong password #5, unauthenticated 401 #6 |
| F2-1 organization-create-join | READY | 6 | Q1, Q3, Q4, Q5. Failure: validation #2, invalid invite #4, already in org #5, 401 #6 |
| F3-1 invite-link | READY | 5 | Q2 resolved: one persistent token per org. Same link after reload or new session #2, member 403 #3, isolation (no-org user joins Acme only, Beta 404, tokens differ) #4, 401 #5 |
| F4-1 posts | READY | 6 | Q1, Q3. Failure: validation #2, #3; 404 cross-org #4; 401 #6 |
| F5-1 upvotes | READY | 6 | Q1, Q7. Failure: 404 cross-org #4, missing post #5, 401 #6; vote twice = toggle (per brief ASSUMED) #2 |
| F6-1 comments | READY | 6 | Q1, Q3, Q5. Failure: validation #2, 404 #4/#5, 401 #6; empty state #3 |
| F7-1 board | READY | 6 | Q1, Q5, Q7, Q9. Sort and tie-break #1, filters #2, empty board #3, isolation #4, invalid filter value #5 (ASSUMED), 401 #6 |
| F8-1 status-change | READY | 6 | Q1, Q7. Member 403 #3, invalid value #4, cross-org 404 #5, 401 #6; any direction (brief ASSUMED) #2 |
| F9-1 delete-post | READY | 5 | Q1, Q6, Q5. Member 403 #2, cross-org 404 #3, repeat delete 404 #4, 401 #5 |
| E2E-1 owner-journey | READY | 9 | More than 6, justified inside the story. Q1, Q5, Q8 |

Checks repeated for every row: 3-6 testable criteria (E2E-1 excepted), at least one error case and one permission or isolation case where the feature has them, no unresolved QUESTION: left, data touched listed, no endpoints or field names, exact UI/error texts marked ASSUMED. Definition of Ready boxes are all checked for the READY rows except "traces to an APPROVED brief", which is conditional on Q1. The "no conflict with the API contract" box could only be checked against the brief, because no contract exists yet (Q10).

## Decisions made (and why)
- File naming: the stories keep the skill's format `F<n>-1-<slug>.md` (e.g. F1-1-signup-login.md). TASK-002 names the shorter pattern `F<n>-<slug>.md`. The Orchestrator (Tech Lead / Scrum Master) approved keeping the skill's format; this is recorded here as an approved waiver of TASK-002's shorter naming pattern, with the Orchestrator as approver.
- Used ASSUMED concrete limits so criteria are testable without vague words (Q3).
- HTTP codes: TASK-002 names only 403 and 404, so those are taken from the task spec. 401 for a missing or invalid login token is ASSUMED (standard meaning; named in neither TASK-002 nor the brief). No endpoints or field names are used (API design is out of scope).
- Exact UI and error texts are not in the brief, so each one is marked ASSUMED in its criterion and in its story's Assumptions list; they can be replaced by "a visible error message" if the human prefers (Q5).
- F3-1: one persistent invite token per organization, per Orchestrator decision. The isolation criterion uses a user with no organization (an admin cannot use an invite, F2-1 #5), and the reuse criterion tests the same URL after reload or in a new session (no second admin exists in the MVP).
- F7-1: added a criterion for an invalid filter value (ASSUMED validation error, Q9). To stay at 6 criteria, sort and newest-first tie-break are now one criterion (#1), using the same "and given" pattern as the empty-board criterion.
- F6-1: "no one edits or deletes comments in the MVP" is marked ASSUMED instead of being presented as following from the brief (the brief covers posts only).
- Vote toggle, any-direction status, hard delete cascade: followed the brief's ASSUMED list where it applies, flagged the rest.
- The Orchestrator accepted the other ASSUMED items (limits, logged-out invite flow, admin can post/vote/comment, permanent delete with confirm dialog, self-vote allowed, no pagination, filters AND) as working assumptions to put in front of the human; they stay marked ASSUMED.

## Open questions
1. **Brief is not approved.** brief.md says "Status: DRAFT (fast-track; approval requested)". The Definition of Ready requires an APPROVED brief. I set stories READY on the assumption the brief will be approved unchanged; if the brief changes, re-run review-story-readiness. Needs: Orchestrator / human approval.
2. **F3-1 invite token (RESOLVED by Orchestrator):** one persistent invite token per organization; "Invite" shows the same link every time and never mints a new token.
3. **Limits are not in the brief.** I used concrete, testable numbers marked ASSUMED; please confirm or replace: password min 8 chars; organization name 1-60; post title 1-120; post description 1-2000 (all three post fields required); comment 1-1000; invite token min 32 chars.
4. **Invite link when logged out:** I assumed the user must sign up / log in first and the invite is then applied (F2-1). Confirm, or say that the token is carried through the sign-up form.
5. **Exact UI and message texts** are not in the brief and are marked ASSUMED: "Email already registered", "Invalid email or password" (identical for wrong password and unknown email, so it does not reveal which emails exist), "create or join organization", "Invite link is invalid", "You already belong to an organization", "Invite" / "Copy" / "Copied" (about 2 seconds), "No posts yet", "No posts match these filters", "New post", "Clear filters", "No comments yet", "Add comment", "Delete this post?". Confirm, or replace with generic wording ("a visible error message").
6. **Admin abilities and delete:** I assumed an admin can also post, vote and comment (the brief lists those under member), and that delete is a hard delete with cascade of comments and votes behind a confirmation dialog (the brief says neither). Also assumed: no one can edit or delete comments in the MVP. Confirm.
7. **Voting on own post** is allowed (ASSUMED). **Board** has no pagination and filters combine with AND (ASSUMED). **Same-status change** is a no-op (ASSUMED).
8. **"Owner's done definition"** (mentioned in TASK-002) is not written in the repo. The journey story follows the step list in the TASK-002 request: sign up, create org, invite a second user, post, vote, comment, change status. Please point me to the real wording if it differs.
9. **Invalid filter value on the board** (new in Attempt 2): the brief does not define what happens for an unknown type or status. F7-1 #5 assumes a validation error and no posts returned. Alternative: ignore the unknown filter or return an empty list. Confirm.
10. **API contract:** TASK-001 (api-contract.yaml) had not landed. TASK-002 names 403 and 404; 401 for "not logged in" is my ASSUMED addition. Validation error shapes are not specified. Recheck all against the contract when it lands.

## Suggested follow-up tasks
- Orchestrator: put the ASSUMED items (Q1, Q3-Q7, Q9) in front of the human in the approval message; if any answer changes, re-run review-story-readiness.
- architect-bot / TASK-001: align the API contract error codes (403/404 from the task, 401 ASSUMED, validation) with these stories.
- qa-bot: derive the pytest and Playwright test list from the criteria; E2E-1 is the Playwright scenario. Independent Attempt 2 review of this fix.
- Optional (qa-bot suggestions, not done, not required by the Orchestrator): a Cancel criterion for the F9-1 confirmation dialog, one-assertion splitting of F7-1 #2, and a criterion for a logged-in user with no organization reading the board.
