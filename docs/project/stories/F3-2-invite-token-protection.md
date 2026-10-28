# F3-2: The invite token stays secret
Status: READY
Security review: touches authentication (security-bot review required)
As an admin, I want the invite token to stay out of server logs, request URLs and the database in clear text, so that a leaked log or database dump cannot let strangers join my organization.

Traces to brief feature F3 and to the approved addition "The invite token never appears in a server-visible URL path (fragment plus POST body)" in brief.md. The design is in ADR-003 and the API contract (PR #2). F3-1 covers what the admin sees; this story covers how the token is handled.

## Acceptance criteria
1. Given "Acme" has an invite and its admin has seen the link, When the invites table is inspected directly in the database, Then it contains the SHA-256 hash of the token (64 hex characters) and no column holds the token itself, and when the admin clicks "Invite" again the same link is shown (F3-1 criterion 2).
2. Given the admin opened "Invite", and Bob previewed and accepted the link, When all captured HTTP requests (browser network trace), the application access log and the reverse-proxy access log are searched for the token, Then no request URL (path or query) contains it, no log contains it or any request body, preview and accept were POST requests with the token in the JSON body, and the responses of the invite endpoints (admin invite, preview, accept) carry "Cache-Control: no-store".
3. Given I open "<site address>/join#<token>" in the browser, When the page has read the token, Then the address bar shows "/join" without the "#<token>" part (the fragment is removed from the address bar and browser history entry).
4. Given I am not logged in and I open a valid "/join#<token>" link for "Acme", When the page loads, Then I see the organization name "Acme" (from preview) and a prompt to sign up or log in, the token is held in sessionStorage under the key "pending_invite" while I sign up (email, password, display name) or log in, and after I am logged in the invite is applied automatically, I am a member (not admin) of "Acme", and the "pending_invite" key is deleted; the key is also deleted when accepting fails and when I log out.
5. Given a token that is edited, truncated, too long, too short, contains characters that are not allowed, or does not exist, When it is sent to preview or to accept, Then the response is 404 with code "INVITE_NOT_FOUND" and the message "Invite link is invalid" in every case, never 400, and the response body is identical for all of these cases and does not echo the submitted value.
6. Given a logged-in user without an organization has sent 10 accept requests with invalid tokens in the last 60 seconds from one IP address (ASSUMED threshold), When the same user sends an 11th accept request, Then the response is 429 with code "RATE_LIMITED" and a Retry-After header, and no membership is created even if the token is valid.

## Business rules
- The token is a bearer secret: whoever holds it can join the organization as a member (ADR-003). It never appears in a path or query string, and request bodies of /invites/* and /auth/* are never logged (contract, ADR-003, ADR-004).
- The token is derived on the server from the organization and a server-side key and only its hash is stored; the admin endpoint re-derives it, so the link never changes (ADR-003).
- Malformed, wrong-length and unknown tokens are indistinguishable (always 404, never 400) (contract, ADR-003).
- A logged-out visitor's token is kept in sessionStorage (key "pending_invite") only while signing up or logging in; it is the one deliberate use of Web Storage (ADR-003). The access token is never put in Web Storage (ADR-002).
- Accept needs a login (401 without one, see F2-1 criterion 6); preview is public.
- Accept is rate limited (HTTP 429, contract: per user; brief.md: invite preview/accept, ASSUMED 10 per 60 seconds). The test uses one user from one IP address so both readings give the same result.

## UI notes
- The "/join" page shows the organization name from the preview and "Join" (ASSUMED label) after login, or the sign-up and login choice when logged out (ASSUMED layout).
- Any 404 from preview or accept shows "Invite link is invalid" (text from the contract and ADR-003; the brief gives no wording, so the text is ASSUMED from the brief's point of view).

## Data touched
- Invite: token hash and token version (read), organization.
- Membership: user, organization, role (created on accept).
- sessionStorage key "pending_invite" in the browser (token, temporary).

## Out of scope
Showing the link to admins (F3-1), joining rules such as already belonging to an organization (F2-1), expiry, revoking and regenerating links, removing members, the Referrer-Policy and CSP headers (ADR-003, ADR-004, security tests).

## Assumptions / Questions
- ASSUMED: the rate-limit threshold in criterion 6 (10 per 60 seconds), the "Join" label, the page layout, and that the 429 on accept is counted per user (contract) rather than per IP (brief).
- ASSUMED: criterion 3 is browser behaviour checked in an e2e or component test (ADR-003 SPA requirement: replaceState); the fragment is removed "immediately" (no time limit in ADR-003).
- ASSUMED: the Retry-After value in criterion 6 is greater than 0 (the contract gives only "integer seconds").
- Criterion 2 needs a test setup that can read the application and proxy logs (ADR-003 "Tests (qa-bot)"); how is up to qa-bot and backend-bot.
- HTTP codes: 403 and 404 are named in TASK-002; 429 and the other error codes come from the API contract. 401 is ASSUMED in the contract, so it stays ASSUMED here too.
- Contract check (TASK-040): checked against api-contract.yaml, ADR-003, ADR-002 and data-model.md on the TASK-001 branch (PR #2, head 0459573, Proposed, not on main). ADR-003 itself is Proposed and security-bot has not re-reviewed it yet. Recheck once merged to main.
