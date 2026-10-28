# F2-2: A user without an organization is refused organization data
Status: READY
Security review: touches authentication (security-bot review required)
As a user who has just signed up and belongs to no organization, I want to be refused clearly when I ask for organization data and be able to use it right after I create or join an organization, so that nothing of another team leaks and I know what to do next.

Traces to the leftover "403 ORG_REQUIRED" (TASK-039 Q11, TASK-040 handoff Q4a). The rule is in the contract conventions (marked ASSUMED there: no story or brief text defines it); this story makes it testable and keeps the ASSUMED label. Added in TASK-040 Attempt 3.

## Acceptance criteria
1. Given I am logged in and belong to no organization, When I request the board, create a post, comment, vote, change a status, delete a post, or ask for the invite link, Then each response is 403 with code "ORG_REQUIRED" (ASSUMED code), no data is returned and nothing is created.
2. Given I am logged in and belong to no organization, When I create an organization, preview an invite link, accept an invite link, or call the auth endpoints, Then none of these is refused with "ORG_REQUIRED" (they work as in F2-1, F3-1 and F1-2).
3. Given I just created the organization "Acme" (or joined it), When I use the new access token returned by that action to request the board, Then the response is 200 and shows "Acme" posts, without logging in again; and the access token I held before still gets "ORG_REQUIRED" on the board (the client must replace its token).
4. Given an access token that names an organization but for which no membership exists (for example the membership was removed in the database for the test), When I use it on any organization endpoint, Then the response is 401 (the contract requires the membership row; the 401 status itself is ASSUMED) and no data is returned.
5. Given I send no access token at all, When I request the board, Then the response is 401, not "ORG_REQUIRED" (authentication is checked first).
6. Given I am a plain member (not admin) of "Acme" and the organization "Globex" has a post, When I change the status of that Globex post or delete it, Then the response is 404 (not 403) with code "POST_NOT_FOUND", and nothing in Globex changes; and when I do the same on an Acme post, Then the response is 403 with code "FORBIDDEN" and the post is unchanged (contract order of checks: 401, then the lookup inside my own organization giving 404, then the role check giving 403, so a role error never reveals that another organization's resource exists; same rule as F8-1 and F9-1).

## Business rules
- Order of checks: authentication (401), then organization membership (ORG_REQUIRED 403), then resource lookup inside the caller's organization (404), then role (403) (contract conventions, "Order of checks"; the 404-before-403 order is tested in criterion 6 here and in F8-1 and F9-1). The contract lists the order as 401, 404, 403; the position of ORG_REQUIRED between 401 and 404 is ASSUMED (ORG_REQUIRED itself is ASSUMED in the contract).
- A user with no organization may call only the auth endpoints, POST /organizations, POST /invites/preview and POST /invites/accept (contract, ASSUMED there).
- The access token carries the organization only after creating or joining one; the action returns a new access token (contract).

## UI notes
- A signed-in user with no organization sees the "create or join organization" step (F2-1), not the board; the message for ORG_REQUIRED is not shown in normal use (ASSUMED).

## Data touched
- Membership (read), access token claims (read).

## Out of scope
Multiple organizations per user, leaving an organization, removing members, the 401 status itself (ASSUMED in the contract), role checks (F3-1, F8-1, F9-1).

## Assumptions / Questions
- ASSUMED: the code "ORG_REQUIRED" and the whole rule (contract: "ASSUMED: no story or brief text defines it"); criteria 1 and 3 change if the Orchestrator picks another code. 401 is ASSUMED in the contract (criteria 4 and 5).
- ASSUMED test setup for criterion 4: the membership row is deleted directly in the test database.
- The permission case is criterion 1 (a signed-in user without organization is not allowed to use organization endpoints); the error case is criteria 4 and 5.
- Brief status: brief.md is APPROVED (human, 2026-10-27). This story traces to the human-approved additions and to the security-bot review of PR #5 (comment 6458253424).
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- HTTP codes: 403 and 404 are named in TASK-002; 429 and the other error codes come from the API contract. 401 is ASSUMED in the contract, so it stays ASSUMED here too.
- Contract check (TASK-040 follow-up, re-pointed to main; first written in Attempt 4): the conventions text on ORG_REQUIRED and the membership row, the Forbidden response, and the list of endpoints allowed without an organization. Checked against the files on main (11497e9a337fdad6d56582077ac3c529d77e3e44, which contains the merges of PR #2 (54f79e4), PR #6 (4a2e084) and PR #7 (11497e9); contract: docs/project/architecture/api-contract.yaml, ADRs: docs/project/decisions/; the files' own status line still says Proposed).
