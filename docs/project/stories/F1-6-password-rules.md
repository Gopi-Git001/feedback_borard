# F1-6: Password length limits (8 to 128 characters)
Status: READY
Security review: touches authentication (security-bot review required)
As a user, I want clear password length rules at sign-up and login, so that I know which passwords are accepted and the server is protected from oversized passwords.

Traces to brief feature F1 (sign-up with a password; password minimum 8 was ASSUMED in TASK-002). The limits are in the API contract (SignupRequest 8 to 128, LoginRequest 1 to 128) and ADR-002 (maximum 128 protects the 64 MiB password hash). Added in TASK-040 Attempt 3 (security-bot should-fix 8). Other sign-up validation is in F1-1.

## Acceptance criteria
1. Given no account exists for "pw8@example.com", When I sign up with a password of exactly 8 characters (for example "Abcdef1!") and a valid display name, Then the account is created and I am logged in.
2. Given no account exists for "pw128@example.com", When I sign up with a password of exactly 128 characters, Then the account is created and I am logged in, and later logging in with that same 128-character password succeeds.
3. Given no account exists for "pw7@example.com", When I sign up with a password of 7 characters, Then the response is 400 with code "VALIDATION_ERROR", the details name the field "password" and the rule but not the value, no account is created and no refresh cookie is set.
4. Given no account exists for "pw129@example.com", When I sign up with a password of 129 characters, Then the response is 400 with code "VALIDATION_ERROR" as in criterion 3, no account is created, and no password hashing was needed to reject it (the value is refused before hashing, ADR-002).
5. Given an account exists for "alice@example.com", When someone logs in with that email and an empty password, or a password of 129 characters, Then the response is 400 with code "VALIDATION_ERROR" (LoginRequest allows 1 to 128 characters), no cookie is set, and a login with the correct email and a wrong password of 8 to 128 characters is still answered 401 "INVALID_CREDENTIALS" (F1-1 criterion 5).
6. Given I signed up with the password "Passw0rd!x", When I look at every response of sign-up and login and at the stored account record, Then no response contains the password, and the stored value is a hash that does not contain the password (an Argon2id hash, ADR-002).

## Business rules
- Password length 8 to 128 at sign-up; 1 to 128 at login (contract). No composition rules (ADR-002). Characters are counted as characters, tests use plain ASCII characters (ASSUMED; the contract does not say how multi-byte characters are counted).
- The minimum 8 stays as the accepted decision although security guidance asks for more; see accepted risk R17 in ADR-004 section 7.
- Passwords are never returned and never logged (brief, ADR-004; log checks are in F1-4).

## UI notes
- The sign-up form shows a field-level error for a too short or too long password (as F1-1 criterion 3); the exact wording is ASSUMED and tests may match on the field or status instead.

## Data touched
- User: password hash.

## Out of scope
Password strength meters, composition rules, a breached-password check (no blocklist and no reset flow in the MVP: accepted risk R17), password reset or change, other sign-up validation (F1-1), rate limits (F1-2).

## Assumptions / Questions
- ASSUMED: criterion 4 "refused before hashing" is an inference from "reject values over 128 (prevents hash-DoS)" in ADR-002; a test may only assert the 400 and the absence of an account.
- ASSUMED: the example passwords and emails are test data; characters are counted as characters (see Business rules).
- The permission case does not apply (public endpoints); the error cases are criteria 3 to 5.
- Contract difference to note: LoginRequest allows 1 to 128 characters, so a login with a 7-character password is not a validation error but a normal INVALID_CREDENTIALS 401.
- Brief status: brief.md is APPROVED (human, 2026-10-27). This story traces to the human-approved additions and to the security-bot review of PR #5 (comment 6458253424).
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- HTTP codes: 403 and 404 are named in TASK-002; 429 and the other error codes come from the API contract. 401 is ASSUMED in the contract, so it stays ASSUMED here too.
- Contract check (TASK-040 follow-up, re-pointed to main; first written in Attempt 4): SignupRequest password minLength 8 and maxLength 128, LoginRequest password minLength 1 and maxLength 128, 400 VALIDATION_ERROR on sign-up and login, ADR-002 password policy (min 8, max 128, Argon2id). The Orchestrator's 8 and 128 accepted, 7 and 129 rejected match the contract. Checked against the files on main (11497e9a337fdad6d56582077ac3c529d77e3e44, which contains the merges of PR #2 (54f79e4), PR #6 (4a2e084) and PR #7 (11497e9); contract: docs/project/architecture/api-contract.yaml, ADRs: docs/project/decisions/; the files' own status line said Proposed at that commit; since PR #14 the contract, data-model.md and stack.md say Accepted by Orchestrator, and ADR-001 to ADR-004 still say Proposed on main 4f08a039b7d89b0ae4f1cac32cf9fbc1408b16cc; architect-bot is aligning the ADR statuses, as reported by the Orchestrator).
