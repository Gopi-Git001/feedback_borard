# F9-1: Admin deletes a post
Status: READY
As an admin, I want to delete a post, so that I can remove spam, duplicates or off-topic feedback from the board.

## Acceptance criteria
1. Given I am the admin of "Acme" and post P has 2 comments and 3 votes, When I delete P and confirm, Then P no longer appears on the board or by its id (404), and P's comments and votes are no longer retrievable.
2. Given I am a member (not admin) of "Acme", When I try to delete post P, Then the response is 403, P still exists with its comments and votes, and the delete control is not shown to me in the UI.
3. Given post P belongs to organization "Beta", When the admin of "Acme" tries to delete P, Then the response is 404 and P still exists.
4. Given post P was already deleted (or never existed), When the admin requests deletion again, Then the response is 404 and nothing else changes.
5. Given I am not logged in, When I try to delete a post, Then the response is 401 and the post still exists.
6. Given I am the admin of "Acme", post P has 2 comments and 3 votes, and the delete confirmation dialog is open, When I click "Cancel" (ASSUMED button text), Then the dialog closes and P, its comments and its votes remain unchanged.

## Business rules
- Only admins delete posts (brief role table); members cannot delete posts, including their own (brief ASSUMED).
- Deleting a post also removes its comments and votes (ASSUMED; they cannot exist without the post).
- Deletion is permanent in the MVP, no undo or trash (ASSUMED).
- Admin may only delete posts of their own organization.

## UI notes
- Admin-only "Delete" control on the post page; clicking it asks for confirmation (ASSUMED text: "Delete this post?" with Delete / Cancel). Cancel closes the dialog and leaves the post unchanged (criterion 6). (Confirmation step is a UI safeguard; see handoff Open questions.)

## Data touched
- Post (removed), Comment (removed with post), Vote (removed with post).

## Out of scope
Deleting comments, restoring deleted posts, bulk delete, soft delete / audit trail, members deleting own posts (post-MVP).

## Assumptions / Questions
- ASSUMED: hard delete with cascade of comments and votes; confirmation dialog before delete (texts "Delete this post?", "Delete", "Cancel" are ASSUMED).
- Brief status was DRAFT (fast-track) when this was written; READY status is conditional on brief approval (see handoff Open questions #1).
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- API contract (TASK-001) did not exist yet. The TASK-002 spec names 403 (member on admin action) and 404 (cross-organization access); stories use no other HTTP code. ASSUMED: 401 for a missing or invalid login token (standard meaning; named in neither TASK-002 nor the brief). Recheck all codes against the contract when it lands.
- Contract check (TASK-039): api-contract.yaml (branch feature/TASK-001-stack-and-contracts, not yet on main) now exists. It confirms hard delete with cascade, 403 for a member, 404 for another organization's post (checked before the role) and 401 without login. The confirmation dialog and its Cancel button are UI-only and not in the contract. Recheck once it is merged to main.
