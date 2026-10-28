# F1-1: Sign up and log in with email and password
Status: READY
As a user, I want to sign up and log in with my email and password, so that I can access my team's feedback board.

## Acceptance criteria
1. Given no account exists for "alice@example.com", When I sign up with that email, the password "Passw0rd!x" (10 characters) and the display name "Alice", Then an account is created with display name "Alice", I am logged in, my display name "Alice" is shown as my name in the app (ASSUMED location: app header), and I am taken to the "create or join organization" step (ASSUMED text for the step).
2. Given an account already exists for "alice@example.com", When someone signs up with "alice@example.com" or "ALICE@example.com" (with any valid password and display name), Then sign-up is rejected with the message "Email already registered" (ASSUMED text), and no second account exists.
3. Given I am on the sign-up form, When I submit (a) an email without "@" or a domain, or (b) a password shorter than 8 characters, or (c) a display name that is empty, only spaces (ASSUMED: spaces-only counts as empty), or 81 characters long, or (d) an empty email or password, Then the form is rejected with a field-level error naming the field, and no account is created; a display name of exactly 1 or exactly 80 characters is accepted.
4. Given an account exists for "alice@example.com" with password "Passw0rd!x", When I log in with that email and password, Then I am logged in and see my organization's board (or the "create or join organization" step if I have no organization).
5. Given an account exists for "alice@example.com", When I log in with the correct email and a wrong password, or with an email that has no account, Then login is rejected with the same message "Invalid email or password" (ASSUMED text) in both cases, and I am not logged in.
6. Given I am not logged in, When I request any board data (posts, comments, votes, invite link) without a valid login token, Then the response is 401 and no data is returned.

## Business rules
- Email is the unique account identifier; comparison is case-insensitive (ASSUMED).
- Display name is required, 1 to 80 characters (limits from the API contract and data-model.md). Leading and trailing spaces are trimmed before the length check (ASSUMED here: data-model.md says "after trim", but the contract's trimming note lists only title, description, body and name). Display names need not be unique (ASSUMED).
- Other members of my organization see only my display name, never my email (API contract, UserPublic).
- Password minimum length is 8 characters (ASSUMED). Passwords are stored hashed, never returned in any response, never logged (brief, non-functional requirements).
- Authentication is by JWT (brief).
- Session renewal, log out and the rate limit (HTTP 429) on sign-up and login are specified in F1-2.

## UI notes
- Sign-up form: email, password, display name, submit. Login form: email, password, submit. Links to switch between the two.
- Errors appear next to the field (validation) or above the form (duplicate email, bad credentials).

## Data touched
- User: email, display name, password hash, created time, organization (empty until F2).

## Out of scope
Password reset, email verification, social/SSO login, changing the display name after sign-up, avatars, session renewal, log out and rate limiting (these three are in F1-2).

## Assumptions / Questions
- ASSUMED: exact UI/message texts "Email already registered", "Invalid email or password" and the "create or join organization" step name (the brief gives no wording); tests may match on any visible error message instead.
- ASSUMED: display name spaces-only is treated as empty (trimmed); display names are not unique. Display name limits 1-80 are from the contract, not ASSUMED.
- ASSUMED: password minimum 8 characters (the contract also says 8, maximum 128); email comparison case-insensitive; login error message is identical for wrong password and unknown email (does not reveal which emails exist).
- Brief status was DRAFT (fast-track) when this was written; READY status is conditional on brief approval (see handoff Open questions #1).
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- HTTP codes: 403 and 404 are named in TASK-002; 429 and the other error codes come from the API contract; 401 is ASSUMED (the contract lists it but itself marks it ASSUMED). Recheck once the contract is merged to main.
- Contract check (TASK-039): api-contract.yaml (branch feature/TASK-001-stack-and-contracts, not yet on main) now exists. It confirms: sign-up requires email, password and display name (1-80); the texts "Email already registered" and "Invalid email or password" match the contract verbatim. The contract lists 401 for a missing or invalid token but itself marks it ASSUMED, so the 401 criterion here stays ASSUMED. Recheck once it is merged to main.
