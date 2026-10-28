# F3-1: Admin shares the organization's invite link
Status: READY
As an admin, I want to see and copy my organization's invite link and share it, so that teammates can join my organization.

## Acceptance criteria
1. Given I am the admin of "Acme" and no invite token exists yet for "Acme", When I click "Invite", Then I see a full URL containing a token of at least 32 random characters, and a "Copy" action that puts that exact URL on my clipboard.
2. Given "Acme" already has an invite token and I have seen its URL, When I click "Invite" again after reloading the page, or after logging out and in again (a new session), Then the same URL with the same token is shown, and still exactly one invite token exists for "Acme".
3. Given I am a member (not admin) of "Acme", When I try to get the invite link, Then the response is 403 and no invite token is created.
4. Given "Dan" (display name "Dan") is logged in with no organization, and organizations "Acme" and "Beta" each have an invite token, When Dan opens the "Acme" invite link and accepts, Then he is a member (not admin) of "Acme" only, he sees only "Acme" posts, requesting any "Beta" post by its id returns 404, and the "Acme" token differs from the "Beta" token.
5. Given I am not logged in, When I request the invite link, Then the response is 401 and no token is created.
6. Given one IP address has already made 10 invite-preview requests in the last 60 seconds (ASSUMED threshold; the preview is the public page that shows only the organization name, e.g. "Acme", before sign-up), When it makes an 11th request, Then the response is 429 with code "RATE_LIMITED", the message "Too many requests. Try again later." and a Retry-After header with a whole number of seconds greater than 0, and no organization name is returned; and after the Retry-After seconds have passed, previewing the "Acme" link shows "Acme" and nothing else about the organization.

## Business rules
- Each organization has one persistent invite token, created the first time an admin opens "Invite" and shown again on every later click; clicking never creates a new token (Orchestrator decision, consistent with brief.md ASSUMED).
- Invite link is for exactly one organization (brief ASSUMED).
- Reusable until revoked; revocation is not in the MVP (brief ASSUMED), so the link stays valid for the life of the MVP.
- Token is long and random (brief ASSUMED); minimum 32 characters (ASSUMED number).
- Only admins can see the invite link (brief role table).
- Invite preview is public (no login) and returns only the organization name (API contract). It is rate limited per IP address (HTTP 429, contract-sourced). ASSUMED: 10 requests per rolling 60 seconds per IP address, counted for any token, valid or not.

## UI notes
- Admin-only "Invite" control on the board page; members do not see it.
- After clicking "Invite": read-only text field with the link and a "Copy" button; after copying the button shows "Copied" for about 2 seconds (ASSUMED text and duration; "Invite" and "Copy" labels are also ASSUMED).

## Data touched
- Invite: organization (one per organization), token, created time, created by.

## Out of scope
Revoking, regenerating or expiring links, multiple links per organization, sending the link by email, per-link usage limits, listing all links, invite by email address.

## Assumptions / Questions
- ASSUMED: minimum token length is 32 characters.
- ASSUMED: invite-preview rate limit of 10 requests per rolling 60 seconds per IP address (contract says "rate limited", no number); the limit counts valid and invalid tokens alike. Same threshold and 429 format as F1-2.
- ASSUMED: exact UI texts "Invite", "Copy", "Copied" (about 2 seconds); the brief only says the admin generates a link to copy and share.
- DECIDED by Orchestrator (TASK-002 follow-up): one persistent invite token per organization; "Invite" shows the same link every time. No open questions remain for this story.
- ASSUMED: logged-out invite flow (sign up or log in first, then the invite is applied) is specified in F2-1.
- Brief status was DRAFT (fast-track) when this was written; READY status is conditional on brief approval (see handoff Open questions #1).
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- API contract (TASK-001) did not exist yet. The TASK-002 spec names 403 (member on admin action) and 404 (cross-organization access); stories use no other HTTP code. ASSUMED: 401 for a missing or invalid login token (standard meaning; named in neither TASK-002 nor the brief). Recheck all codes against the contract when it lands.
- Contract check (TASK-039): api-contract.yaml (branch feature/TASK-001-stack-and-contracts, not yet on main) now exists. It defines invite preview (public, organization name only, 404 for an unknown token, 429 rate limited) and one persistent token per organization (43 characters, consistent with the 32 minimum here). Recheck once it is merged to main.
