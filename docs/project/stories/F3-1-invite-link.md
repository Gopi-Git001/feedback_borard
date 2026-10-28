# F3-1: Admin shares the organization's invite link
Status: READY
Security review: touches authentication (security-bot review required)
As an admin, I want to see and copy my organization's invite link and share it, so that teammates can join my organization.

How the token is stored, kept out of request URLs and handled in the browser is in F3-2.

## Acceptance criteria
1. Given I am the admin of "Acme" and no invite token exists yet for "Acme", When I click "Invite", Then I see a full link of the form "<site address>/join#<token>" where the token is in the part after "#" and is at least 32 random characters long (43 with the current design), and a "Copy" action that puts that exact link on my clipboard.
2. Given "Acme" already has an invite token and I have seen its link, When I click "Invite" again after reloading the page, or after logging out and in again (a new session), Then the same link with the same token is shown, and still exactly one invite exists for "Acme".
3. Given I am a member (not admin) of "Acme", When I try to get the invite link, Then the response is 403 and no invite is created.
4. Given "Dan" (display name "Dan") is logged in with no organization, and organizations "Acme" and "Beta" each have an invite, When Dan opens the "Acme" link (/join#<Acme token>) and accepts, Then he is a member (not admin) of "Acme" only, he sees only "Acme" posts, requesting any "Beta" post by its id returns 404, and the "Acme" token differs from the "Beta" token.
5. Given I am not logged in, When I request the invite link, Then the response is 401 and no invite is created.
6. Given one IP address has already made 10 invite-preview requests in the last 60 seconds (ASSUMED threshold; the preview is the public check that shows only the organization name, e.g. "Acme", before sign-up), When it makes an 11th request, Then the response is 429 with code "RATE_LIMITED", the message "Too many requests. Try again later." and a Retry-After header with a whole number of seconds (the contract says only "integer seconds"; "greater than 0" is ASSUMED), and no organization name is returned; and after the Retry-After seconds have passed, previewing the "Acme" link shows "Acme" and nothing else about the organization.

## Business rules
- Each organization has one persistent invite token, created the first time an admin opens "Invite" and shown again on every later click; clicking never creates a new token (Orchestrator decision, consistent with brief.md ASSUMED). Every admin of the organization sees the same link.
- The link is "<site address>/join#<token>": the token is in the URL fragment, which the browser never sends to any server. The token never appears in any request URL, path or query (ADR-003, brief.md approved addition).
- Preview and accept are POST requests to /invites/preview and /invites/accept with the token in the JSON body (contract, ADR-003). Preview is public (no login) and returns only the organization name.
- The server stores only a hash of the token, not the token (ADR-003); the same link is shown every time because the token is derived again on demand. Testable in F3-2.
- Invite link is for exactly one organization (brief ASSUMED).
- Reusable until revoked; revocation is not in the MVP (brief ASSUMED), so the link stays valid for the life of the MVP.
- Token is long and random (brief ASSUMED); minimum 32 characters (ASSUMED number; the contract token is 43 characters).
- Only admins can see the invite link (brief role table).
- Invite preview is rate limited per IP address (HTTP 429, contract-sourced). ASSUMED (brief.md): 10 requests per rolling 60 seconds per IP address, counted for any token, valid or not.

## UI notes
- Admin-only "Invite" control on the board page; members do not see it.
- After clicking "Invite": read-only text field with the link and a "Copy" button; after copying the button shows "Copied" for about 2 seconds (ASSUMED text and duration; "Invite" and "Copy" labels are also ASSUMED).

## Data touched
- Invite: organization (one per organization), token hash (the token itself is not stored), token version, created time, created by.

## Out of scope
Revoking, regenerating or expiring links, multiple links per organization, sending the link by email, per-link usage limits, listing all links, invite by email address, how the token is stored and kept out of logs (F3-2).

## Assumptions / Questions
- ASSUMED: minimum token length is 32 characters.
- ASSUMED: invite-preview rate limit of 10 requests per rolling 60 seconds per IP address (contract says "rate limited", no number; ADR-002 lists a different default of 20 per 900 s per IP, also ASSUMED and configurable); the limit counts valid and invalid tokens alike. Same threshold and 429 format as F1-2.
- ASSUMED: the Retry-After value is greater than 0 (criterion 6). The contract only says the header holds integer seconds; it gives no minimum.
- ASSUMED: exact UI texts "Invite", "Copy", "Copied" (about 2 seconds); the brief only says the admin generates a link to copy and share.
- DECIDED by Orchestrator (TASK-002 follow-up): one persistent invite token per organization; "Invite" shows the same link every time. DECIDED by Orchestrator (TASK-040): the link is /join#<token>, and preview and accept are POST with the token in the body.
- The logged-out invite flow (sign up or log in first, then the invite is applied) is specified in F3-2 criterion 4 and F2-1.
- Brief status was DRAFT (fast-track) when this was written; brief.md is now APPROVED by the human (2026-10-27), including the invite-token approved addition.
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- HTTP codes: 403 and 404 are named in TASK-002; 429 and the other error codes come from the API contract. 401 is ASSUMED in the contract, so it stays ASSUMED here too.
- Contract check (TASK-040): checked against api-contract.yaml, ADR-002, ADR-003 and data-model.md on the TASK-001 branch (PR #2, head 0459573, Proposed, not on main). It matches: POST /organizations/current/invite (admin, get-or-create, same token every time, 200/401/403), POST /invites/preview and /invites/accept with the token in the body, 429 on preview. Recheck once merged to main.
