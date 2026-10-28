# F3-1: Admin shares the organization's invite link
Status: READY
As an admin, I want to see and copy my organization's invite link and share it, so that teammates can join my organization.

## Acceptance criteria
1. Given I am the admin of "Acme" and no invite token exists yet for "Acme", When I click "Invite", Then I see a full URL containing a token of at least 32 random characters, and a "Copy" action that puts that exact URL on my clipboard.
2. Given "Acme" already has an invite token, When I click "Invite" a second time (or a second admin of "Acme" does), Then the same URL with the same token is shown, and still exactly one invite token exists for "Acme".
3. Given I am a member (not admin) of "Acme", When I try to get the invite link, Then the response is 403 and no invite token is created.
4. Given I am the admin of "Acme" and another organization "Beta" exists, When I use my invite link, Then the user joins only "Acme", and the link never gives access to any "Beta" data.
5. Given I am not logged in, When I request the invite link, Then the response is 401 and no token is created.

## Business rules
- Each organization has one persistent invite token, created the first time an admin opens "Invite" and shown again on every later click; clicking never creates a new token (Orchestrator decision, consistent with brief.md ASSUMED).
- Invite link is for exactly one organization (brief ASSUMED).
- Reusable until revoked; revocation is not in the MVP (brief ASSUMED), so the link stays valid for the life of the MVP.
- Token is long and random (brief ASSUMED); minimum 32 characters (ASSUMED number).
- Only admins can see the invite link (brief role table).

## UI notes
- Admin-only "Invite" control on the board page; members do not see it.
- After clicking "Invite": read-only text field with the link and a "Copy" button; after copying the button shows "Copied" for about 2 seconds.

## Data touched
- Invite: organization (one per organization), token, created time, created by.

## Out of scope
Revoking, regenerating or expiring links, multiple links per organization, sending the link by email, per-link usage limits, listing all links, invite by email address.

## Assumptions / Questions
- ASSUMED: minimum token length is 32 characters.
- DECIDED by Orchestrator (TASK-002 follow-up): one persistent invite token per organization; "Invite" shows the same link every time. No open questions remain for this story.
- ASSUMED: logged-out invite flow (sign up or log in first, then the invite is applied) is specified in F2-1.
- Brief status was DRAFT (fast-track) when this was written; READY status is conditional on brief approval (see handoff Open questions #1).
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- ASSUMED (all stories): API contract (TASK-001) did not exist yet; HTTP codes are used only where the task spec names them (401/403/404); recheck against the contract when it lands.
