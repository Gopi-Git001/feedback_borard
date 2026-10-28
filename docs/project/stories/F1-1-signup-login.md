# F1-1: Sign up and log in with email and password
Status: READY
As a user, I want to sign up and log in with my email and password, so that I can access my team's feedback board.

## Acceptance criteria
1. Given no account exists for "alice@example.com", When I sign up with that email and the password "Passw0rd!x" (10 characters), Then an account is created, I am logged in, and I am taken to the "create or join organization" step (ASSUMED text for the step).
2. Given an account already exists for "alice@example.com", When someone signs up with "alice@example.com" or "ALICE@example.com", Then sign-up is rejected with the message "Email already registered" (ASSUMED text), and no second account exists.
3. Given I am on the sign-up form, When I submit (a) an email without "@" or a domain, or (b) a password shorter than 8 characters, or (c) an empty email or password, Then the form is rejected with a field-level error naming the field, and no account is created.
4. Given an account exists for "alice@example.com" with password "Passw0rd!x", When I log in with that email and password, Then I am logged in and see my organization's board (or the "create or join organization" step if I have no organization).
5. Given an account exists for "alice@example.com", When I log in with the correct email and a wrong password, or with an email that has no account, Then login is rejected with the same message "Invalid email or password" (ASSUMED text) in both cases, and I am not logged in.
6. Given I am not logged in, When I request any board data (posts, comments, votes, invite link) without a valid login token, Then the response is 401 and no data is returned.

## Business rules
- Email is the unique account identifier; comparison is case-insensitive (ASSUMED).
- Password minimum length is 8 characters (ASSUMED). Passwords are stored hashed, never returned in any response, never logged (brief, non-functional requirements).
- Authentication is by JWT (brief).

## UI notes
- Sign-up form: email, password, submit. Login form: email, password, submit. Links to switch between the two.
- Errors appear next to the field (validation) or above the form (duplicate email, bad credentials).

## Data touched
- User: email, password hash, created time, organization (empty until F2).

## Out of scope
Password reset, email verification, social/SSO login, logout/session expiry rules, rate limiting of login attempts.

## Assumptions / Questions
- ASSUMED: exact UI/message texts "Email already registered", "Invalid email or password" and the "create or join organization" step name (the brief gives no wording); tests may match on any visible error message instead.
- ASSUMED: password minimum 8 characters; email comparison case-insensitive; login error message is identical for wrong password and unknown email (does not reveal which emails exist).
- Brief status was DRAFT (fast-track) when this was written; READY status is conditional on brief approval (see handoff Open questions #1).
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- API contract (TASK-001) did not exist yet. The TASK-002 spec names 403 (member on admin action) and 404 (cross-organization access); stories use no other HTTP code. ASSUMED: 401 for a missing or invalid login token (standard meaning; named in neither TASK-002 nor the brief). Recheck all codes against the contract when it lands.
