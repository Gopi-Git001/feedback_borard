# F2-1: Create an organization or join one via invite link
Status: READY
Security review: touches authentication (security-bot review required)
As a new user, I want to create an organization (and become its admin) or join one through an invite link, so that I get access to my team's board.

## Acceptance criteria
1. Given I am logged in and belong to no organization, When I create an organization named "Acme" (4 characters), Then the organization exists, I am its admin and its only member, and I land on its empty board.
2. Given I am logged in and belong to no organization, When I submit an organization name that is empty, only spaces, or longer than 60 characters, Then creation is rejected with a field-level error and no organization is created.
3. Given I am logged in with no organization and I hold a valid invite link "<site address>/join#<token>" for "Acme", When I open the link, Then the page asks the server to preview the token (POST /invites/preview with the token in the body) and shows the organization name "Acme", and when I accept (POST /invites/accept with the token in the body), Then I become a member (not admin) of "Acme" and land on its board; no request URL contains the token.
4. Given I am logged in and I open an invite link whose token does not exist (for example the token is edited, truncated, or random) or a "/join" link with no token after the "#", When I try to join, Then I see the message "Invite link is invalid" (the contract's INVITE_NOT_FOUND message; the brief gives no wording), I am not added to any organization, and no data about any organization is shown; for a link with no token no request is sent (ASSUMED: from the TASK-001 handoff, not in the contract or ADR-003).
5. Given I already belong to an organization, When I try to create another organization or join via any invite link (including one for my own organization), Then the action is rejected with the message "You already belong to an organization" (ASSUMED text) and my membership is unchanged.
6. Given I am not logged in, When I try to create an organization or to accept an invite (POST /invites/accept), Then the response is 401, no organization is created, and I am not added to one (the invite preview stays public, see F3-1 criterion 6).

## Business rules
- A user belongs to exactly one organization (brief, ASSUMED for MVP).
- Joining uses the invite link "<site address>/join#<token>"; the token travels only in the URL fragment and in POST bodies (preview, accept), never in a request URL (ADR-003, brief.md approved addition).
- A logged-out visitor who opens an invite link signs up or logs in first; the token is held in sessionStorage (key "pending_invite") meanwhile and the invite is applied afterwards (ADR-003; testable in F3-2 criterion 4). The page removes the fragment from the address bar after reading it (F3-2 criterion 3).
- The creator of an organization is its admin; everyone who joins via an invite link is a member (brief roles).
- Organization name length 1 to 60 characters after trimming (ASSUMED). Duplicate organization names are allowed, because isolation is by organization id (ASSUMED).

## UI notes
- A logged-in user with no organization sees two choices: "Create organization" (name field) or "Join with invite link" (ASSUMED labels).
- Opening an invite link while logged out shows the organization name and sends me to sign up (email, password and display name, see F1-1) or log in first, and then applies the invite (ADR-003; page layout ASSUMED).

## Data touched
- Organization: name, created time.
- User: organization, role (admin or member).

## Out of scope
Multiple organizations per user, leaving or switching organization, renaming or deleting an organization, removing members, transferring admin.

## Assumptions / Questions
- ASSUMED: organization name 1 to 60 characters; duplicate names allowed.
- ASSUMED: exact UI/message texts "You already belong to an organization", "Create organization", "Join with invite link" (the brief gives no wording). "Invite link is invalid" is taken from the contract and ADR-003 (verbatim), which are still Proposed (PR #2).
- The logged-out flow (sign up or log in first, token kept in sessionStorage, invite applied afterwards) was ASSUMED before; it is now specified by ADR-003 and tested in F3-2 criterion 4.
- Brief status was DRAFT (fast-track) when this was written; READY status is conditional on brief approval (see handoff Open questions #1).
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- HTTP codes: 403 and 404 are named in TASK-002; 429 and the other error codes come from the API contract; 401 is ASSUMED (the contract lists it but itself marks it ASSUMED). Recheck once the contract is merged to main.
- Contract check (TASK-040): checked against api-contract.yaml and ADR-003 on the TASK-001 branch (PR #2, head 0459573, Proposed, not on main): POST /invites/preview (public, 200/404/429) and POST /invites/accept (200/401/404/409/429), message "Invite link is invalid", 409 ALREADY_IN_ORGANIZATION. 401 is ASSUMED in the contract. Recheck once merged to main.
