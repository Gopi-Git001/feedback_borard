# F4-1: Create a feedback post
Status: READY
As a member, I want to create a post with a title, description and type (idea or bug), so that my team can see and discuss my feedback.

## Acceptance criteria
1. Given I am a logged-in member of "Acme", When I submit title "Dark mode" (9 characters), description "Please add a dark theme." and type "idea", Then a post is created in "Acme" with status "New", 0 votes, me as author and the current time as created time, and it appears on the "Acme" board.
2. Given I am on the new-post form, When I submit (a) an empty or spaces-only title, (b) a title longer than 120 characters, (c) an empty description, or (d) a description longer than 2000 characters, Then the post is rejected with a field-level error naming the field and no post is created.
3. Given I am on the new-post form, When I submit a type other than "idea" or "bug" (or no type), Then the post is rejected with a field-level error on type and no post is created.
4. Given a post exists in organization "Beta", When a member of "Acme" requests that post by its id, Then the response is 404 and no data from "Beta" is returned.
5. Given I am a member of "Acme" and a post exists in "Acme", When I open that post, Then I see its title, description, type, status, vote count, author and created time.
6. Given I am not logged in, When I try to create or read a post, Then the response is 401 and no post is created or returned.

## Business rules
- Required fields: title, description, type (brief F4; all three required is ASSUMED).
- Title 1 to 120 characters, description 1 to 2000 characters, after trimming (ASSUMED numbers).
- Type is one of: idea, bug. New posts always start with status New (first status in brief F8 order).
- Members cannot edit or delete posts (brief ASSUMED).
- Every post belongs to exactly one organization, the author's.

## UI notes
- "New post" form with title, description, and a type selector (idea / bug).
- After success the user returns to the board and sees the new post.

## Data touched
- Post: organization, author, title, description, type, status, created time.

## Out of scope
Editing or deleting own posts (post-MVP), attachments, search, tags, drafts.

## Assumptions / Questions
- ASSUMED: title 1-120 and description 1-2000 characters, both required.
- Brief status was DRAFT (fast-track) when this was written; READY status is conditional on brief approval (see handoff Open questions #1).
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- ASSUMED (all stories): API contract (TASK-001) did not exist yet; HTTP codes are used only where the task spec names them (401/403/404); recheck against the contract when it lands.
