# F8-1: Admin changes a post's status
Status: READY
As an admin, I want to move a post through New, Planned, In Progress and Done, so that my team can see how feedback is being handled.

## Acceptance criteria
1. Given I am the admin of "Acme" and post P has status "New", When I set the status to "Planned", then to "In Progress", then to "Done", Then after each step P shows the new status on the post page and on the board.
2. Given post P has status "Done", When I (admin) set the status to "New", Then P shows status "New" (any direction is allowed).
3. Given I am a member (not admin) of "Acme", When I try to change the status of post P, Then the response is 403 and P's status is unchanged; and the status control is not shown to me in the UI.
4. Given I am the admin of "Acme", When I submit a status value other than New, Planned, In Progress or Done, Then it is rejected with a validation error and P's status is unchanged.
5. Given post P belongs to organization "Beta", When the admin of "Acme" tries to change its status, Then the response is 404 and P's status is unchanged.
6. Given I am not logged in, When I try to change a status, Then the response is 401 and the status is unchanged.

## Business rules
- Allowed statuses: New, Planned, In Progress, Done. New posts start as New (F4).
- Normal path is New to Planned to In Progress to Done; an admin may also move in any direction or skip steps (brief ASSUMED).
- Only admins change status (brief role table).
- Changing a post to its current status is accepted and changes nothing (ASSUMED).

## UI notes
- Admins see a status selector on the post page; members see the status as text only.

## Data touched
- Post: status (and updated time, ASSUMED).

## Out of scope
Status history or audit log, notifying anyone of a change, per-status permissions, custom statuses.

## Assumptions / Questions
- ASSUMED: setting the same status again is a no-op, not an error.
- Brief status was DRAFT (fast-track) when this was written; READY status is conditional on brief approval (see handoff Open questions #1).
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- HTTP codes: 403 and 404 are named in TASK-002; 429 and the other error codes come from the API contract; 401 is ASSUMED (the contract lists it but itself marks it ASSUMED). Recheck once the contract is merged to main.
