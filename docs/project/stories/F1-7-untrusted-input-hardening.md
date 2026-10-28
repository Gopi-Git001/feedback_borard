# F1-7: Forged tokens, a swapped token type and a deleted membership are not trusted
Status: READY
Security review: touches authentication (security-bot review required)
As a user of the feedback board, I want the server to reject forged, altered or stale tokens, and to refuse an access token whose membership no longer exists, so that nobody can act as me or keep access they no longer have.

Traces to the security-bot review of PR #5 (low findings) and the qa-bot suggestions on PR #5 (comment 6458450359): tampered or "alg: none" access tokens were not covered by any criterion. Added in TASK-040 Attempt 4 (a new story, because F1-2 to F1-5 are full at 6 criteria). In TASK-040 Attempt 5 the invented X-Forwarded-For and the markup-in-text criteria moved to F1-8, and this story gained criterion 5 (an access token sent as the refresh cookie) and criterion 6 (a token whose membership was deleted), both from the security-bot low findings on PR #2.

## Acceptance criteria
1. Given a valid access token for me, When the signature part is changed (one character) or the payload is edited (for example another user id in "sub" or another organization id in "org") without signing it again, and the result is sent as "Authorization: Bearer" to a protected endpoint such as "who am I", Then the response is 401 (ASSUMED status, as in the contract) and no data is returned.
2. Given a token whose header says "alg": "none" (with an empty signature) or any other algorithm than HS256 (for example "HS384"), or a token signed with a different secret, with otherwise valid claims for an existing user, When it is sent as a bearer token to a protected endpoint, Then the response is 401 and no data is returned (ADR-002: the server accepts HS256 only and never reads the algorithm from the token).
3. Given a token signed with the real secret, When it is expired by more than 30 seconds, or has a wrong issuer or audience, or lacks one of the required claims (exp, iat, sub, iss, aud, typ, jti), or has typ "refresh", Then the response is 401 and no data is returned; and a token that expired less than 30 seconds ago is still accepted (clock leeway of 30 seconds, so a logged-out access token is valid for at most 15 min 30 s: contract, ADR-002, accepted risks R2 and R13).
4. Given I am logged in, When the refresh request carries a refresh cookie whose value was altered (one character of the signature changed, or a refresh token signed with a different secret), with the correct guard header, Then the response is 401, no access token is issued, the cookie is cleared (contract: invalid cookie), and my real session is not revoked by this request (a request that carries my unaltered cookie still works afterwards).
5. Given I hold a valid, unexpired access token, When its value is sent as the refresh cookie ("refresh_token") to the refresh endpoint with the correct guard header, Then the response is 401 with code "UNAUTHENTICATED", no access token is issued, the response clears the cookie (the token has the wrong type, so it is an invalid refresh cookie: contract, ADR-002), and the access token I sent still works as a bearer token until it expires.
6. Given a valid, unexpired access token whose "org" claim names "Acme", and the membership of that user in "Acme" has been deleted (the test removes the row), When the token is sent as "Authorization: Bearer" to an organization endpoint such as the board, Then the response is 401 and no data is returned (the membership is read from the database on every request, so the claim alone is not enough: contract; same rule as F2-2 criterion 4, tested here from the forged-identity side; the 401 status is ASSUMED as in the contract).

## Business rules
- The access token is verified with algorithms=["HS256"] only, issuer "feedback-board", audience "feedback-board-api", leeway 30 seconds, and the required claims exp, iat, sub, iss, aud, typ and jti; typ must be "access" (contract, ADR-002).
- The refresh token is accepted only from the cookie on refresh and logout; a refresh token as bearer token is F1-3 criterion 5, and an access token as refresh cookie is criterion 5 here. Every refresh 401 except one clears the cookie (rule in F1-3 Business rules).
- Role and membership are read from the database on each request; a token alone never proves membership (contract, ADR-002). The token itself stays valid for at most 15 min 30 s after logout, reuse detection or eviction (accepted risks R2 and R13).

## UI notes
- None. A rejected token on a page shows the login form again (ASSUMED, as in F1-2).

## Data touched
- None written by criteria 1 to 3 and 6; criteria 4 and 5 change nothing (the family is not revoked by an altered or wrongly typed cookie; the test removes a membership row for criterion 6 only as test setup).

## Out of scope
Rate-limit thresholds and the 429 format (F1-2), the invented X-Forwarded-For, the limiter under simultaneous requests and the display-name, organization-name, post and comment text rendering (F1-8), refresh reuse detection, the guard header and the bearer rule for refresh tokens (F1-3), cookie flags and headers (F1-4).

## Assumptions / Questions
- ASSUMED: the 401 status for forged tokens and for a deleted membership (the 401 rule is ASSUMED in the contract); the example payload edits are test data.
- ASSUMED: criterion 3 needs tokens that a test can build with the test secret (JWT_SECRET of the test environment) and a clock the test controls or tokens with fixed past exp values; how is up to qa-bot and backend-bot. Criterion 6 needs a test that deletes a membership row (as F2-2 criterion 4).
- ASSUMED: criteria 4 and 5 assume the contract's 401 with cleared cookie for an invalid cookie (refresh operation: missing, invalid, wrong type or expired).
- The permission case: criteria 1 to 6 are the forged-identity and stale-identity (401) cases; there is no role case for a story about untrusted input. The error cases are all six criteria.
- Contract check (TASK-040 follow-up, re-pointed to main; first written in Attempt 4): api-contract.yaml, ADR-002 (JWT, membership) on main (commit 4a2e08423380ee872acf08043bd046adda4c4766, which merged PR #2; contract: docs/project/architecture/api-contract.yaml, ADRs: docs/project/decisions/; the files' own status line still says Proposed).
- Brief status: brief.md is APPROVED (human, 2026-10-27).
