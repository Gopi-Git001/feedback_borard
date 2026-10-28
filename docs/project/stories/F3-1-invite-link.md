# F3-1: Admin generates an invite link
Status: DRAFT
As an admin, I want to generate an invite link that I can copy and share, so that teammates can join my organization.

## Acceptance criteria
1. Given I am the admin of "Acme", When I click "Generate invite link", Then I see a full URL containing a token of at least 32 random characters, and a "Copy" action that puts that exact URL on my clipboard.
2. Given I generated an invite link for "Acme", When two different logged-in users with no organization open it one after the other and accept, Then both become members of "Acme" (the link is reusable, and was not consumed by the first use).
3. Given I am a member (not admin) of "Acme", When I try to generate an invite link, Then the response is 403 and no invite token is created.
4. Given I am the admin of "Acme" and another organization "Beta" exists, When I use my invite link, Then the user joins only "Acme", and the link never gives access to any "Beta" data.
5. Given I am not logged in, When I request an invite link, Then the response is 401 and no token is created.

## Business rules
- Invite link is for exactly one organization (brief ASSUMED).
- Reusable until revoked; revocation is not in the MVP (brief ASSUMED), so a generated link stays valid for the life of the MVP.
- Token is long and random (brief ASSUMED); minimum 32 characters (ASSUMED number).
- Only admins can generate links (brief role table).

## UI notes
- Admin-only "Invite" control on the board page; members do not see it.
- After generating: read-only text field with the link and a "Copy" button; after copying the button shows "Copied" for about 2 seconds.

## Data touched
- Invite: organization, token, created time, created by.

## Out of scope
Revoking or expiring links, sending the link by email, per-link usage limits, listing all links, invite by email address.

## Assumptions / Questions
- ASSUMED: minimum token length is 32 characters.
- QUESTION: Does each click on "Generate invite link" create a new token (several valid links per organization), or does the organization have one persistent token that is shown again? Since revocation is not in the MVP, a new token would leave all older links valid. Product decision needed; blocks a testable criterion for "generate twice".
- Brief status was DRAFT (fast-track) when this was written; READY status is conditional on brief approval (see handoff Open questions #1).
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- ASSUMED (all stories): API contract (TASK-001) did not exist yet; HTTP codes are used only where the task spec names them (401/403/404); recheck against the contract when it lands.
