# F1-9: A request body that is not JSON is refused on organization create, post create, comment create and status change
Status: READY
Security review: touches authentication (security-bot review required)
As a signed-in user of the feedback board, I want the server to refuse a write request whose Content-Type is not JSON, so that a page on another site cannot send a "simple" cross-site form or text request that changes my organization, posts, comments or statuses without a preflight.

Traces to ADR-004 section 3 (a test per endpoint that takes a body, sending "text/plain" and expecting 415 and no row written), the contract conventions (415 for a request with a body that does not send "application/json"), the TASK-040 follow-up from the Orchestrator (item 5, after the post-merge review of PR #6). Sign-up and login are F1-8 criterion 3; invite preview and accept are F3-4 criterion 3.

## Acceptance criteria
1. Given I am logged in and belong to no organization, When I send "POST /organizations" with a body that would otherwise be valid ({"name": "Acme"}) and a Content-Type whose media type is not "application/json" (test data: "text/plain", "application/x-www-form-urlencoded", "multipart/form-data", no Content-Type, "application/jsonp", "application/vnd.api+json" and "text/plain; x=application/json"), Then each response is 415 with the standard error body (code "VALIDATION_ERROR"), no organization and no membership is created, and I still belong to no organization (an endpoint that needs an organization still answers 403 "ORG_REQUIRED").
2. Given I am an admin or member of "Acme", When I send "POST /posts" with a body that would otherwise be valid (a type, a title and a description within the limits) and a Content-Type from the same test data as criterion 1, Then each response is 415 with the standard error body, no post is created (the board and the post count of "Acme" are unchanged), and when I send the same body as "application/json", "application/json; charset=utf-8" or "APPLICATION/JSON" it is accepted with 201 (only the media type is compared, case-insensitively, parameters ignored).
3. Given I am a member of "Acme" and a post of "Acme" exists, When I send "POST /posts/{post_id}/comments" with a body that would otherwise be valid ({"body": "Thanks"}) and a Content-Type from the same test data as criterion 1, Then each response is 415 with the standard error body, no comment is created (the comment list and the comment count of the post are unchanged).
4. Given I am an admin of "Acme" and a post of "Acme" has the status "New", When I send "PATCH /posts/{post_id}/status" with a body that would otherwise be valid ({"status": "Planned"}) and a Content-Type from the same test data as criterion 1, Then each response is 415 with the standard error body and the status of the post is still "New".
5. Given the four endpoints of criteria 1 to 4, When a request with "text/plain" is sent (a) without any login, (b) with a login that is not allowed to do the operation (a member on the status change; a post id that belongs to another organization or does not exist on the comment and status endpoints), and (c) with a body that would be answered 400 as "application/json" (for example an empty title or an unknown status), Then every one of them is answered 415, not 401, 403, 404 or 400 (the 415 check comes after the limiter and before authentication, lookup and body validation), and nothing changes; and as "application/json" the same requests are answered 401, 404 or 403, and 400 as before.
6. Given a request that would be answered 415, When it arrives on "POST /organizations" after the per-user limit of that endpoint is used up, Then the answer is 429 with "Retry-After" (the limiter first); and for post create, comment create and status change, which have no limiter (accepted risk R5, ADR-004 section 7), a 415 is never replaced by a 429.

## Business rules
- A request with a body must send Content-Type "application/json", otherwise 415 with the standard error body (code "VALIDATION_ERROR") and no change. The check is not listed per operation in the contract (like the 413 of nginx) and runs after the limiter and before authentication (contract conventions, ADR-004 section 3).
- Check order for every endpoint (ADR-004 section 3): 429 (limiter), 415 (Content-Type), 401, 400, 404, 409; each endpoint uses the subset that applies. The contract orders a protected endpoint as 401, lookup scoped to the organization (404, also for another organization's resource), then role (403).
- Content-Type comparison (Orchestrator decision, TASK-040 follow-up; the contract and ADR-004 say only "application/json", so the comparison details are ASSUMED there): only the media type is compared, case-insensitively and ignoring parameters. "application/json", "application/json; charset=utf-8" and "APPLICATION/JSON" are accepted. Everything else gets 415: "text/plain", "application/x-www-form-urlencoded", "multipart/form-data", no Content-Type, "application/jsonp", any "+json" type such as "application/vnd.api+json", and "text/plain; x=application/json" (a parameter never changes the media type).
- The contract has no endpoint to update a post or a comment (F4-1: editing posts is after the MVP; F6-1: no comment editing in the MVP), so there is nothing to test for them here. If such endpoints are added, they follow the same rule.
- The endpoints that take no body (refresh, logout, vote toggle, delete post, the GET endpoints, invite link creation) have no Content-Type rule.

## UI notes
- None. A request rejected with 415 is shown like any other error (ASSUMED, as in F1-2).

## Data touched
- None written (a 415 creates and changes nothing); criterion 2 creates one post when it checks that the accepted forms of "application/json" work.

## Out of scope
Sign-up and login (F1-8), invite preview and accept (F3-4), the rate-limit thresholds (F1-2), the 400 rules of each body (F2-1, F4-1, F6-1, F8-1), post and comment update (no such endpoint in the MVP contract), a CSRF token, and the Origin check (F1-3, only refresh and logout have it).

## Assumptions / Questions
- ASSUMED: the media-type comparison of the Orchestrator's rule (case-insensitive, parameters ignored, "+json" types refused) is not stated in the contract or ADR-004; the contract states only that "application/json" is required.
- ASSUMED: for "POST /organizations", the per-user limit (the contract names it as an architect addition, default 10 per 60 s, ASSUMED there) belongs to the limiter step that comes first; the contract does not say whether it is counted before or after the 415, so criterion 6 follows the rule "429 first, then 415". Needs the Orchestrator's confirmation (see the TASK-040 handoff, open question 11).
- ASSUMED: the test environment of F1-2 for criterion 6 (a small limit with a long window, RATE_LIMIT_ENABLED not false).
- The permission case: criterion 5 (no login; a member on the status change; another organization's resource). The error cases are all six criteria.
- HTTP codes: 415 and the check order come from the contract conventions and ADR-004 section 3; 401 is ASSUMED in the contract; 403 and 404 are named in TASK-002 and the contract.
- Contract check (TASK-040 follow-up): checked against the contract conventions, createOrganization, createPost, createComment and updatePostStatus in api-contract.yaml, and ADR-004 section 3, on main (commit 4a2e08423380ee872acf08043bd046adda4c4766, which merged PR #2; contract: docs/project/architecture/api-contract.yaml, ADRs: docs/project/decisions/; the files' own status line still says Proposed). ADR-004 section 3 lists "post and comment create and update"; the contract has no update endpoints.
- Brief status: brief.md is APPROVED (human, 2026-10-27).
