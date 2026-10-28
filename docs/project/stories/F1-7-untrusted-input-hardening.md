# F1-7: Forged tokens, forged client address and markup in a display name are not trusted
Status: READY
Security review: touches authentication (security-bot review required)
As a user of the feedback board, I want the server to reject forged or altered tokens, to ignore a client address that a caller invents, and to show any name I type as plain text, so that nobody can act as me or get more than the allowed number of requests, and a name can never run code in another person's browser.

Traces to the security-bot review of PR #5 (low findings) and the qa-bot suggestions on PR #5 (comment 6458450359): tampered or "alg: none" access tokens, X-Forwarded-For spoofing and the display name rendered as text were not covered by any criterion. Added in TASK-040 Attempt 4 (a new story, because F1-2 to F1-5 are full at 6 criteria).

## Acceptance criteria
1. Given a valid access token for me, When the signature part is changed (one character) or the payload is edited (for example another user id in "sub" or another organization id in "org") without signing it again, and the result is sent as "Authorization: Bearer" to a protected endpoint such as "who am I", Then the response is 401 (ASSUMED status, as in the contract) and no data is returned.
2. Given a token whose header says "alg": "none" (with an empty signature) or any other algorithm than HS256 (for example "HS384"), or a token signed with a different secret, with otherwise valid claims for an existing user, When it is sent as a bearer token to a protected endpoint, Then the response is 401 and no data is returned (ADR-002: the server accepts HS256 only and never reads the algorithm from the token).
3. Given a token signed with the real secret, When it is expired by more than 30 seconds, or has a wrong issuer or audience, or lacks one of the required claims (exp, iat, sub, iss, aud, typ, jti), or has typ "refresh", Then the response is 401 and no data is returned; and a token that expired less than 30 seconds ago is still accepted (clock leeway of 30 seconds, so a logged-out access token is valid for at most 15 min 30 s: contract, ADR-002, accepted risks R2 and R13).
4. Given I am logged in, When the refresh request carries a refresh cookie whose value was altered (one character of the signature changed, or a refresh token signed with a different secret), with the correct guard header, Then the response is 401, no access token is issued, the cookie is cleared (contract: invalid cookie), and my real session is not revoked by this request (a request that carries my unaltered cookie still works afterwards).
5. Given the per-IP login limit is set to a small N with a long window (technique of F1-2), When I send N+1 login requests through the web server from one client, each with a different "X-Forwarded-For" header value that I invent, Then request N+1 is the first 429 (the invented values do not give a new rate-limit bucket, because the web server overwrites the header with the real client address and the backend trusts it only from the proxy addresses in TRUSTED_PROXY_IPS); and the same holds when the requests reach the backend directly from a peer that is not a trusted proxy (the header is ignored).
6. Given I sign up with the display name "<img src=x onerror=alert(1)>" (a valid length), When my name is shown (in the page header or user menu, as author of a post and of a comment, and anywhere else a name appears), Then the page shows the characters exactly as typed, no HTML element is created from them and no script runs (in the e2e run no dialog event fires and the page has no "img" element with src "x"), and the API returns the name unchanged as a JSON string apart from trimming of leading and trailing spaces (ADR-004: user text is rendered as text only).

## Business rules
- The access token is verified with algorithms=["HS256"] only, issuer "feedback-board", audience "feedback-board-api", leeway 30 seconds, and the required claims exp, iat, sub, iss, aud, typ and jti; typ must be "access" (contract, ADR-002).
- The refresh token is accepted only from the cookie on refresh and logout; a refresh token as bearer token is F1-3 criterion 5.
- The client address for rate limiting comes from the right-most entry of X-Forwarded-For, set by exactly one trusted proxy (nginx); other peers' X-Forwarded-For is ignored; IPv6 addresses are grouped by /64 (contract, ADR-002; accepted risk R15).
- All user-supplied text is rendered as text only: no dangerouslySetInnerHTML, no Markdown or HTML rendering, no automatic links (ADR-004).

## UI notes
- None. A rejected token on a page shows the login form again (ASSUMED, as in F1-2).

## Data touched
- None written by criteria 1 to 3 and 5; criterion 4 changes nothing (the family is not revoked by an altered cookie); criterion 6 stores the display name as typed (trimmed).

## Out of scope
Rate-limit thresholds and the 429 format (F1-2), refresh reuse detection, the guard header and the bearer rule for refresh tokens (F1-3), cookie flags and headers (F1-4), the display-name length rule (F1-1), a content security policy test for script injection beyond the page header check (F1-4 criterion 6), IP spoofing through a second proxy in front of nginx (accepted risk R15: exactly one proxy is assumed).

## Assumptions / Questions
- ASSUMED: the 401 status for forged tokens (the 401 rule is ASSUMED in the contract); the example payload edits and the example name are test data.
- ASSUMED: criterion 3 needs tokens that a test can build with the test secret (JWT_SECRET of the test environment) and a clock the test controls or tokens with fixed past exp values; how is up to qa-bot and backend-bot.
- ASSUMED: criterion 4 assumes the contract's 401 with cleared cookie for an invalid cookie (refresh operation); criterion 5 reuses the test technique and environment variables of F1-2 and needs RATE_LIMIT_ENABLED not false.
- The permission case: criteria 1 to 4 are the forged-identity (401) cases; there is no role case for a story about untrusted input. The error cases are all six criteria.
- Contract check (TASK-040 Attempt 4): api-contract.yaml, ADR-002 (JWT, client IP), ADR-004 (text rendering) on the TASK-001 branch (PR #2, head bf3fabbe3339c16b9f87293e7e748ca2fcb0e41a, Proposed, not on main). Recheck once merged to main.
- Brief status: brief.md is APPROVED (human, 2026-10-27).
