# F1-2: Stay logged in, log out, and rate limits on sign-up, login and refresh
Status: READY
Security review: touches authentication (security-bot review required)
As a user, I want my login to be renewed automatically for up to 7 days and to be able to log out so that the session really ends, and I want repeated automated sign-up, login and renewal attempts to be limited, so that my account stays usable and safer.

Traces to brief feature F1 and to the human-approved additions in brief.md ("POST /auth/refresh and POST /auth/logout ... refresh tokens are stored server-side with rotation and a 7-day absolute cap, and logout revokes them"; "Rate limiting (HTTP 429) on signup, login, refresh and invite preview/accept"). Reuse detection of rotated tokens, the CSRF guard (X-Requested-With and Origin) and the bearer-token rule are in F1-3.

## Acceptance criteria
1. Given I am logged in and my browser holds a valid refresh cookie, When the app asks for a new access token (for example on page reload, or after my 15-minute access token expired; the request carries the guard header described in F1-3), Then the response is 200, a new access token valid for 900 seconds is issued for the same user, the refresh token is rotated (the cookie is replaced by a new value), the new cookie's Max-Age is the number of seconds left until my login time plus 7 days (never more than 604800), and I stay logged in without typing my password.
2. Given the refresh cookie is missing, tampered with, expired, or its token was already revoked (for example by logout), When the app asks for a new access token, Then the response is 401 with code "UNAUTHENTICATED", the refresh cookie is cleared (Max-Age 0), no access token is issued, and I am shown the login form (ASSUMED UI behaviour).
3. Given I logged in at time T (by sign-up or log-in) and have kept refreshing, When I ask for a new access token at any moment before T plus 7 days, Then it succeeds and the new cookie expires no later than T plus 7 days (a refresh 6 days after T gives a Max-Age of at most 86400 seconds); and when I ask at or after T plus 7 days, Then the response is 401, the cookie is cleared, I am shown the login form, and logging in again starts a new 7-day period. (Test with a controllable clock; ASSUMED test technique.)
4. Given I am logged in and have copied my refresh cookie value, When I log out (the request carries the guard header described in F1-3), Then the response is 204, every refresh token of that login is revoked on the server, the refresh cookie is cleared (Max-Age 0), I am shown the login form, and when my earlier copy of the cookie is sent for a new access token, Then the response is 401 and no access token is issued; and logging out again with no cookie, an unknown cookie or an already revoked one also returns 204, and no logout request is ever answered with 429 (test with 100 logout requests from one IP in a minute; ASSUMED test value).
5. Given one IP address has already made 10 sign-up requests (or 10 login requests) in the last 60 seconds (ASSUMED threshold), When it makes an 11th request to the same endpoint, Then the response is 429 with code "RATE_LIMITED", the message "Too many requests. Try again later." and a Retry-After header with a whole number of seconds (the contract says only "integer seconds"; "greater than 0" is ASSUMED), and no account is created or logged in, even if the credentials are valid.
6. Given one IP address has already made 10 token-refresh requests in the last 60 seconds (ASSUMED threshold), When it makes an 11th, Then the response is 429 with the same code, message and Retry-After header as criterion 5 (including the ASSUMED "greater than 0") and no access token is issued; and after the Retry-After seconds have passed, a valid refresh request succeeds as in criterion 1.

## Business rules
- Access token lifetime 15 minutes (900 seconds). The refresh token is an HttpOnly cookie that JavaScript cannot read (API contract, ADR-002).
- Each login or sign-up starts a new token family with an absolute 7-day cap counted from login. Rotation (each refresh replaces the refresh token with a successor in the same family) never extends the session beyond login time plus 7 days. After 7 days I must log in again (contract, ADR-002).
- Logout revokes the whole family on the server, clears the cookie, and is idempotent (always 204). It is not rate limited (contract, ADR-002).
- Known limit, not a criterion (ADR-002): an access token issued before logout or revocation stays valid until it expires (at most 15 minutes).
- Rate limit (HTTP 429) applies to sign-up, login and refresh, per IP address (contract). Contract-sourced: code RATE_LIMITED, message "Too many requests. Try again later.", Retry-After header in seconds. ASSUMED (brief.md): 10 requests per rolling 60 seconds per IP address, counted separately for each endpoint, configurable by environment variable; requests count whether or not they succeed.
- The same 429 rule for invite preview and accept is in F3-1 and F3-2.

## UI notes
- A "Log out" control for signed-in users (ASSUMED label). Renewal is silent: no screen is shown (ASSUMED).
- A 429 response is shown as a visible "try again later" message (ASSUMED wording; tests may match on the status code instead).

## Data touched
- Refresh token record kept on the server (only a hash is stored): user, token family, login time (family start), expiry, rotated or revoked state and reason.
- Rate-limit counters (per IP address and endpoint).
- User (read): id, email, display name.

## Out of scope
Rotated-token reuse detection, the CSRF guard header and Origin check, and the bearer-token rule (all F1-3), account lockout and any per-account login limit (out of scope, Orchestrator decision), "log out of all devices", the cap on active families per user (ADR-002, ASSUMED there), revoking access tokens, password reset, rate limits on other endpoints, CAPTCHA.

## Assumptions / Questions
- ASSUMED: rate-limit threshold 10 requests per rolling 60 seconds per IP address per endpoint, as in brief.md. ADR-002 lists different default numbers (sign-up 5 per 3600 s, login 20 per 900 s, refresh 60 per 900 s, also ASSUMED there) that are configurable by environment variables; the stories follow the approved brief. See the TASK-040 handoff, Open questions.
- ASSUMED: the Retry-After value is greater than 0 (criteria 5 and 6). The contract only says the header holds integer seconds; it gives no minimum.
- ASSUMED: "Log out" label, silent renewal, and the redirect to the login form after a failed refresh or logout.
- ASSUMED: the e2e run switches rate limits off with RATE_LIMIT_ENABLED=false (ADR-002 names this variable and says the e2e compose override sets it; the application refuses to start with it off when APP_ENV=production).
- Brief status was DRAFT (fast-track) when this was written; the additions of this story are in brief.md (human-approved additions).
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- HTTP codes: 403 and 404 are named in TASK-002; 429 and the other error codes come from the API contract. 401 is ASSUMED in the contract (conventions and the Unauthorized response both say so), so 401 stays ASSUMED here too.
- Contract check (TASK-040): checked against api-contract.yaml, ADR-002 and data-model.md on the TASK-001 branch (PR #2, head 0459573, status Proposed, not on main). It matches: refresh 200/401/403/429, logout 204/403 (no 429), 7-day absolute cap, rotation, family revoked by logout. 401 is ASSUMED in the contract. Recheck once merged to main.
