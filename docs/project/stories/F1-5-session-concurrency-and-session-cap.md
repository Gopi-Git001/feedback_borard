# F1-5: Logout, refresh and login stay safe when they run at the same time, and at most 10 sessions per user
Status: READY
Security review: touches authentication (security-bot review required)
As a user, I want a logout to really end my session even if a refresh is running at the same moment, and I want old sessions not to pile up, so that a stolen or racing session cannot survive.

Traces to the human-approved addition "logout revokes [refresh tokens]" in brief.md and to the concurrency rule and test requirements in ADR-002 and data-model.md section 3.8 (PR #2, security-bot N1). Added in TASK-040 Attempt 3 (security-bot should-fix 2). The single-request behaviour is in F1-2 and F1-3.

## Acceptance criteria
1. Given I am logged in with a valid refresh cookie, When a refresh and a logout with the same cookie and the guard header are sent at the same time (two connections, started together, repeated at least 50 times, plus one run in which the refresh is delayed between creating its successor token and committing), Then in every repetition where the logout answered 204 no token of that login's family is still active on the server (zero rows not revoked), and the cookie issued by a refresh that won the race gets 401 on its next refresh.
2. Given my refresh token T1 was already rotated into T2 (more than 10 seconds ago), When T1 is presented at the same time as T2 is being rotated into T3, Then at the end no token of the family is active and every later refresh with T1, T2 or T3 returns 401.
3. Given I am logged in in 10 browsers (10 active sessions), When I log in again from an 11th, Then the session with the oldest login time is revoked (reason "evicted"), its next refresh returns 401 and its browser shows the login form, the 11th session works, and an access token that session had already received stays valid until it expires (at most 15 min 30 s, R2) (ASSUMED limit of 10 sessions per user, ADR-002 and contract; not in the brief).
4. Given one user logs in 12 times at the same time (12 connections), When all requests have finished, Then the user has at most 10 active sessions and every surplus session has the reason "evicted".
5. Given I am logged in with cookie C1 and I log in again in the same browser, When the new login completes, Then the family of C1 is revoked (reason "logout"), a copy of C1 returns 401 on refresh, and only the new session is active (contract and ADR-002).
6. Given a refresh with a valid guard header and a logout without the guard header are sent at the same time for the same cookie, When both finish, Then the logout is 403 "FORBIDDEN" and revokes nothing, the refresh is 200, and in none of criteria 1 to 5 does any request fail with a server error or a database deadlock error (ADR-002 test requirement d).

## Business rules
- A token family is the chain of refresh tokens that starts at one login (F1-3). Every rotation, reuse revoke, logout and cap eviction of a family takes one lock per family, and login and sign-up take a per-user lock first; isolation level READ COMMITTED (ADR-002, data-model.md 3.8).
- At most 10 active families (sessions) per user; creating an 11th revokes the active one with the lowest family start time (ties: lowest family id) with reason "evicted" (ADR-002; marked ASSUMED there, an architect addition that is not in the brief).
- Login and sign-up also revoke the family of a valid refresh cookie that comes with the request (reason "logout") so re-login does not stack sessions (ADR-002).
- Known limits, not criteria (ADR-002, accepted): an issued access token stays valid until it expires, at most 15 min 30 s (15 minutes plus 30 seconds of clock leeway; ADR-002, accepted risk R2 and R13); a stolen refresh token replayed within the 10-second reuse leeway is answered 401 but not detected as reuse (R13).

## UI notes
- An evicted or revoked session sees the login form after its next renewal fails (ASSUMED, as in F1-2).

## Data touched
- Refresh token records (server side, hash only): family, revoked state and reason (logout, reuse, evicted).

## Out of scope
Concurrency of other endpoints, "log out of all devices", listing or removing sessions, the single-request behaviour (F1-2, F1-3), load or performance testing, how the locks are implemented.

## Assumptions / Questions
- ASSUMED: the cap of 10 sessions is an architect addition (ADR-002 says ASSUMED, not in the stories or the brief); criteria 3 and 4 follow it and are removed if the Orchestrator drops the cap (leftover (c) of TASK-040 is now covered here).
- ASSUMED test technique: two or more connections released by a barrier, 50 repetitions, and a test hook that delays the refresh transaction (ADR-002 names exactly this); the exact hook is up to backend-bot and qa-bot. Criteria 1, 2, 4 and 6 are backend integration tests, not browser tests.
- The permission case is the 403 for the logout without the guard header in criterion 6.
- Brief status: brief.md is APPROVED (human, 2026-10-27). This story traces to the human-approved additions and to the security-bot review of PR #5 (comment 6458253424).
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- HTTP codes: 403 and 404 are named in TASK-002; 429 and the other error codes come from the API contract. 401 is ASSUMED in the contract, so it stays ASSUMED here too.
- Contract check (TASK-040 follow-up, re-pointed to main; first written in Attempt 4): rotation, reuse and logout take one family lock, login and sign-up take a user lock, READ COMMITTED, cap of 10 sessions with eviction, re-login revokes the presented family, test requirements (a) to (d) (ADR-002 section Refresh token; data-model.md 3.8; contract conventions and the refresh, login and logout descriptions). Checked against the files on main (11497e9a337fdad6d56582077ac3c529d77e3e44, which contains the merges of PR #2 (54f79e4), PR #6 (4a2e084) and PR #7 (11497e9); contract: docs/project/architecture/api-contract.yaml, ADRs: docs/project/decisions/; the files' own status line said Proposed at that commit; since PR #14 the contract, data-model.md and stack.md say Accepted by Orchestrator, and ADR-001 to ADR-004 say Proposed on main d2e2fdcb4a90250bac374d586379d595e677610a (the same on a6eaaaf0bd46755874bf587939e2e49a8fb0b73f)).
