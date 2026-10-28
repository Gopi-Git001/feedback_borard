# F4-1: Create a feedback post
Status: READY
As a member, I want to create a post with a title, description and type (idea or bug), so that my team can see and discuss my feedback.

## Acceptance criteria
1. Given I am a logged-in member of "Acme", When I submit title "Dark mode" (9 characters), description "Please add a dark theme." and type "idea", Then a post is created in "Acme" with status "New", 0 votes, my display name as author (for example "Alice") and the current time as created time, and it appears on the "Acme" board.
2. Given I am on the new-post form, When I submit (a) an empty or spaces-only title, (b) a title longer than 120 characters, (c) an empty description, or (d) a description longer than 2000 characters, Then the post is rejected with a field-level error naming the field and no post is created.
3. Given I am on the new-post form, When I submit a type other than "idea" or "bug" (or no type), Then the post is rejected with a field-level error on type and no post is created.
4. Given a post exists in organization "Beta", When a member of "Acme" requests that post by its id, Then the response is 404 and no data from "Beta" is returned.
5. Given I am a member of "Acme" and a post exists in "Acme", When I open that post, Then I see its title, description, type, status, vote count, the author's display name (not the author's email) and created time.
6. Given I am not logged in, When I try to create or read a post, Then the response is 401 and no post is created or returned.

## Business rules
- Required fields: title, description, type (brief F4; all three required is ASSUMED).
- Title 1 to 120 characters, description 1 to 2000 characters, after trimming (ASSUMED numbers).
- Type is one of: idea, bug. New posts always start with status New (first status in brief F8 order).
- Members cannot edit or delete posts (brief ASSUMED).
- Every post belongs to exactly one organization, the author's.
- A post names its author by display name only; the email is never shown to other members (API contract).
- A request that creates a post with a Content-Type whose media type is not "application/json" is answered 415 after the limiter (where there is one) and before authentication, and changes nothing (F1-9; not a criterion of this story).

## UI notes
- "New post" form (ASSUMED label) with title, description, and a type selector (idea / bug).
- After success the user returns to the board and sees the new post.

## Data touched
- Post: organization, author (shown by display name), title, description, type, status, created time.

## Out of scope
Editing or deleting own posts (post-MVP), attachments, search, tags, drafts.

## Assumptions / Questions
- ASSUMED: title 1-120 and description 1-2000 characters, both required.
- Brief status was DRAFT (fast-track) when this was written; READY status is conditional on brief approval (see handoff Open questions #1).
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- HTTP codes: 403 and 404 are named in TASK-002; 429 and the other error codes come from the API contract; 401 is ASSUMED (the contract lists it but itself marks it ASSUMED). Checked against the contract on main (11497e9a337fdad6d56582077ac3c529d77e3e44, which contains the merges of PR #2 (54f79e4), PR #6 (4a2e084) and PR #7 (11497e9)).
- Contract check (TASK-040 follow-up, re-pointed to main; first written in Attempt 4): api-contract.yaml is on main (11497e9a337fdad6d56582077ac3c529d77e3e44, which contains the merges of PR #2 (54f79e4), PR #6 (4a2e084) and PR #7 (11497e9); contract: docs/project/architecture/api-contract.yaml, ADRs: docs/project/decisions/; the files' own status line still says Proposed). Post author is exposed as display name only (no email); title, description and type limits match the contract.
