# Handoff: TASK-040 Align stories with the revised auth and invite design
Bot: ba-bot   Attempt: 2   PR: https://github.com/Gopi-Git001/feedback_borard/pull/5   Branch: fix/TASK-040-auth-and-invite-redesign

Security review: touches authentication (security-bot review required). Stories that touch authentication: F1-1, F1-2, F1-3 (new), F2-1, F3-1, F3-2 (new), E2E-1.

Checked against PR #2 (https://github.com/Gopi-Git001/feedback_borard/pull/2), branch feature/TASK-001-stack-and-contracts, **head 0459573b4c6ece0c2af58794b345520060b00fc1** ("TASK-001: Handoff: attempt 2b section, stories impact, revocation reversal"). Files read from that head: docs/project/architecture/api-contract.yaml, architecture/data-model.md, decisions/ADR-002, ADR-003, ADR-004 (security headers and origin check only), handoffs/TASK-001-handoff.md (Attempt 2 and 2b). Main was at 2240765 (PR #4 merged). I fetched again before finishing Attempt 1 and again for Attempt 2: the PR #2 head was still 0459573 both times.

Open questions: see "Open questions" below (8 items, including one entry of known leftovers).

Review history: Attempt 1 = commit 280c465 (PR #5 head 7c40954 is the same content applied on main 2240765). Attempt 2 = this version (Orchestrator decisions: drop the login lockout, rate limits per IP as in the brief, stale contract lines fixed, leftovers recorded).

## Summary
F1-2 now follows the revised session design (rotation, family revoked by logout, 7-day absolute cap, no 429 on logout) and a new F1-3 holds reuse detection, the X-Requested-With and Origin guard and the bearer-token rule. F3-1 now uses the link /join#<token> with POST preview and accept; a new F3-2 covers hash-only storage, no token in any request URL, fragment removal, the logged-out sessionStorage flow, the uniform 404 and the accept rate limit. F2-1, E2E-1 and F1-1 were updated, the TASK-039 handoff was corrected, and TASK-039.md and TASK-040.md were written retroactively. Nothing outside docs/project/stories/, handoffs/ and tasks/ changed.

## Attempt 2 changes
- **F1-3: per-account login limit removed** (5 failed attempts per 900 s). Account lockout is out of scope (Orchestrator decision; architect-bot is dropping it from the contract and ADR-002). F1-3 now has 5 criteria (reuse, leeway, header guard, Origin guard, bearer rule), which is still within 3-6. Cross-references fixed in F1-1, F1-2 and this handoff; E2E-1 and F3-x never mentioned it.
- **Rate limits decided:** the brief's 10 requests per 60 s per IP per endpoint is the decision, including invite accept per IP. F3-2 now says per IP in the criterion, the business rule and the assumptions (it said per user).
- **Stale contract-check lines** in F4-1, F6-1 and F9-1 replaced (only those lines). Finding: api-contract.yaml is still absent from origin/main (`git ls-tree -r origin/main` shows no contract file), so the lines now say it is on PR #2 (Proposed, head 0459573).
- **Known leftovers** recorded in one Open-questions entry (no new criteria).
- **PR #2 head now: 0459573b4c6ece0c2af58794b345520060b00fc1** (fetched in Attempt 2). the head is the same commit as before, so no contract, ADR or data-model value I relied on has changed. Note: the contract and ADR-002 on that head still contain the per-account login limit and the per-user accept limit until architect-bot aligns them, so the stories and the contract disagree on those two points for now.

## Acceptance criteria
| Criterion | Status (met / not met) | Test that proves it |
|-----------|------------------------|---------------------|
| F1-2: logout revokes the family; refresh rotates; session ends 7 days after login | met | F1-2 #1 (rotation, Max-Age), #3 (7-day cap), #4 (logout, old copy gets 401) |
| F1-2: reuse of an old refresh token gives 401 and revokes the family | met (in F1-3, because F1-2 would exceed 6 criteria) | F1-3 #1; leeway case F1-3 #2 |
| F1-2: refresh and logout need X-Requested-With and a valid Origin, with the contract's code | met (in F1-3) | F1-3 #3 (header, 403 FORBIDDEN), #4 (Origin, 403 FORBIDDEN) |
| F1-2: no 429 on logout; "401 is ASSUMED in the contract" text | met | F1-2 #4 (no logout request answered with 429), Business rules, and the footer lines "401 is ASSUMED in the contract" in F1-2 (HTTP codes line and Contract check line) |
| F3-1: link /join#<token>, POST preview/accept with body token, hash only stored, same link every time, no token in a request URL | met (storage and URL checks in F3-2) | F3-1 #1, #2, #4; F3-2 #1, #2 |
| F3-1: 429 on invite preview kept | met | F3-1 #6 |
| F2-1: POST preview and accept; token held in sessionStorage while signing up; bad or missing token shows "Invite link is invalid" | met (the sessionStorage criterion is F3-2 #4, see Decisions) | F2-1 #3, #4; F3-2 #4, #5 |
| E2E-1: step 3 uses /join#<token>; no request URL contains the token; RATE_LIMIT_ENABLED=false | met | E2E-1 #3, #10, Business rules (test environment) |
| F1-1: remove the conflicting out-of-scope line; display_name 1-80 trimmed | met | F1-1 Out of scope, #3, Business rules |
| TASK-039 handoff: repo public, Q5/Q9 updated, Q11 kept, ASSUMED kept | met | TASK-039-handoff.md line 9, Q5, Q9, Q11 unchanged |
| Security review line on F1-2, F3-1, F2-1, E2E-1, F1-3, F3-2 (and in this handoff) | met | line under Status in each story; line 4 here; also added to F1-1 (see Decisions) |
| TASK-039.md and TASK-040.md exist (Goal, Scope, Acceptance criteria, retroactive note) | met | docs/project/tasks/TASK-039.md, TASK-040.md |
| F4-1 to F9-1 unchanged | met | git diff --name-only lists none of them |
| Readiness re-run on every changed story | met, with the gaps below | Test results table |
| Re-check PR #2 head before finishing | met | head 0459573 before and after (Attempt 1 and Attempt 2) |
| Attempt 2: login lockout criterion removed from F1-3, cross-references fixed | met | F1-3 has 5 criteria; `grep -n -i "per-account\|6th\|lock" docs/project/stories/*.md` finds only the out-of-scope notes in F1-2 and F1-3 |
| Attempt 2: accept limit per IP in F3-2 | met | F3-2 #6, Business rules, Assumptions |
| Attempt 2: stale contract-check lines in F4-1, F6-1, F9-1 | met | last line of each file (only those lines changed) |
| Attempt 2: leftovers recorded, header and PR link updated | met | Open questions Q4; line 2 of this file |

## Files changed
- docs/project/stories/F1-1-signup-login.md (security line; trimming and display-name limits now contract-sourced; out-of-scope line removed; cross-reference to F1-3, reworded in Attempt 2; contract-check line)
- docs/project/stories/F1-2-session-and-rate-limits.md (rewritten: 6 criteria for rotation, invalid cookie, 7-day cap, logout with family revocation, 429 sign-up/login, 429 refresh; Attempt 2: per-account references removed)
- docs/project/stories/F1-3-session-hardening.md (NEW; Attempt 2: login lockout criterion removed, 5 criteria)
- docs/project/stories/F2-1-organization-create-join.md (criteria 3, 4, 6; rules; UI note; footers)
- docs/project/stories/F3-1-invite-link.md (link format, rules, data touched, footers)
- docs/project/stories/F3-2-invite-token-protection.md (NEW; Attempt 2: accept limit per IP)
- docs/project/stories/E2E-1-owner-journey.md (step 3, new criterion 10, test environment, footers)
- docs/project/handoffs/TASK-039-handoff.md (public repo; Q5 and Q9 resolved or superseded; two superseded notes in Decisions)
- docs/project/stories/F4-1-posts.md, F6-1-comments.md, F9-1-delete-post.md (Attempt 2: only the stale "Contract check (TASK-039)" line replaced)
- docs/project/handoffs/TASK-040-handoff.md (NEW, this file)
- docs/project/tasks/TASK-039.md (NEW, retroactive)
- docs/project/tasks/TASK-040.md (NEW, retroactive)
Not touched: brief.md, plan.md, board.md, code, api-contract.yaml, ADRs, F5-1, F7-1, F8-1 (F4-1, F6-1, F9-1 only in the one line named above).

## How to test locally
Docs only, nothing to run. Review: (1) `git diff --name-only origin/main` lists only the files above; (2) each new or changed criterion can be turned into a test with the values given; (3) every value in a story that is not in the contract, ADRs or the Orchestrator's list is marked ASSUMED; (4) check the contract-sourced values against `git show origin/feature/TASK-001-stack-and-contracts:docs/project/architecture/api-contract.yaml` (and ADR-002, ADR-003 in docs/project/decisions/); (5) count criteria per story: `awk '/^## Acceptance criteria/{a=1;next} /^## /{a=0} a&&/^[0-9]+\. /{c++} END{print c}' <file>`.

## Test results
No automated tests (docs task). I re-ran review-story-readiness on each changed story myself (not independent; qa-bot and security-bot review). Criteria counted with the awk command above: F1-1 6, F1-2 6, F1-3 5, F2-1 6, F3-1 6, F3-2 6, E2E-1 10 (justified exception). No `QUESTION:` item in any story.

| Story | Ready? | Gaps / questions |
|-------|--------|------------------|
| F1-1 signup-login (6) | READY | Only a cross-reference reworded in Attempt 2. Contract is Proposed (PR #2), so "no conflict with the contract" holds only against head 0459573. Criterion 3 bundles four validation groups (as before). 401 (#6) ASSUMED. |
| F1-2 session-and-rate-limits (6) | READY | #3 and #4 are multi-clause but each clause is testable. Thresholds 10 per 60 s per IP are ASSUMED (brief.md) and decided by the Orchestrator; ADR-002 is being aligned. Retry-After "greater than 0" ASSUMED. 7-day test needs a controllable clock (ASSUMED technique). 401 ASSUMED in the contract. |
| F1-3 session-hardening (5) NEW | READY | 401 for a refresh token used as a bearer token is ASSUMED (status not in the contract). Permission case = the 403 guard (#3, #4). Re-run in Attempt 2 after removing the login-limit criterion; 5 criteria is within 3-6. The contract and ADR-002 still mention a per-account login limit until architect-bot drops it (not a story conflict, the story is silent on it). |
| F2-1 organization-create-join (6) | READY | The logged-out sessionStorage flow is a criterion in F3-2 #4, not here (6-criterion cap). "No request when no token after #" ASSUMED (from the TASK-001 handoff). 403 ORG_REQUIRED still not covered (Q11 of TASK-039). |
| F3-1 invite-link (6) | READY | Preview threshold ASSUMED (brief.md, decided; ADR-002 being aligned). Retry-After ASSUMED. Storage and URL secrecy moved to F3-2. |
| F3-2 invite-token-protection (6) NEW | READY | #2 bundles URL, log, body and header checks, and needs access to app and proxy logs. #3 is browser behaviour. #6 threshold ASSUMED, per IP (decided; the contract still says per user until aligned). ADR-003 is Proposed and awaits security-bot re-review (Q2). |
| E2E-1 owner-journey (10) | READY | 10 criteria on purpose (one flow). #10 reads the whole-run network trace. |

Definition of Ready: all boxes are checked for the rows above, except that "no conflict with other stories or the API contract" is checked against a contract that is still Proposed on PR #2 (head 0459573) and that "traces to the approved brief" now holds (brief.md is APPROVED and lists the additions). F4-1 to F9-1 were not re-reviewed; in Attempt 2 only the stale "Contract check (TASK-039)" line of F4-1, F6-1 and F9-1 was replaced (the contract is on PR #2, Proposed, not on main); no criterion changed.

## Decisions made (and why)
- **Contract and ADRs win over the Orchestrator's list** where they differ; the differences are listed in these decisions and under Open questions.
- **F1-2 split.** Rotation, 7-day cap, logout and the two rate-limit criteria fill F1-2's 6 slots. Reuse detection, the CSRF guard and the bearer rule went to the new F1-3-session-hardening.md. The file F1-2-session-and-rate-limits.md keeps its name so existing references stay valid.
- **F3-1 split.** F3-1 keeps its 6 criteria (link shape, same link, member 403, join and isolation, 401, preview 429). Hash-only storage, no token in request URLs or logs, fragment removal, the logged-out flow, the uniform 404 and the accept rate limit are in the new F3-2-invite-token-protection.md.
- **sessionStorage criterion lives in F3-2 #4, not F2-1.** F2-1 has 6 criteria and no slot; F2-1's rules and UI note state the flow and point to F3-2 #4. If the Orchestrator wants it inside F2-1, F2-1 needs a 7th criterion or a new story F2-2.
- **"Invite link is invalid" is no longer labelled ASSUMED in F2-1 #4**, because the contract (NotFound response, previewInvite) and ADR-003 give that text verbatim. It stays ASSUMED from the brief's point of view, because the contract is still Proposed. Other texts ("Email already registered", "Invalid email or password", "You already belong to an organization") were not re-labelled; they are untouched.
- **Display-name trimming is contract-sourced now** (contract conventions and SignupRequest: trim, then validate 1-80, store the trimmed value). The Orchestrator said to keep it ASSUMED unless the contract states it, so I removed the ASSUMED label from the story; brief.md still says "ASSUMED trimming" (Q6).
- **F1-1 out-of-scope line.** PR #4 had already reduced it to "... avatars, session renewal, log out and rate limiting (these three are in F1-2)". I removed that part completely, since those three are now in scope (F1-2, F1-3).
- **Security-review line also added to F1-1** (not in the Orchestrator's list), because sign-up and login handle passwords and issue sessions. Remove it if not wanted.
- **Rate-limit numbers: decided by the Orchestrator (Attempt 2).** The brief's 10 requests per 60 s per IP per endpoint (ASSUMED in brief.md) is the decision, for sign-up, login, refresh, invite preview and invite accept (accept per IP). ADR-002 is being aligned to it by architect-bot, so its different defaults are not an open question any more. The stories already used the brief's number.
- **Per-account login limit removed from F1-3 (Attempt 2).** Orchestrator decision: an account lockout is out of scope (it would let an attacker lock a victim out; architect-bot is dropping it from the contract and ADR-002). The criterion, its ASSUMED threshold (5 failed attempts per 900 s), the ASSUMED "6th attempt with the correct password is blocked" and the "login lock" business rule were deleted; F1-3 renumbered (the bearer-token criterion is now #5).
- **E2E-1 #10 added** (journey now 10 criteria) instead of folding the token check into step 3, so it can fail separately. RATE_LIMIT_ENABLED=false is written as a test-environment setting (ADR-002 and the Orchestrator); rate-limit criteria are not part of the journey.
- **TASK-039 handoff corrections.** Line 9 no longer says the repo is private. I did not verify why the earlier fetch of TEAM-CONVENTIONS.md failed, and that file lives in the separate Saas_Bot repo, whose visibility I did not check; the handoff says so. Q5 (logout 429) is marked resolved and Q9 (no revocation) superseded, because PR #2 removed the logout 429 and added server-side revocation. Q11 (403 ORG_REQUIRED) is kept as a leftover and all ASSUMED labels are kept.
- **Spec files TASK-039.md and TASK-040.md** are retroactive, written from the Orchestrator's messages as relayed to me; they carry that note.

## Open questions
1. **PR #2 is still moving.** Contract status is "Proposed, awaiting Orchestrator approval"; ADR-003 awaits security-bot re-review; ADR-002 is "Proposed". Any change to the guard header value, the leeway (10 s), the 43-character token, the pending_invite key or the 429 scope changes F1-2, F1-3, F2-1, F3-1, F3-2 or E2E-1. Head checked: 0459573 (unchanged in Attempt 2). Until architect-bot aligns them, the contract and ADR-002 still show the per-account login limit, per-user invite accept and organization-create limits, and different rate-limit numbers than the stories.
2. **brief.md calls display-name trimming ASSUMED**, the contract states it. Orchestrator may align the brief.
3. **Retry-After "greater than 0"** is still ASSUMED in F1-2 #5, #6 and F3-1 #6 (the contract says only integer seconds). F3-2 #6 and its Assumptions carry the same ASSUMED value.
4. **Known leftovers, no criteria in any story (Orchestrator will cover them in backend tests):** (a) 403 `ORG_REQUIRED` for a logged-in user with no organization calling an org-scoped endpoint (ASSUMED in the contract; carried over from TASK-039 Q11); (b) the per-user 429 on `POST /organizations` (contract note "drop it if it is out of scope"; not in brief.md); (c) the cap of 10 active refresh-token families per user (ASSUMED in ADR-002). F2-1, F4-1 and F7-1 are full at 6 criteria.
5. **401 is ASSUMED in the contract** (conventions, Unauthorized response); the same holds for the bearer-misuse 401 in F1-3 #5. Needs the Orchestrator's confirmation, as before.
6. **Test environment:** rate limits are off in e2e (RATE_LIMIT_ENABLED=false), so F1-2 #5, #6, F3-1 #6 and F3-2 #6 must be backend or component tests with small limits. qa-bot to plan.
7. **sessionStorage criterion in F3-2 #4**, not F2-1 (6-criterion cap); say if it should move to a 7th F2-1 criterion or a new story.
8. **F1-1 also has the security-review line** (not in the original list); remove if not wanted.

## Suggested follow-up tasks
- Orchestrator: update brief.md for trimming (Q2); get PR #2 approved with the contract and ADR-002 aligned to the decisions above (no per-account login limit, per-IP accept limit, brief's rate-limit numbers), then ask me for a small recheck of the "Contract check" lines once the contract is on main.
- ba-bot (small): when api-contract.yaml is on main, change the "Contract check" lines in F4-1, F6-1 and F9-1 (and the TASK-040 lines elsewhere) to say it is on main.
- qa-bot and security-bot: review F1-2, F1-3, F2-1, F3-1, F3-2 and E2E-1; security-bot should confirm the F1-3 #5 interpretation (401 for a refresh token used as a bearer token).
- backend-bot and qa-bot: derive tests from F1-3 and F3-2; make the log-inspection test (F3-2 #2) part of the suite; cover the Q4 leftovers in backend tests.
