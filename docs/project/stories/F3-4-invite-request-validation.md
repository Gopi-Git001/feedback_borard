# F3-4: Invite requests are validated: body shape, content type and order of checks
Status: READY
Security review: touches authentication (security-bot review required)
As an admin who shares an invite link and as a person who opens one, I want the invite preview and accept endpoints to reject a malformed request in a fixed, predictable order and never to fail with a server error or echo what I sent, so that a bad request cannot reveal whether a token exists or break the server.

Traces to the invite request rules in the API contract and ADR-003 ("Invite request tests", PR #2) and to the security-bot findings on PR #5 (re-review of 369411635: the 400 case had no criterion). Split from F3-2, which is full at 6 criteria; F3-2 covers how the token is stored and kept out of URLs and logs and the uniform 404 for a string token, F3-1 what the admin sees.

## Acceptance criteria
1. Given the invite preview endpoint and the invite accept endpoint (accept as a logged-in user without an organization), When the JSON body has no "token" field (for example {}), a "token" that is null or not a string (123, [], {}, true), or any extra field besides "token" (for example {"token": "x", "a": 1}), Then the response is 400 with code "VALIDATION_ERROR", the details name only the field and the rule and never the submitted value, nothing is created, and neither the response nor any log line contains the submitted value (contract: additionalProperties false; ADR-003 tests i and vi).
2. Given the same two endpoints, When the body is empty, malformed JSON (for example "{"), valid JSON that is not an object (an array, a bare string or null), or deeply nested JSON (for example 10,000 nested arrays, under the 64 KB limit), and the Content-Type is "application/json", Then the response is 400 with code "VALIDATION_ERROR", never 500 and never a stack trace (ADR-003 test iv; a body over the nginx limit gets nginx's own 413, accepted risk R14, not tested here).
3. Given the same two endpoints, When a request is sent with a Content-Type that is not "application/json" ("text/plain", "application/x-www-form-urlencoded", "multipart/form-data", or no Content-Type), Then the response is 415 with the standard error body (code "VALIDATION_ERROR") and nothing changes (no membership is created), and the 415 comes after the limiter: when the 10 requests of that IP and endpoint are used up in the window, the answer is 429, not 415 (contract conventions and ADR-004 section 3; accepted risk R10).
4. Given the accept endpoint, When requests are sent that each fail one step, Then the checks run in exactly this order, 429, 415, 401, 400, 404, 409: the request over the limit gets 429 whatever its Content-Type, login or body; a request with a Content-Type that is not JSON gets 415 even without a login; an anonymous request with a JSON body gets 401 even when the body is bad; a logged-in request with a bad body gets 400 even when the token is unknown; a logged-in request with an unknown token gets 404 even when I already belong to an organization; and only a valid token from a user who already belongs to an organization gets 409 "ALREADY_IN_ORGANIZATION" (contract conventions, acceptInvite and ADR-004 section 3: one order of checks for every endpoint).
5. Given the preview endpoint (public, no login), When requests are sent that each fail one step, Then the checks run in this order: 429 first, then 415 for a non-JSON Content-Type, then 400 for a bad body shape, then 404 "INVITE_NOT_FOUND" for a token that is not a valid current token (contract previewInvite: 429, 415, 400, 404; the same one order of checks, only the steps that apply).
6. Given a token that is a string but not a valid current token (the empty string, 1 character, 43 characters of the wrong alphabet, 50,000 characters, spaces only, "../", a quote or SQL text, an emoji, a NUL character "\u0000", or the lone surrogate "\ud800" that is valid JSON but cannot be encoded as UTF-8), When it is sent to preview or accept, Then the response is 404 with code "INVITE_NOT_FOUND" and the message "Invite link is invalid", never 400 and never 500, the body is identical in every case and does not echo the value (ADR-003 tests ii and iii).

## Business rules
- Order of checks on accept: 429 (limiter, before the body is read), 415 (Content-Type), 401 (access token), 400 (body shape), 404 (token lookup), 409 (membership check). On preview: 429, 415, 400, 404 (contract conventions, previewInvite and acceptInvite, ADR-003, ADR-004 section 3).
- The request body is exactly {"token": <string>}; a missing, non-string or extra field is 400, any string token that is not valid is 404 (a 404 never depends on the length or the characters of the string).
- Every request counts toward the per-IP limit of its endpoint, including a 415 or a 400 (accepted risk R10, which applies to invite preview and accept as well as sign-up, login and refresh).
- No response and no log line echoes the submitted value (ADR-003, ADR-004).

## UI notes
- None. The web page does not send a request for a token that does not have the 43-character shape (F2-1 criterion 4); these cases are API tests.

## Data touched
- None written; accept creates a membership only for a valid token (F2-1), which no criterion here reaches.

## Out of scope
Hash-only storage, no token in URLs and logs, the fragment, the logged-out flow and the uniform 404 examples of a realistic wrong token (F3-2), the 429 threshold and format (F1-2, F3-2 criterion 6), the joining rules (F2-1), the 415 on endpoints other than invite preview and accept (F1-8 criterion 3), the body-size 413 from nginx (accepted risk R14).

## Assumptions / Questions
- ASSUMED: the test values in criterion 6 beyond those named in ADR-003; 401 status as in the contract (ASSUMED there).
- ASSUMED: the test technique for the limiter is the one in F1-2 (a small limit N with a long window, N+1 requests); the order tests in criteria 4 and 5 use fresh limits so that no 429 hides a later step.
- The permission case: criterion 4 (401 without a login, 409 for a member of another organization) and criterion 5 (public endpoint, no role case). The error cases are all six criteria.
- HTTP codes: 403 and 404 are named in TASK-002; 400, 401, 409, 415 and 429 come from the API contract and ADR-004; 401 is ASSUMED in the contract.
- Contract check (TASK-040 Attempt 5): checked against api-contract.yaml (previewInvite, acceptInvite, conventions), ADR-003 (Invite request tests) and ADR-004 section 3 and 7 on the TASK-001 branch (PR #2, head 79558a84db0a1c05067683a9be5159fdc8df5254, Proposed, not on main). The contract states the order 429, 415, 401, 400, 404, 409 for accept and 429, 415, 400, 404 for preview; the 415 itself is not listed per operation, like nginx's 413. Recheck once merged to main.
- Brief status: brief.md is APPROVED (human, 2026-10-27).
