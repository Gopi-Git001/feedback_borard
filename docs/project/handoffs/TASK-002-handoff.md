# Handoff: TASK-002 User stories with testable acceptance criteria for F1-F9
Bot: ba-bot   Attempt: 1   PR: (set when the PR is opened)   Branch: feature/TASK-002-user-stories

## Open questions (read first)
1. **Brief is not approved.** brief.md says "Status: DRAFT (fast-track; approval requested)". The Definition of Ready requires an APPROVED brief. I set stories READY on the assumption the brief will be approved unchanged; if the brief changes, re-run review-story-readiness. Needs: Orchestrator / human approval.
2. **F3-1 (blocks READY, story left DRAFT):** Does each click on "Generate invite link" create a new token, or does the organization have one persistent token that is shown again? Since revocation is not in the MVP, new tokens would leave every older link valid. Needs a product decision.
3. **Limits are not in the brief.** I used concrete, testable numbers marked ASSUMED; please confirm or replace: password min 8 chars; organization name 1-60; post title 1-120; post description 1-2000 (all three post fields required); comment 1-1000; invite token min 32 chars.
4. **Invite link when logged out:** I assumed the user must sign up / log in first and the invite is then applied (F2-1). Confirm, or say that the token is carried through the sign-up form.
5. **Login error text** is identical for wrong password and unknown email (ASSUMED, does not reveal which emails exist).
6. **Admin abilities:** I assumed an admin can also post, vote and comment (brief lists those under member). Confirm.
7. **Delete post:** I assumed hard delete with cascade of comments and votes, and a confirmation dialog in the UI. The brief says neither. Confirm.
8. **Voting on own post** is allowed (ASSUMED). **Board** has no pagination and filters combine with AND (ASSUMED). **Same-status change** is a no-op (ASSUMED).
9. **"Owner's done definition"** (mentioned in TASK-002) is not written in the repo. The journey story follows the step list in the TASK-002 request: sign up, create org, invite a second user, post, vote, comment, change status. Please point me to the real wording if it differs.
10. **API contract:** TASK-001 (api-contract.yaml) had not landed, so stories use HTTP codes only where TASK-002 names them (401/403/404). Recheck against the contract when it lands. I used 401 for "not logged in" (not named in the task spec, standard meaning).
11. **File naming:** TASK-002 says F<n>-<slug>.md; the write-user-stories skill says <FEATURE-ID>-<n>-<slug>.md. I followed the skill (e.g. F1-1-signup-login.md). Rename if you prefer the shorter form.

## Summary
Ten story files in docs/project/stories/: one per feature F1-F9 and one end-to-end journey (E2E-1). Each has Given/When/Then criteria with concrete values, covering happy path, validation, duplicate email, wrong password, invalid invite, 403 for members on admin actions, 404 for cross-organization access, empty board and newest-first tie-break. Nine stories are READY; F3-1 is DRAFT because of one open product question.

## Acceptance criteria
| Criterion | Status (met / not met) | Test that proves it |
|-----------|------------------------|---------------------|
| Each feature F1-F9 has a story with at least one happy path and one failure-path criterion | met | Review: each F*-1 file; failure criteria listed in the table below |
| At least one isolation criterion per data-reading feature | met | F4-1 #4, F5-1 #4, F6-1 #4, F7-1 #5, F8-1 #5, F9-1 #3, E2E-1 #9 (F1 and F2 read no organization data; F3-1 #4 covers the invite link) |
| Journey story maps step by step to the done definition | met, with caveat (open question 9) | E2E-1 criteria 1-7 map to the step list; 8-9 add permission and isolation |
| PR opened | see PR line above | n/a |

## Files changed
Only new files (no existing file modified):
- docs/project/stories/F1-1-signup-login.md
- docs/project/stories/F2-1-organization-create-join.md
- docs/project/stories/F3-1-invite-link.md
- docs/project/stories/F4-1-posts.md
- docs/project/stories/F5-1-upvotes.md
- docs/project/stories/F6-1-comments.md
- docs/project/stories/F7-1-board.md
- docs/project/stories/F8-1-status-change.md
- docs/project/stories/F9-1-delete-post.md
- docs/project/stories/E2E-1-owner-journey.md
- docs/project/handoffs/TASK-002-handoff.md

## How to test locally
Docs-only task, nothing to run. To review: open each story and check (1) every criterion can be turned into a test with the stated values, (2) the failure and permission cases in the table below are present, (3) ASSUMED items match the brief's ASSUMED list or are flagged in Open questions. Confirm that `git diff --name-only main` lists only files under docs/project/stories/ and docs/project/handoffs/.

## Test results
No automated tests (docs task). Manual review-story-readiness run on each story (I did this myself, not an independent review):

| Story | Ready? | Gaps / questions |
|-------|--------|------------------|
| F1-1 signup-login | READY | Limits ASSUMED (Q3); brief not approved (Q1). Failure: duplicate email #2, validation #3, wrong password #5, unauthenticated 401 #6 |
| F2-1 organization-create-join | READY | Q1, Q3, Q4. Failure: validation #2, invalid invite #4, already in org #5, 401 #6 |
| F3-1 invite-link | DRAFT | QUESTION open (Q2): new token per click vs one persistent token. Permission: member 403 #3, 401 #5 |
| F4-1 posts | READY | Q1, Q3. Failure: validation #2, #3; 404 cross-org #4; 401 #6 |
| F5-1 upvotes | READY | Q1, Q8. Failure: 404 cross-org #4, missing post #5, 401 #6; vote twice = toggle (per brief ASSUMED) #2 |
| F6-1 comments | READY | Q1, Q3. Failure: validation #2, 404 #4/#5, 401 #6; empty state #3 |
| F7-1 board | READY | Q1, Q8. Sort #1, tie-break newest #2, filters #3, empty board #4, isolation #5, 401 #6 |
| F8-1 status-change | READY | Q1, Q8. Member 403 #3, invalid value #4, cross-org 404 #5, 401 #6; any direction (brief ASSUMED) #2 |
| F9-1 delete-post | READY | Q1, Q7. Member 403 #2, cross-org 404 #3, repeat delete 404 #4, 401 #5 |
| E2E-1 owner-journey | READY | 9 criteria (more than 6, justified inside the story). Q1, Q9 |

Definition of Ready boxes all checked for the READY rows except "traces to an APPROVED brief", which is conditional on Q1. The "no conflict with the API contract" box could only be checked against the brief, because no contract exists yet (Q10).

## Decisions made (and why)
- Followed the skill's file naming (Q11).
- Used ASSUMED concrete limits so criteria are testable without vague words (Q3).
- Stories name HTTP codes 401/403/404 only, per the task, and no endpoints or field names (API design is out of scope).
- Left F3-1 DRAFT rather than guess the invite-token behavior.
- Vote toggle, any-direction status, hard delete cascade: followed the brief's ASSUMED list where it applies, flagged the rest.

## Suggested follow-up tasks
- Orchestrator: answer Q1-Q4 and Q7, then I update the stories and flip F3-1 to READY.
- architect-bot / TASK-001: align the API contract error codes (401/403/404, validation) with these stories.
- qa-bot: derive the pytest and Playwright test list from the criteria; E2E-1 is the Playwright scenario.
