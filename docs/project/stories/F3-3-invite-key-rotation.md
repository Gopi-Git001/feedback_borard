# F3-3: Rotating the invite key keeps links safe and the admin's link working
Status: READY
Security review: touches authentication (security-bot review required)
As an operator and as an admin, I want old invite links to stop working when the server's invite key is replaced and the admin to get a working new link, so that a leaked key or link can be cut off without losing the organization's invite.

Traces to the human-approved invite-token addition in brief.md and to the key-rotation rule in ADR-003 and data-model.md 3.4 (PR #2, security-bot N2). Added in TASK-040 Attempt 3 (security-bot should-fix 3). The normal link behaviour is F3-1; token secrecy is F3-2. There is no admin "regenerate" feature in the MVP; rotation is an operator action (stop all backends, set a new INVITE_TOKEN_KEY, start them).

## Acceptance criteria
1. Given "Acme" has an invite, its admin has seen the link L1, and the operator restarts the app with a new INVITE_TOKEN_KEY, When anyone previews or accepts L1's token, even before an admin has opened "Invite" again, Then the response is 404 with code "INVITE_NOT_FOUND" and the message "Invite link is invalid", and no one joins.
2. Given the key was rotated, When the Acme admin clicks "Invite", Then a different link L2 is shown, the stored invite hash equals the SHA-256 of L2's token, exactly one invite row exists for "Acme", and L2 previews as "Acme" and can be accepted by a user without organization, who becomes a member.
3. Given L2 is shown, When the admin clicks "Invite" again, or the same admin sends two requests for the invite link at the same time (two concurrent requests from admin sessions; there is only one admin per organization in the MVP, ADR-003 test b), Then every response shows the same token L2, and the stored hash and the single row do not change again.
4. Given the key was rotated and no admin has opened "Invite" yet, When a token computed with the new key is previewed or accepted, Then it also returns 404 "INVITE_NOT_FOUND" (deliberate: no link of that organization works until an admin opens "Invite" once).
5. Given the key was rotated, When a member (not admin) asks for the invite link, Then the response is 403, no invite hash is changed and no link is shown; and when someone not logged in asks, Then the response is 401.
6. Given the test key INVITE_TOKEN_KEY "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8" (the 32 bytes 00 01 02 ... 1f; for tests only), the organization id "00000000-0000-4000-8000-000000000001" and token version 1, When the invite token is derived, Then it is "PNqzMLttQPIF8nHKGWLPGIMzyUHw8lLpXulro9uECFo" and the stored hash is "bc4debf5f218992063f53085e8e5d0b67f7d685916c9bb5810c398da541780a1" (the vector in ADR-003, re-computed by ba-bot and matching).

## Business rules
- The token is HMAC-SHA256(INVITE_TOKEN_KEY bytes, "invite:v" + version + ":" + organization id), 43 characters; only its SHA-256 hash is stored (ADR-003).
- The admin invite endpoint re-derives the token with the current key and, if its hash differs from the stored one, stores the new hash in the same transaction. Preview and accept also re-derive the expected token from the stored row with the current key and compare in constant time; a mismatch is 404 (ADR-003 rotation rules 1 and 2).
- Several backends must be rotated together; the key rotation does not touch sessions or JWT_SECRET (ADR-003 rules 3 and 4). The operator runbook is in ADR-003 and will be written into the README by another bot; it is not a story criterion.

## UI notes
- The admin sees the new link the next time "Invite" is opened and must share it again (the old link is dead); there is no message about rotation (ASSUMED).

## Data touched
- Invite: token hash (updated), token version (unchanged by rotation), organization.

## Out of scope
An admin "regenerate link" feature, expiry, revoking, removing members (all post-MVP, F3-1), the runbook text, JWT_SECRET rotation, how the key is stored and provisioned.

## Assumptions / Questions
- Accepted risk R8 (ADR-004 section 7; the no-expiry, no-revoke part is also R6): the invite link has no expiry and no revoke, it stays valid until the key rotates, a rotation leaves a window (criteria 1 and 4) in which no link works until an admin opens "Invite", and all backends of a mixed fleet must be rotated together (ADR-003 rule 3).
- ASSUMED: criteria 1 to 4 and 6 are backend tests that restart the app or set the key by environment variable (ADR-003 "Tests (qa-bot)" a to c); criterion 4 uses a token computed by the test with the new key.
- The vector in criterion 6 is test data only and must never be used as a real key (ADR-003). I re-computed it with HMAC-SHA256 and SHA-256 and it matches.
- ADR-003 is Proposed and security-bot must confirm the rotation rule (ADR-003 says so); if the rule changes, criteria 1 to 4 change.
- The permission case is criterion 5; the error cases are criteria 1, 4 and 5.
- Brief status: brief.md is APPROVED (human, 2026-10-27). This story traces to the human-approved additions and to the security-bot review of PR #5 (comment 6458253424).
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- HTTP codes: 403 and 404 are named in TASK-002; 429 and the other error codes come from the API contract. 401 is ASSUMED in the contract, so it stays ASSUMED here too.
- Contract check (TASK-040 Attempt 4): ADR-003 key rotation rules 1 to 4, key bytes and test vector, tests (a) to (c); data-model.md 3.4; contract invite description (rotation 404). The vector was re-computed independently and matches. Checked against PR #2 head bf3fabbe3339c16b9f87293e7e748ca2fcb0e41a (branch feature/TASK-001-stack-and-contracts, Proposed, not on main). Recheck once merged to main.
