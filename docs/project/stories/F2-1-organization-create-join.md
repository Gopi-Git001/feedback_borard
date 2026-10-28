# F2-1: Create an organization or join one via invite link
Status: READY
As a new user, I want to create an organization (and become its admin) or join one through an invite link, so that I get access to my team's board.

## Acceptance criteria
1. Given I am logged in and belong to no organization, When I create an organization named "Acme" (4 characters), Then the organization exists, I am its admin and its only member, and I land on its empty board.
2. Given I am logged in and belong to no organization, When I submit an organization name that is empty, only spaces, or longer than 60 characters, Then creation is rejected with a field-level error and no organization is created.
3. Given I am logged in with no organization and I hold a valid invite link for "Acme", When I open the link and accept, Then I become a member (not admin) of "Acme" and land on its board.
4. Given I am logged in and I open an invite link whose token does not exist (for example the token is edited, truncated, or random), When I try to join, Then I see the message "Invite link is invalid" (ASSUMED text), I am not added to any organization, and no data about any organization is shown.
5. Given I already belong to an organization, When I try to create another organization or join via any invite link (including one for my own organization), Then the action is rejected with the message "You already belong to an organization" (ASSUMED text) and my membership is unchanged.
6. Given I am not logged in, When I try to create or join an organization, Then the response is 401, no organization is created, and I am not added to one.

## Business rules
- A user belongs to exactly one organization (brief, ASSUMED for MVP).
- The creator of an organization is its admin; everyone who joins via an invite link is a member (brief roles).
- Organization name length 1 to 60 characters after trimming (ASSUMED). Duplicate organization names are allowed, because isolation is by organization id (ASSUMED).

## UI notes
- A logged-in user with no organization sees two choices: "Create organization" (name field) or "Join with invite link" (ASSUMED labels).
- Opening an invite link while logged out sends me to sign up / log in first, and then applies the invite (ASSUMED; see handoff Open questions).

## Data touched
- Organization: name, created time.
- User: organization, role (admin or member).

## Out of scope
Multiple organizations per user, leaving or switching organization, renaming or deleting an organization, removing members, transferring admin.

## Assumptions / Questions
- ASSUMED: organization name 1 to 60 characters; duplicate names allowed.
- ASSUMED: exact UI/message texts "Invite link is invalid", "You already belong to an organization", "Create organization", "Join with invite link" (the brief gives no wording).
- ASSUMED: a logged-out user opening an invite link signs up / logs in first and then the invite is applied.
- Brief status was DRAFT (fast-track) when this was written; READY status is conditional on brief approval (see handoff Open questions #1).
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- API contract (TASK-001) did not exist yet. The TASK-002 spec names 403 (member on admin action) and 404 (cross-organization access); stories use no other HTTP code. ASSUMED: 401 for a missing or invalid login token (standard meaning; named in neither TASK-002 nor the brief). Recheck all codes against the contract when it lands.
