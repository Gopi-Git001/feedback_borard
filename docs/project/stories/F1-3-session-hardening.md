# F1-3: Harden the session: refresh-token reuse, request guard and login attempt limit
Status: READY
Security review: touches authentication (security-bot review required)
As a user, I want a stolen or replayed refresh token, a forged cross-site request and password guessing to be stopped, so that nobody else can keep or take over my session.

Traces to brief feature F1 and to the human-approved additions in brief.md (refresh tokens stored server-side with rotation and a 7-day absolute cap; rate limiting on login). The behaviour is specified in the API contract, ADR-002 and ADR-004 (PR #2); the criteria below turn it into testable steps. Normal refresh, logout and the per-IP rate limits are in F1-2.

## Acceptance criteria
1. Given I logged in and refreshed once, so that my refresh token T1 was rotated into T2 more than 10 seconds ago, When T1 is presented again for a new access token (for example by someone who copied it), Then the response is 401, the whole token family of that login is revoked, the cookie is cleared, and when T2 is then presented, Then it also returns 401 and I must log in again.
2. Given my refresh token T1 was rotated into T2 less than 10 seconds ago (REFRESH_REUSE_LEEWAY_SECONDS, default 10, as in the contract; two browser tabs racing), When T1 is presented again, Then the response is 401, no access token is issued, the family is not revoked, and T2 still works for a new access token.
3. Given I am logged in with a valid refresh cookie, When a refresh or a logout request arrives without the header "X-Requested-With: feedback-board", or with any other value in that header, Then the response is 403 with code "FORBIDDEN", no access token is issued, the cookie is not changed, the token family is not revoked, and a later request with the correct header succeeds.
4. Given I am logged in with a valid refresh cookie, When a refresh or a logout request carries the correct header but an Origin header that is not the configured frontend origin (for example "https://evil.example"), Then the response is 403 with code "FORBIDDEN" and nothing changes; and when the Origin equals the configured frontend origin, or no Origin header is sent, with the correct header, Then refresh returns 200 and logout returns 204.
5. Given an email address (registered or not) has had 5 failed login attempts in the last 900 seconds (ASSUMED threshold, ADR-002 default; the brief gives no per-account number), When a 6th login attempt for that email arrives, even with the correct password, Then the response is 429 with code "RATE_LIMITED", a Retry-After header, and no one is logged in, and the response for an email that has no account is the same 429.
6. Given I hold a refresh token value (the HttpOnly cookie's JWT), When I send it as "Authorization: Bearer" to a protected endpoint such as "who am I", Then the response is 401 (ASSUMED status; the contract says only that a refresh token is never accepted as a bearer token) and no data is returned.

## Business rules
- A token family is the chain of refresh tokens that starts at one login. Reuse of a rotated or revoked token revokes the whole family and answers 401; within 10 seconds after a rotation it answers 401 without revoking (contract, ADR-002, data-model.md).
- The cookie endpoints (refresh and logout) need the header "X-Requested-With: feedback-board" and, when an Origin header is present, it must equal the configured frontend origin; otherwise 403 "FORBIDDEN" with no state change (contract, ADR-002, ADR-004). This is in addition to the cookie being SameSite=Strict.
- Login has a per-IP limit (F1-2) and a per-account limit on failed attempts. The per-account limit counts attempts for unknown emails too, so the response never reveals whether an email exists (ADR-002). Accepted trade-off in ADR-002: an attacker can lock a victim's login for up to 15 minutes.
- Only an access token is accepted as a bearer token; the refresh token is accepted only from the cookie on refresh and logout (contract, ADR-002).

## UI notes
- None beyond F1-2: a failed or rejected request shows the login form again (ASSUMED); a 429 shows a "try again later" message (ASSUMED wording).

## Data touched
- Refresh token records (server side, hash only): revoked state and reason (reuse detected, logout).
- Rate-limit counters (per account key, hash of the lower-cased email).

## Out of scope
Password change or reset revoking all sessions (no such flow in the MVP, ADR-002), CAPTCHA, permanent account lockout, the 10-active-families cap (ASSUMED in ADR-002), access-token revocation (an issued access token works up to 15 minutes), CORS rules.

## Assumptions / Questions
- ASSUMED: per-account login threshold 5 failed attempts per 900 seconds (ADR-002 default; configurable by RATE_LIMIT_LOGIN_PER_ACCOUNT; not in brief.md). Whether a 6th attempt with the correct password is blocked follows from ADR-002's lock-out remark and is ASSUMED to be tested this way.
- ASSUMED: 401 for a refresh token used as a bearer token (criterion 6); the 401 rule itself is ASSUMED in the contract.
- ASSUMED: the Retry-After value in criterion 5 is greater than 0 (the contract gives only "integer seconds").
- Test note: the e2e run uses RATE_LIMIT_ENABLED=false (ADR-002), so criterion 5 is a backend test with small limits set by environment variables, not an e2e step.
- HTTP codes: 403 and 404 are named in TASK-002; 429 and the other error codes come from the API contract. 401 is ASSUMED in the contract, so it stays ASSUMED here.
- Contract check (TASK-040): checked against api-contract.yaml, ADR-002, ADR-004 and data-model.md on the TASK-001 branch (PR #2, head 0459573, Proposed, not on main). Recheck once merged to main.
- Brief status was DRAFT (fast-track) when the F-stories were written; the additions behind this story are in brief.md.
