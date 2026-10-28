# F3-1: Admin shares the organization's invite link
Status: READY
Security review: touches authentication (security-bot review required)
As an admin, I want to see and copy my organization's invite link and share it, so that teammates can join my organization.

How the token is stored, kept out of request URLs and handled in the browser is in F3-2.

## Acceptance criteria
1. Given I am the admin of "Acme" and no invite token exists yet for "Acme", When I click "Invite", Then I see a full link of the form "<site address>/join#<token>" where the token is in the part after "#" and is at least 32 random characters long (43 characters of A-Z, a-z, 0-9, "_" and "-" with the current design, ADR-003), and a "Copy" action that puts that exact link on my clipboard.
2. Given "Acme" already has an invite token and I have seen its link, When I click "Invite" again after reloading the page, or after logging out and in again (a new session), Then the same link with the same token is shown (unchanged until the server key rotates, F3-3), and still exactly one invite exists for "Acme".
3. Given I am a member (not admin) of "Acme", When I try to get the invite link, Then the response is 403 and no invite is created.
4. Given "Dan" (display name "Dan") is logged in with no organization, and organizations "Acme" and "Beta" each have an invite, When Dan opens the "Acme" link (/join#<Acme token>) and accepts, Then he is a member (not admin) of "Acme" only, he sees only "Acme" posts, requesting any "Beta" post by its id returns 404, and the "Acme" token differs from the "Beta" token.
5. Given I am not logged in, When I request the invite link, Then the response is 401 and no invite is created.
6. Given one IP address has already made 10 invite-preview requests within one 60-second window (ASSUMED threshold: 10 requests per 60-second window per IP per endpoint; window type is an implementation detail and tests must not depend on the boundary; the preview is the public check that shows only the organization name, e.g. "Acme", before sign-up), When it makes an 11th request in that window, Then the response is 429 with code "RATE_LIMITED", the message "Too many requests. Try again later." and a Retry-After header with a whole number of seconds, at least 1 (contract: Retry-After minimum 1), and no organization name is returned; and after the Retry-After seconds have passed, previewing the "Acme" link shows "Acme" and nothing else about the organization.

## Business rules
- Each organization has one persistent invite token, created the first time an admin opens "Invite" and shown again on every later click; clicking never creates a new token, and the link is unchanged until the server key rotates (F3-3; accepted risk R6: no expiry, no revoke) (Orchestrator decision, consistent with brief.md ASSUMED). Every admin of the organization sees the same link.
- The link is "<site address>/join#<token>": the token is in the URL fragment, which the browser never sends to any server. The token never appears in any request URL, path or query (ADR-003, brief.md approved addition).
- Preview and accept are POST requests to /invites/preview and /invites/accept with the token in the JSON body (contract, ADR-003). Preview is public (no login) and returns only the organization name.
- The server stores only a hash of the token, not the token (ADR-003); the same link is shown every time (until the key rotates, F3-3) because the token is derived again on demand. Testable in F3-2.
- Invite link is for exactly one organization (brief ASSUMED).
- Reusable until revoked; revocation is not in the MVP (brief ASSUMED), so the link stays valid for the life of the MVP.
- Token is long and random (brief ASSUMED); minimum 32 characters (ASSUMED number; the contract token is 43 characters).
- Only admins can see the invite link (brief role table).
- Invite preview is rate limited per IP address (HTTP 429, contract-sourced). ASSUMED (brief.md): 10 requests per 60-second window per IP per endpoint (window type is an implementation detail and tests must not depend on the boundary), counted for any token, valid or not (contract); the limiter runs before the token is looked at. Configurable with RATE_LIMIT_INVITE_PREVIEW_PER_IP (<max>/<window_seconds>, default 10/60, ADR-002).

## UI notes
- Admin-only "Invite" control on the board page; members do not see it.
- After clicking "Invite": read-only text field with the link and a "Copy" button; after copying the button shows "Copied" for about 2 seconds (ASSUMED text and duration; "Invite" and "Copy" labels are also ASSUMED).

## Data touched
- Invite: organization (one per organization), token hash (the token itself is not stored), token version, created time, created by.

## Out of scope
Revoking, regenerating or expiring links, rotating the server key (F3-3), multiple links per organization, sending the link by email, per-link usage limits, listing all links, invite by email address, how the token is stored and kept out of logs (F3-2).

## Assumptions / Questions
- ASSUMED: minimum token length is 32 characters.
- ASSUMED: invite-preview rate limit of 10 requests per 60-second window per IP per endpoint, window type an implementation detail (ADR-002 and the contract at head bf3fabb use the same default of 10 per 60 seconds per IP, still ASSUMED there, and describe a sliding window); the limit counts valid and invalid tokens alike; same boundary-independent test technique as F1-2 (small limit N with a long window, request N+1 is the first 429). Same threshold and 429 format as F1-2.
- Retry-After at least 1 is contract-sourced at head bf3fabb (and at 6a961c3; it was ASSUMED at 0459573).
- ASSUMED: exact UI texts "Invite", "Copy", "Copied" (about 2 seconds); the brief only says the admin generates a link to copy and share.
- DECIDED by Orchestrator (TASK-002 follow-up): one persistent invite token per organization; "Invite" shows the same link every time until the server key rotates (F3-3). DECIDED by Orchestrator (TASK-040): the link is /join#<token>, and preview and accept are POST with the token in the body.
- The logged-out invite flow (sign up or log in first, then the invite is applied) is specified in F3-2 criterion 4 and F2-1.
- Brief status was DRAFT (fast-track) when this was written; brief.md is now APPROVED by the human (2026-10-27), including the invite-token approved addition.
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- HTTP codes: 403 and 404 are named in TASK-002; 429 and the other error codes come from the API contract. 401 is ASSUMED in the contract, so it stays ASSUMED here too.
- Contract check (TASK-040 Attempt 4): checked against api-contract.yaml, ADR-002, ADR-003 and data-model.md on the TASK-001 branch (PR #2, head bf3fabbe3339c16b9f87293e7e748ca2fcb0e41a, Proposed, not on main; the values used here are unchanged since 0459573 except Retry-After minimum 1). It matches: POST /organizations/current/invite (admin, get-or-create, same token every time, 200/401/403), POST /invites/preview and /invites/accept with the token in the body, 429 on preview. Recheck once merged to main.
