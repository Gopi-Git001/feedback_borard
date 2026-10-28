# F6-1: Comment on a post
Status: READY
As a member, I want to comment on a post, so that I can discuss the feedback with my team.

## Acceptance criteria
1. Given I am a member of "Acme" viewing post P, When I submit the comment "Same here, please prioritise." (29 characters), Then the comment is saved with me as author (shown by my display name, for example "Bob") and the current time, and it appears under P.
2. Given I am viewing post P, When I submit a comment that is empty, only spaces, or longer than 1000 characters, Then it is rejected with a field-level error and no comment is created.
3. Given post P has 3 comments created at 10:00, 10:05 and 10:10, When I open P, Then the comments are listed oldest first (10:00, 10:05, 10:10); and given a post with 0 comments, Then I see "No comments yet" (ASSUMED text).
4. Given post P belongs to organization "Beta", When a member of "Acme" tries to read or add comments on P, Then the response is 404 and no comment data from "Beta" is returned or created.
5. Given no post exists with the requested id, When I try to comment on it, Then the response is 404 and no comment is created.
6. Given I am not logged in, When I try to read or add a comment, Then the response is 401 and nothing is returned or created.

## Business rules
- Comment text 1 to 1000 characters after trimming (ASSUMED).
- Comments are listed oldest first (ASSUMED).
- No one can edit or delete comments in the MVP (ASSUMED). The brief only says members cannot edit or delete posts and lists comment editing nowhere in the MVP; deleting a post (F9) removes its comments.
- A comment belongs to one post and so to that post's organization.
- A comment names its author by display name only; the email is never shown to other members (API contract).
- A request that creates a comment with a Content-Type that the media-type rule of F1-9 refuses is answered 415 after the limiter (where there is one) and before authentication, and changes nothing (F1-9; not a criterion of this story).

## UI notes
- Comment list under the post, then a text box and "Add comment" button (ASSUMED label).
- Each comment shows the author's display name (not email), time and text.

## Data touched
- Comment: post, author (shown by display name), text, created time.

## Out of scope
Editing or deleting comments, replies/threads, mentions, notifications, markdown or attachments.

## Assumptions / Questions
- ASSUMED: comment limit 1000 characters; oldest-first ordering.
- ASSUMED: exact UI texts "No comments yet" and "Add comment"; no one can edit or delete comments in the MVP.
- Brief status was DRAFT (fast-track) when this was written; READY status is conditional on brief approval (see handoff Open questions #1).
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- HTTP codes: 403 and 404 are named in TASK-002; 429 and the other error codes come from the API contract; 401 is ASSUMED (the contract lists it but itself marks it ASSUMED). Checked against the contract on main (11497e9a337fdad6d56582077ac3c529d77e3e44, which contains the merges of PR #2 (54f79e4), PR #6 (4a2e084) and PR #7 (11497e9)).
- Contract check (TASK-040 follow-up, re-pointed to main; first written in Attempt 4): api-contract.yaml is on main (11497e9a337fdad6d56582077ac3c529d77e3e44, which contains the merges of PR #2 (54f79e4), PR #6 (4a2e084) and PR #7 (11497e9); contract: docs/project/architecture/api-contract.yaml, ADRs: docs/project/decisions/; the files' own status line said Proposed at that commit; since PR #14 the contract, data-model.md and stack.md say Accepted by Orchestrator, and ADR-001 to ADR-004 still say Proposed on main 4f08a039b7d89b0ae4f1cac32cf9fbc1408b16cc; architect-bot is aligning the ADR statuses, as reported by the Orchestrator). Comment author is exposed as display name only (no email); comment limit 1-1000 matches.
