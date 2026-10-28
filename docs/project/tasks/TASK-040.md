# TASK-040: Align stories with the revised auth and invite design
Owner: ba-bot   Milestone: M0   Size: M   Attempt: 5
Blocked by: PR #2 (architect-bot's revised design, still under review)   Branch: fix/TASK-040-auth-and-invite-redesign
Note: this spec was written retroactively by ba-bot at the Orchestrator's request, from the Orchestrator's TASK-040 message and the local instruction that relayed it.

## Goal
Make the stories match the revised design in api-contract.yaml, ADR-002, ADR-003 and the TASK-001 handoff (Attempt 2 and 2b) on PR #2, so the implementation and tests are written against one version.

## Context (read these)
- docs/project/stories/ (F1-1, F1-2, F2-1, F3-1, E2E-1)
- On PR #2: docs/project/architecture/api-contract.yaml, docs/project/decisions/ADR-002 and ADR-003, docs/project/handoffs/TASK-001-handoff.md
- docs/project/brief.md (approved additions)

## Scope
- F1-2: logout revokes the whole token family; refresh rotates; reuse of an old refresh token gives 401 and revokes the family; session ends 7 days after login; refresh and logout need the X-Requested-With header and a valid Origin; no 429 on logout; split into F1-3 if more than 6 criteria are needed.
- F3-1: invite link is /join#<token>; preview and accept are POST /invites/preview and /invites/accept with {token} in the body; only a hash is stored; the admin sees the same link every time until the server key rotates (F3-3); no token in any request URL; split into F3-2 if needed.
- F2-1: joining uses POST preview and accept; the token is held in sessionStorage while the user signs up or logs in; a bad or missing token shows "Invite link is invalid".
- E2E-1: step 3 uses /join#<token>; add a check that no request URL contains the token; run with RATE_LIMIT_ENABLED=false.
- F1-1: remove the out-of-scope line that conflicts with display name and the approved extras; display name 1-80, trimmed.
- Handoffs: TASK-039 says the repo is public, not private; keep Q11 (403 ORG_REQUIRED) as a leftover; keep ASSUMED labels.
- Mark F1-2, F3-1, F2-1, E2E-1 (and any new F1-3 or F3-2) as touching authentication, so security-bot reviews them.
- Add the missing docs/project/tasks/TASK-039.md and TASK-040.md.
- Attempt 2 (Orchestrator decisions): no login lockout and no per-account login limit (out of scope, listed as such in F1-2 and F1-3); rate limits are the brief's 10 requests per 60-second window per IP per endpoint (ASSUMED; window type is an implementation detail and tests must not depend on the boundary), for sign-up, login, refresh, invite preview and invite accept (accept per IP); logout is never rate limited.
- Attempt 2: in F4-1, F6-1 and F9-1 only the last "Contract check" footer line is replaced (the contract is on PR #2, not on main). Their criteria are not changed. F5-1, F7-1 and F8-1 are not touched.
- Attempt 3 (additional input, PR #2 head 6a961c3): new stories F1-4 (cookie flags, security headers on success and error responses, log hygiene), F1-5 (logout versus refresh races, session cap), F1-6 (password boundaries 8, 128 accepted and 7, 129 rejected), F2-2 (403 ORG_REQUIRED, ASSUMED), F3-3 (INVITE_TOKEN_KEY rotation); F1-3 gets criterion 6 (Origin: null); E2E-1 #1 checks the cookie flags and #10 also checks Referer, console, Web Storage and the address bar; rate-limit text aligned to 6a961c3 (Retry-After minimum 1, env-configurable limits, boundary-independent wording); the per-account login limit stays out of scope and is listed as an accepted risk in the handoff; architect-bot's story-vs-contract mismatches fixed.
- Attempt 4 (PR #2 head bf3fabbe3339c16b9f87293e7e748ca2fcb0e41a; qa-bot CHANGES_REQUESTED on c524b45 and the security-bot low findings): TASK-039 handoff Q2, Q3, Q4, Q10 and Q11 marked resolved or superseded; accepted-risk wording R1 to R17 in the handoff (replaced in Attempt 5 by a pointer to ADR-004 section 7), with the approval attribution reported by the Orchestrator; "15 min 30 s" as the only post-logout access-token window; F1-3 Origin rule follows the contract (limiter first); F1-4 folds in Domain, Max-Age, nginx errors and secret values; N and N+1 technique instead of a burst; "unchanged until the key rotates"; leeway cookie wording neutral (open point); F2-2 criterion 6 (404 before 403); F3-2 #4 matches the Join click; F3-3 #3 one admin; new story F1-7 (forged JWTs, X-Forwarded-For, display name as text); lockout "not offered".
- Attempt 5 (PR #2 head 79558a84db0a1c05067683a9be5159fdc8df5254; security-bot re-review of 369411635 and the Orchestrator's final PR #2 rules): one refresh-401 cookie rule (no Set-Cookie only for a token rotated less than 10 s ago; logout, eviction or reuse detection clear the cookie) in F1-3 criteria 2 and 6, F1-4 criterion 2, F1-2 criterion 2; F1-3 criteria 4 and 6 of Attempt 4 merged into criterion 4; accept check order 429, 415, 401, 400, 404, 409 and the 400 (missing, non-string or extra field) and 415 cases in new story F3-4 (F3-2 keeps the uniform 404 and says "never 400 for a string token"); new story F1-8 (invented X-Forwarded-For, 20 simultaneous requests let exactly 10 pass, 415 on sign-up and login, text rendering of display name, organization name, post and comment); F1-7 gets criteria 5 (access token as refresh cookie) and 6 (deleted membership); F1-2 criterion 6 (429 on refresh is not a logged-out session); F1-4 criterion 3 (Vary: Origin); R-number fixes; the R1-R17 mirror in the handoff replaced by a pointer to ADR-004 section 7; "R7 gates (see ADR-004 section 7)"; process chatter removed.
- Attempt 3: fix stale statements (this spec and the TASK-040 handoff said F4-1 to F9-1 were unchanged); update the numbering and design text in the TASK-039 handoff; make the rate-limit wording boundary-independent; keep the F3-2 criterion 5 examples valid under both contract heads (the 512 limit was removed at 6a961c3; no limit at bf3fabb); label contract-sourced message texts consistently.

## Acceptance criteria
- Given F1-2 and its split F1-3, then criteria cover rotation, reuse detection, the 7-day cap, logout revoking the family, the missing-header and bad-Origin 403, and no 429 on logout.
- Given F3-1 and F3-2, then criteria cover the /join#<token> link, POST preview and accept, hash-only storage, the same link until the key rotates, and no token in any request URL.
- Given F2-1, then criteria cover POST preview and accept and the "Invite link is invalid" message, and the sessionStorage flow is specified (F3-2 criterion 4).
- Given F1-3, then it has 6 criteria (reuse detection, rotated less than 10 seconds ago gives 401 without Set-Cookie, missing or wrong X-Requested-With gives 403, bad Origin including Origin: null and its variants gives 403, refresh token used as a bearer gives 401 ASSUMED, logout or eviction within 10 seconds gives 401 with the cleared cookie) and no lockout criterion.
- Given F3-2, then it has 6 criteria (hash-only storage, no token in any URL or log with no-store, fragment removed from the address bar, the logged-out sessionStorage flow, uniform 404 INVITE_NOT_FOUND for any string token, accept 429 per IP); and given F3-4 (new in Attempt 5), then it has 6 criteria (400 for a missing, non-string or extra field, 400 for malformed bodies, 415 after the limiter, accept order 429, 415, 401, 400, 404, 409, preview order, odd strings give 404).
- Given E2E-1, then step 3 uses /join#<token> and a criterion checks that no request URL contains the token.
- Given F1-4, F1-5, F1-6, F2-2 and F3-3, then they have 6, 6, 6, 6 and 6 criteria (F2-2 had 5 until Attempt 4) and cover: cookie flags and headers on every response (also errors) and log hygiene; the four concurrency tests and the session cap; password boundaries; ORG_REQUIRED; key rotation with the ADR-003 vector. Per-account login limit has no criterion (accepted risk).
- Given F1-7, then it has 6 criteria: tampered token, alg none or wrong algorithm, expired or wrong-claim or refresh-typed token, tampered refresh cookie, access token sent as the refresh cookie, deleted membership gives 401; and given F1-8 (new in Attempt 5), then it has 5 criteria: invented X-Forwarded-For (small limit N, request N+1 is the first 429), 20 simultaneous requests let exactly 10 pass, 415 on sign-up and login after the limiter, display name rendered as text, organization name, post and comment rendered as text.
- Given the handoff (Attempt 5), then it points to ADR-004 section 7 for the accepted-risk register (owner: ADR-004; no copy), keeps the approval attribution, and has the "Attempt 5 changes" and "PR #2 delta bf3fabb -> 79558a8" sections.
- Given every changed story, then it has 3-6 criteria (the journey is the justified exception), no QUESTION: items, and the security-review line.
- Given the handoff, then it states the PR #2 head checked, lists conflicts with the Orchestrator's list, and keeps all ASSUMED labels.

## Out of scope
Code, brief.md, plan.md, board.md, api-contract.yaml, ADRs, any criterion of F4-1 to F9-1 (only the Contract check footer line of F4-1, F6-1 and F9-1 changes; F5-1, F7-1 and F8-1 are untouched), login lockout and per-account login limits.

## Files
stories: F1-1, F1-2, F1-3 (new in Attempt 1), F1-4, F1-5, F1-6, F2-2, F3-3 (all new in Attempt 3), F1-7 (new in Attempt 4), F1-8 and F3-4 (new in Attempt 5), F2-1, F3-1, F3-2 (new in Attempt 1), E2E-1 (not changed in Attempt 5), and the footer line of F4-1, F6-1, F9-1. handoffs: TASK-039-handoff.md (corrections, supersession notes), TASK-040-handoff.md. tasks: TASK-039.md, TASK-040.md.

## Deliverables
- PR titled `TASK-040: ...` on the branch above (do not merge)
- Handoff report docs/project/handoffs/TASK-040-handoff.md
- Use your skills: write-user-stories, review-story-readiness, write-handoff-report
