# E2E-1: End-to-end journey (sign up, create org, invite, post, vote, comment, change status)
Status: READY
Security review: touches authentication (security-bot review required)
As a team lead and her teammate, we want to go from a new account to a triaged piece of feedback in one flow, so that we know the Team Feedback Board works end to end.

This story is the Playwright e2e target. Alice = first user (becomes admin). Bob = second user (becomes member). Carol = user of a different organization (isolation check). Each user signs up with email, password and a display name equal to the first name ("Alice", "Bob", "Carol"); other users see these display names, never emails.

## Acceptance criteria
1. (F1) Given no accounts exist, When Alice signs up with "alice@example.com", password "Passw0rd!x" and display name "Alice", Then she is logged in, her display name "Alice" is shown as her name in the app (ASSUMED location: app header), and she sees the "create or join organization" step (ASSUMED text); and the browser's cookie jar (Playwright context.cookies()) holds the "refresh_token" cookie with HttpOnly, SameSite=Strict, Path=/api/v1/auth and a Max-Age of at most 604800, while document.cookie does not list it (Secure is set unless the e2e environment runs with COOKIE_SECURE=false; F1-4 criterion 1).
2. (F2) Given Alice is logged in with no organization, When she creates the organization "Acme", Then she is admin of "Acme" and sees an empty board with the text "No posts yet" (ASSUMED text).
3. (F3, F2) Given Alice is admin of "Acme", When she clicks "Invite" (ASSUMED label) and sees a link of the form "<site address>/join#<token>", and Bob signs up as "bob@example.com" with display name "Bob" and opens that /join#<token> link and accepts, Then Bob is a member (not admin) of "Acme" and sees the same empty board.
4. (F4, F7) Given Bob is a member of "Acme", When he creates a post with title "Dark mode", a description, and type "idea", Then the post appears on the board with status "New" and 0 votes, visible to both Alice and Bob, with the author shown as "Bob".
5. (F5) Given the post "Dark mode" has 0 votes, When Alice and then Bob each upvote it once, Then it shows 2 votes; and when Bob clicks upvote again, Then it shows 1 vote.
6. (F6) Given the post "Dark mode" has no comments, When Bob adds the comment "Would help at night.", Then Alice sees that comment under the post, with the author shown as "Bob" (display name, not email).
7. (F8) Given the post is "New", When Alice (admin) sets its status to "Planned", Then both Alice and Bob see "Planned" on the post and on the board, and filtering the board by status "Planned" lists "Dark mode".
8. (Permission, F8 and F9) Given Bob is a member, When he tries to change the status or delete "Dark mode", Then each action returns 403 and the post is unchanged.
9. (Isolation, F2 and F7) Given Carol signed up (display name "Carol") and created the organization "Beta", When she opens the board and requests the "Dark mode" post by its id, Then her board shows "No posts yet" (ASSUMED text) and the post request returns 404.
10. (Token secrecy, F3) Given steps 1 to 9 are complete, When the browser network trace of the whole run (Alice, Bob and Carol) is searched for the "Acme" invite token, Then no request URL (path or query) contains it, no request carries a "Referer" header containing it, the only requests that carry it are the POST requests to /invites/preview and /invites/accept (token in the body), the browser console output contains neither the token nor a Content-Security-Policy violation, localStorage and sessionStorage hold no invite token, no access token and no refresh token after the run (the only allowed entry is the documented "pending_invite" sessionStorage key, and only while a logged-out visitor signs up or logs in, F3-2 criterion 4; it is gone after accept), and after opening a /join#<token> link the page address (location.href) no longer contains "#<token>".

## Business rules
- Steps map one to one to the Orchestrator's journey: sign up (1), create org (2), invite a second user (3), post (4), vote (5), comment (6), change status (7). Criteria 8 and 9 are the permission and isolation checks required by TASK-002. Criterion 10 is the invite-token and browser-leak check added in TASK-040 (ADR-003: no token in any request URL, no Referer, no console or Web Storage leak; extended in Attempt 3). Criterion 1 also asserts the refresh cookie flags (F1-4 criterion 1).
- All rules of F1-F9 apply; this story adds no new rules.
- Test environment: the run is done with RATE_LIMIT_ENABLED=false (ADR-002 says the e2e compose override sets it; the Orchestrator asked for it in TASK-040), because all sign-ups come from one IP address. The rate-limit criteria (F1-2, F3-1, F3-2) are not part of this journey; the application refuses to start with this setting when APP_ENV=production.

## UI notes
- Uses the screens of F1-F9 only. Two browser contexts (Alice, Bob) plus one for Carol in the e2e run.

## Data touched
- User (3, each with email and display name), Organization (2), Invite (1), Post (1), Vote (2, then 1), Comment (1).

## Out of scope
Post-MVP features, delete success path (covered by F9-1), validation and duplicate-email paths (covered by F1-1, F2-1, F4-1), refresh, log out and rate limits (covered by F1-2, F1-3, F3-1 and F3-2); the "pending_invite" flow itself (F3-2 criterion 4), response headers and log hygiene (F1-4).

## Assumptions / Questions
- ASSUMED: the app header is where the signed-in user's display name is shown; display names "Alice", "Bob", "Carol" are test data.
- ASSUMED: exact UI texts "create or join organization", "Invite", "No posts yet" (see F1-1, F2-1, F3-1, F7-1); the brief gives no wording.
- Journey has 10 criteria (more than the usual 6) on purpose: it is one flow with two roles and two organizations; it is a single end-to-end scenario, not one task of work. Justified exception.
- The "owner's done definition" is not written in the repo; the steps follow the wording in the TASK-002 request (see handoff Open questions).
- Depends on F3-1 only for "the invite link lets a new user join"; F3-1 uses one persistent token per organization.
- Brief status was DRAFT when this was written; READY is conditional on brief approval.
- Contract check (TASK-040 follow-up, re-pointed to main; first written in Attempt 4): checked against api-contract.yaml and ADR-002, ADR-003 on main (11497e9a337fdad6d56582077ac3c529d77e3e44, which contains the merges of PR #2 (54f79e4), PR #6 (4a2e084) and PR #7 (11497e9); contract: docs/project/architecture/api-contract.yaml, ADRs: docs/project/decisions/; the files' own status line said Proposed at that commit; since PR #14 the contract, data-model.md and stack.md say Accepted by Orchestrator, and ADR-001 to ADR-004 say Proposed on main a6eaaaf0bd46755874bf587939e2e49a8fb0b73f (the same on 4f08a039b7d89b0ae4f1cac32cf9fbc1408b16cc)): display name required at sign-up, authors shown by display name only, invite link /join#<token> with POST preview and accept, RATE_LIMIT_ENABLED. 401 is ASSUMED in the contract.
