# F6-1: Comment on a post
Status: READY
As a member, I want to comment on a post, so that I can discuss the feedback with my team.

## Acceptance criteria
1. Given I am a member of "Acme" viewing post P, When I submit the comment "Same here, please prioritise." (29 characters), Then the comment is saved with me as author and the current time, and it appears under P.
2. Given I am viewing post P, When I submit a comment that is empty, only spaces, or longer than 1000 characters, Then it is rejected with a field-level error and no comment is created.
3. Given post P has 3 comments created at 10:00, 10:05 and 10:10, When I open P, Then the comments are listed oldest first (10:00, 10:05, 10:10); and given a post with 0 comments, Then I see "No comments yet".
4. Given post P belongs to organization "Beta", When a member of "Acme" tries to read or add comments on P, Then the response is 404 and no comment data from "Beta" is returned or created.
5. Given no post exists with the requested id, When I try to comment on it, Then the response is 404 and no comment is created.
6. Given I am not logged in, When I try to read or add a comment, Then the response is 401 and nothing is returned or created.

## Business rules
- Comment text 1 to 1000 characters after trimming (ASSUMED).
- Comments are listed oldest first (ASSUMED).
- Members cannot edit or delete comments (consistent with brief ASSUMED rule for posts; comments editing is not in the MVP list).
- A comment belongs to one post and so to that post's organization.

## UI notes
- Comment list under the post, then a text box and "Add comment" button.
- Each comment shows author, time and text.

## Data touched
- Comment: post, author, text, created time.

## Out of scope
Editing or deleting comments, replies/threads, mentions, notifications, markdown or attachments.

## Assumptions / Questions
- ASSUMED: comment limit 1000 characters; oldest-first ordering.
- Brief status was DRAFT (fast-track) when this was written; READY status is conditional on brief approval (see handoff Open questions #1).
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- ASSUMED (all stories): API contract (TASK-001) did not exist yet; HTTP codes are used only where the task spec names them (401/403/404); recheck against the contract when it lands.
