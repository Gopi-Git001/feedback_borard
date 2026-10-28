# F1-1: Sign up and log in with email and password
Status: READY
Security review: touches authentication (security-bot review required)
As a user, I want to sign up and log in with my email and password, so that I can access my team's feedback board.

## Acceptance criteria
1. Given no account exists for "alice@example.com", When I sign up with that email, the password "Passw0rd!x" (10 characters) and the display name "Alice", Then an account is created with display name "Alice", I am logged in, my display name "Alice" is shown as my name in the app (ASSUMED location: app header), and I am taken to the "create or join organization" step (ASSUMED text for the step).
2. Given an account already exists for "alice@example.com", When someone signs up with "alice@example.com" or "ALICE@example.com" (with any valid password and display name), Then sign-up is rejected with the message "Email already registered" (text from the contract: Conflict response, EMAIL_TAKEN; not in the brief), and no second account exists.
3. Given I am on the sign-up form, When I submit (a) an email without "@" or a domain, or (b) a password shorter than 8 characters, or (c) a display name that is empty, only spaces (leading and trailing spaces are trimmed first, so spaces-only counts as empty), or 81 characters long after trimming, or (d) an empty email or password, Then the form is rejected with a field-level error naming the field, and no account is created; a display name of exactly 1 or exactly 80 characters is accepted.
4. Given an account exists for "alice@example.com" with password "Passw0rd!x", When I log in with that email and password, Then I am logged in and see my organization's board (or the "create or join organization" step if I have no organization).
5. Given an account exists for "alice@example.com", When I log in with the correct email and a wrong password, or with an email that has no account, Then login is rejected with the same message "Invalid email or password" (text from the contract: login operation, INVALID_CREDENTIALS; not in the brief) in both cases, and I am not logged in.
6. Given I am not logged in, When I request any board data (posts, comments, votes, invite link) without a valid login token, Then the response is 401 and no data is returned.

## Business rules
- Email is the unique account identifier; comparison is case-insensitive (ASSUMED).
- Display name is required, 1 to 80 characters, after trimming leading and trailing spaces; the trimmed value is stored (API contract conventions and SignupRequest, data-model.md; brief.md still calls the trimming ASSUMED). Display names need not be unique (ASSUMED).
- Other members of my organization see only my display name, never my email (API contract, UserPublic).
- Password length is 8 to 128 characters (contract SignupRequest, ADR-002; the minimum 8 was ASSUMED in TASK-002; the boundaries 8, 128, 7 and 129 are criteria in F1-6). Passwords are stored hashed, never returned in any response, never logged (brief, non-functional requirements; log hygiene is tested in F1-4).
- Authentication is by JWT (brief).
- Session renewal, log out and the rate limit (HTTP 429) on sign-up and login are specified in F1-2; refresh-token reuse, the request guard and the bearer-token rule are in F1-3; cookie flags, security headers and log hygiene are in F1-4; concurrency and the session cap are in F1-5; password length boundaries are in F1-6.

## UI notes
- Sign-up form: email, password, display name, submit. Login form: email, password, submit. Links to switch between the two.
- Errors appear next to the field (validation) or above the form (duplicate email, bad credentials).

## Data touched
- User: email, display name, password hash, created time, organization (empty until F2).

## Out of scope
Password reset, email verification, social/SSO login, changing the display name after sign-up, avatars, account lockout and any per-account login limit (out of scope, not offered; accepted risks R1, R3, R4 and R17, see ADR-004 section 7: guessing against one account is limited only by the per-IP limit in F1-2, passwords have a minimum of 8 and there is no breached-password check, R17).

## Assumptions / Questions
- Message texts "Email already registered" (contract: Conflict response, EMAIL_TAKEN) and "Invalid email or password" (contract: login operation description, INVALID_CREDENTIALS) are contract-sourced; the contract on main still states status Proposed and the brief gives no wording. ASSUMED: the "create or join organization" step name; tests may match on any visible error message instead.
- Display name limits 1-80 and trimming (spaces-only is empty) are from the contract (brief.md calls trimming ASSUMED); display names are not unique (ASSUMED).
- Password length 8 to 128 is contract-sourced (SignupRequest; checked on main); ASSUMED: email comparison case-insensitive; login error message is identical for wrong password and unknown email (does not reveal which emails exist).
- Brief status was DRAFT (fast-track) when this was written; READY status is conditional on brief approval (see handoff Open questions #1).
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- HTTP codes: 403 and 404 are named in TASK-002; 429 and the other error codes come from the API contract; 401 is ASSUMED (the contract lists it but itself marks it ASSUMED). Checked against the contract on main (11497e9a337fdad6d56582077ac3c529d77e3e44, which contains the merges of PR #2 (54f79e4), PR #6 (4a2e084) and PR #7 (11497e9)).
- Contract check (TASK-040 follow-up, re-pointed to main; first written in Attempt 4): checked against api-contract.yaml on main (11497e9a337fdad6d56582077ac3c529d77e3e44, which contains the merges of PR #2 (54f79e4), PR #6 (4a2e084) and PR #7 (11497e9); contract: docs/project/architecture/api-contract.yaml, ADRs: docs/project/decisions/; the files' own status line still says Proposed). It confirms: sign-up requires email, password (8-128) and display name (1-80, trimmed first); the texts "Email already registered" and "Invalid email or password" match the contract verbatim. 401 is ASSUMED in the contract, so the 401 criterion here stays ASSUMED.
