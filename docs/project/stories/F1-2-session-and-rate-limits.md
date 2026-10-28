# F1-2: Stay logged in, log out, and rate limits on sign-up, login and refresh
Status: READY
As a user, I want my login to be renewed automatically while I use the board and to be able to log out, and I want repeated automated sign-up, login and renewal attempts to be limited, so that my account stays usable and safer.

Traces to brief feature F1 and to the additions approved by the human and relayed by the Orchestrator for TASK-039 (rate limiting on login, sign-up, refresh and invite preview; refresh and logout endpoints). brief.md itself does not list them yet (see Assumptions / Questions).

## Acceptance criteria
1. Given I am logged in and my browser holds a valid refresh cookie, When the app asks for a new access token (for example on page reload, or after my 15-minute access token expired), Then a new access token valid for 900 seconds is issued for the same user, the refresh cookie is replaced by a new one, and I stay logged in without typing my password.
2. Given the refresh cookie is missing, tampered with, or older than 7 days, When the app asks for a new access token, Then the response is 401, no access token is issued, and I am shown the login form (ASSUMED UI behaviour).
3. Given I am logged in, When I click "Log out" (ASSUMED label), Then the logout response is 204, the refresh cookie is cleared (Max-Age 0), I am shown the login form, and a later request for a new access token without that cookie returns 401; logging out again with no cookie also returns 204.
4. Given one IP address has already made 10 sign-up requests (or 10 login requests) in the last 60 seconds (ASSUMED threshold), When it makes an 11th request to the same endpoint, Then the response is 429 with code "RATE_LIMITED", the message "Too many requests. Try again later." and a Retry-After header with a whole number of seconds greater than 0, and no account is created or logged in, even if the credentials are valid.
5. Given one IP address has already made 10 token-refresh requests in the last 60 seconds (ASSUMED threshold), When it makes an 11th, Then the response is 429 with the same code, message and Retry-After header as criterion 4 and no access token is issued; and after the Retry-After seconds have passed, a valid refresh request succeeds as in criterion 1.

## Business rules
- Access token lifetime 15 minutes (900 seconds); refresh token lifetime 7 days; the refresh token is an HttpOnly cookie that JavaScript cannot read (API contract, ADR-002).
- Each successful refresh issues a new access token and a new refresh cookie (API contract).
- Rate limit (HTTP 429) applies to sign-up, login and refresh, per IP address. Contract-sourced: code RATE_LIMITED, message "Too many requests. Try again later.", Retry-After header in seconds. ASSUMED: the numeric threshold of 10 requests per rolling 60 seconds per IP address, counted separately for each endpoint; requests count whether or not they succeed.
- Known limit, not a criterion (ADR-002): logout only clears the cookie. An access token issued before logout stays valid until it expires (at most 15 minutes), and a copy of the refresh token stolen before logout stays valid until it expires (at most 7 days). Server-side revocation is a follow-up outside this story.
- The same 429 rule for invite preview is in F3-1.

## UI notes
- A "Log out" control for signed-in users (ASSUMED label). Renewal is silent: no screen is shown (ASSUMED).
- A 429 response is shown as a visible "try again later" message (ASSUMED wording; tests may match on the status code instead).

## Data touched
- Refresh token (cookie only; nothing new is stored on the server in the MVP, ADR-002).
- User (read): id, email, display name.

## Out of scope
Server-side revoking of refresh tokens, "log out of all devices", password reset, rate limits on other endpoints, account lockout, CAPTCHA, a rate limit on logout (the contract lists a 429 for logout, the approved scope does not; see Open questions).

## Assumptions / Questions
- ASSUMED: rate-limit threshold 10 requests per rolling 60 seconds per IP address per endpoint; requests count whether or not they succeed. The contract and ADR-002 say "per IP" but give no number.
- ASSUMED: "Log out" label, silent renewal, and the redirect to the login form after a failed refresh or logout.
- ASSUMED: rate limits must be configurable or relaxed in test environments so the Playwright run (several sign-ups from one IP) does not hit them; the stories do not say how.
- Contract and ADR-002 mismatch to resolve: the approved scope lists rate limiting on login, sign-up, refresh and invite preview; api-contract.yaml also declares 429 on logout. This story covers only the four approved endpoints.
- Brief status was DRAFT (fast-track) when this was written; READY status is conditional on brief approval (see handoff TASK-002 Open questions #1). The additions of this story are human-approved (via Orchestrator, TASK-039) but not yet in brief.md.
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- Contract check (TASK-039): api-contract.yaml (branch feature/TASK-001-stack-and-contracts, not yet on main) defines refresh (200, 401, 429), logout (204, 429), the 429 body and the Retry-After header. Recheck once it is merged to main.
