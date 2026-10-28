# E2E-1: End-to-end journey (sign up, create org, invite, post, vote, comment, change status)
Status: READY
As a team lead and her teammate, we want to go from a new account to a triaged piece of feedback in one flow, so that we know the Team Feedback Board works end to end.

This story is the Playwright e2e target. Alice = first user (becomes admin). Bob = second user (becomes member). Carol = user of a different organization (isolation check). Each user signs up with email, password and a display name equal to the first name ("Alice", "Bob", "Carol"); other users see these display names, never emails.

## Acceptance criteria
1. (F1) Given no accounts exist, When Alice signs up with "alice@example.com", password "Passw0rd!x" and display name "Alice", Then she is logged in, her display name "Alice" is shown as her name in the app (ASSUMED location: app header), and she sees the "create or join organization" step (ASSUMED text).
2. (F2) Given Alice is logged in with no organization, When she creates the organization "Acme", Then she is admin of "Acme" and sees an empty board with the text "No posts yet" (ASSUMED text).
3. (F3, F2) Given Alice is admin of "Acme", When she clicks "Invite" (ASSUMED label) and Bob signs up as "bob@example.com" with display name "Bob" and opens that link and accepts, Then Bob is a member (not admin) of "Acme" and sees the same empty board.
4. (F4, F7) Given Bob is a member of "Acme", When he creates a post with title "Dark mode", a description, and type "idea", Then the post appears on the board with status "New" and 0 votes, visible to both Alice and Bob, with the author shown as "Bob".
5. (F5) Given the post "Dark mode" has 0 votes, When Alice and then Bob each upvote it once, Then it shows 2 votes; and when Bob clicks upvote again, Then it shows 1 vote.
6. (F6) Given the post "Dark mode" has no comments, When Bob adds the comment "Would help at night.", Then Alice sees that comment under the post, with the author shown as "Bob" (display name, not email).
7. (F8) Given the post is "New", When Alice (admin) sets its status to "Planned", Then both Alice and Bob see "Planned" on the post and on the board, and filtering the board by status "Planned" lists "Dark mode".
8. (Permission, F8 and F9) Given Bob is a member, When he tries to change the status or delete "Dark mode", Then each action returns 403 and the post is unchanged.
9. (Isolation, F2 and F7) Given Carol signed up (display name "Carol") and created the organization "Beta", When she opens the board and requests the "Dark mode" post by its id, Then her board shows "No posts yet" (ASSUMED text) and the post request returns 404.

## Business rules
- Steps map one to one to the Orchestrator's journey: sign up (1), create org (2), invite a second user (3), post (4), vote (5), comment (6), change status (7). Criteria 8 and 9 are the permission and isolation checks required by TASK-002.
- All rules of F1-F9 apply; this story adds no new rules.

## UI notes
- Uses the screens of F1-F9 only. Two browser contexts (Alice, Bob) plus one for Carol in the e2e run.

## Data touched
- User (3, each with email and display name), Organization (2), Invite (1), Post (1), Vote (2, then 1), Comment (1).

## Out of scope
Post-MVP features, delete success path (covered by F9-1), validation and duplicate-email paths (covered by F1-1, F2-1, F4-1), refresh, log out and rate limits (covered by F1-2 and F3-1).

## Assumptions / Questions
- ASSUMED: the app header is where the signed-in user's display name is shown; display names "Alice", "Bob", "Carol" are test data.
- ASSUMED: exact UI texts "create or join organization", "Invite", "No posts yet" (see F1-1, F2-1, F3-1, F7-1); the brief gives no wording.
- Journey has 9 criteria (more than the usual 6) on purpose: it is one flow with two roles and two organizations; it is a single end-to-end scenario, not one task of work. Justified exception.
- The "owner's done definition" is not written in the repo; the steps follow the wording in the TASK-002 request (see handoff Open questions).
- Depends on F3-1 only for "the invite link lets a new user join"; F3-1 uses one persistent token per organization.
- Brief status was DRAFT when this was written; READY is conditional on brief approval.
- Contract check (TASK-039): api-contract.yaml (branch feature/TASK-001-stack-and-contracts, not yet on main) requires a display name at sign-up and shows post and comment authors by display name only. Recheck once it is merged to main. Note for test authors: all e2e sign-ups come from one IP, so rate limits (F1-2) need a test-environment setting (see F1-2 Assumptions).
