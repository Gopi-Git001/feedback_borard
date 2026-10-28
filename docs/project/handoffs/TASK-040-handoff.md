# Handoff: TASK-040 Align stories with the revised auth and invite design
Bot: ba-bot   Attempt: 1   PR: to be set when opened   Branch: fix/TASK-040-auth-and-invite-redesign

Security review: touches authentication (security-bot review required). Stories that touch authentication: F1-1, F1-2, F1-3 (new), F2-1, F3-1, F3-2 (new), E2E-1.

Checked against PR #2 (https://github.com/Gopi-Git001/feedback_borard/pull/2), branch feature/TASK-001-stack-and-contracts, **head 0459573b4c6ece0c2af58794b345520060b00fc1** ("TASK-001: Handoff: attempt 2b section, stories impact, revocation reversal"). Files read from that head: docs/project/architecture/api-contract.yaml, architecture/data-model.md, decisions/ADR-002, ADR-003, ADR-004 (security headers and origin check only), handoffs/TASK-001-handoff.md (Attempt 2 and 2b). Main was at 2240765 (PR #4 merged). I fetched again before finishing: the PR #2 head was still 0459573.

Open questions: see "Open questions" below (11 items).

## Summary
F1-2 now follows the revised session design (rotation, family revoked by logout, 7-day absolute cap, no 429 on logout) and a new F1-3 holds reuse detection, the X-Requested-With and Origin guard, the per-account login limit and the bearer-token rule. F3-1 now uses the link /join#<token> with POST preview and accept; a new F3-2 covers hash-only storage, no token in any request URL, fragment removal, the logged-out sessionStorage flow, the uniform 404 and the accept rate limit. F2-1, E2E-1 and F1-1 were updated, the TASK-039 handoff was corrected, and TASK-039.md and TASK-040.md were written retroactively. Nothing outside docs/project/stories/, handoffs/ and tasks/ changed.

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
| Re-check PR #2 head before finishing | met | head 0459573 before and after |

## Files changed
- docs/project/stories/F1-1-signup-login.md (security line; trimming and display-name limits now contract-sourced; out-of-scope line removed; cross-reference to F1-3; contract-check line)
- docs/project/stories/F1-2-session-and-rate-limits.md (rewritten: 6 criteria for rotation, invalid cookie, 7-day cap, logout with family revocation, 429 sign-up/login, 429 refresh)
- docs/project/stories/F1-3-session-hardening.md (NEW)
- docs/project/stories/F2-1-organization-create-join.md (criteria 3, 4, 6; rules; UI note; footers)
- docs/project/stories/F3-1-invite-link.md (link format, rules, data touched, footers)
- docs/project/stories/F3-2-invite-token-protection.md (NEW)
- docs/project/stories/E2E-1-owner-journey.md (step 3, new criterion 10, test environment, footers)
- docs/project/handoffs/TASK-039-handoff.md (public repo; Q5 and Q9 resolved or superseded; two superseded notes in Decisions)
- docs/project/handoffs/TASK-040-handoff.md (NEW, this file)
- docs/project/tasks/TASK-039.md (NEW, retroactive)
- docs/project/tasks/TASK-040.md (NEW, retroactive)
Not touched: brief.md, plan.md, board.md, code, api-contract.yaml, ADRs, F4-1 to F9-1.

## How to test locally
Docs only, nothing to run. Review: (1) `git diff --name-only origin/main` lists only the files above; (2) each new or changed criterion can be turned into a test with the values given; (3) every value in a story that is not in the contract, ADRs or the Orchestrator's list is marked ASSUMED; (4) check the contract-sourced values against `git show origin/feature/TASK-001-stack-and-contracts:docs/project/architecture/api-contract.yaml` (and ADR-002, ADR-003 in docs/project/decisions/); (5) count criteria per story: `awk '/^## Acceptance criteria/{a=1;next} /^## /{a=0} a&&/^[0-9]+\. /{c++} END{print c}' <file>`.

## Test results
No automated tests (docs task). I re-ran review-story-readiness on each changed story myself (not independent; qa-bot and security-bot review). Criteria counted with the awk command above: F1-1 6, F1-2 6, F1-3 6, F2-1 6, F3-1 6, F3-2 6, E2E-1 10 (justified exception). No `QUESTION:` item in any story.

| Story | Ready? | Gaps / questions |
|-------|--------|------------------|
| F1-1 signup-login (6) | READY | Contract is Proposed (PR #2), so "no conflict with the contract" holds only against head 0459573. Criterion 3 bundles four validation groups (as before). 401 (#6) ASSUMED. |
| F1-2 session-and-rate-limits (6) | READY | #3 and #4 are multi-clause but each clause is testable. Thresholds 10 per 60 s ASSUMED and in conflict with ADR-002's defaults (Q1). Retry-After "greater than 0" ASSUMED. 7-day test needs a controllable clock (ASSUMED technique). 401 ASSUMED in the contract. |
| F1-3 session-hardening (6) NEW | READY | Per-account threshold (5 per 900 s, ADR-002 default) and 401 for a refresh token used as a bearer token are ASSUMED. Permission case = the 403 guard (#3, #4). #5 cannot run in the e2e suite (rate limits off); it is a backend test. |
| F2-1 organization-create-join (6) | READY | The logged-out sessionStorage flow is a criterion in F3-2 #4, not here (6-criterion cap). "No request when no token after #" ASSUMED (from the TASK-001 handoff). 403 ORG_REQUIRED still not covered (Q11 of TASK-039). |
| F3-1 invite-link (6) | READY | Preview threshold ASSUMED and differs from ADR-002 (Q1). Retry-After ASSUMED. Storage and URL secrecy moved to F3-2. |
| F3-2 invite-token-protection (6) NEW | READY | #2 bundles URL, log, body and header checks, and needs access to app and proxy logs. #3 is browser behaviour. #6 threshold ASSUMED; per user (contract) versus per IP (brief) (Q3). ADR-003 is Proposed and awaits security-bot re-review (Q2). |
| E2E-1 owner-journey (10) | READY | 10 criteria on purpose (one flow). #10 reads the whole-run network trace. |

Definition of Ready: all boxes are checked for the rows above, except that "no conflict with other stories or the API contract" is checked against a contract that is still Proposed on PR #2 (head 0459573) and that "traces to the approved brief" now holds (brief.md is APPROVED and lists the additions). F4-1 to F9-1 were not changed and not re-reviewed; their "Contract check (TASK-039)" lines still say the contract is "not yet on main".

## Decisions made (and why)
- **Contract and ADRs win over the Orchestrator's list** where they differ; the differences are listed under Open questions (Q1, Q3, Q4, Q5).
- **F1-2 split.** Rotation, 7-day cap, logout and the two rate-limit criteria fill F1-2's 6 slots. Reuse detection, the CSRF guard, the per-account login limit and the bearer rule went to the new F1-3-session-hardening.md. The file F1-2-session-and-rate-limits.md keeps its name so existing references stay valid.
- **F3-1 split.** F3-1 keeps its 6 criteria (link shape, same link, member 403, join and isolation, 401, preview 429). Hash-only storage, no token in request URLs or logs, fragment removal, the logged-out flow, the uniform 404 and the accept rate limit are in the new F3-2-invite-token-protection.md.
- **sessionStorage criterion lives in F3-2 #4, not F2-1.** F2-1 has 6 criteria and no slot; F2-1's rules and UI note state the flow and point to F3-2 #4. If the Orchestrator wants it inside F2-1, F2-1 needs a 7th criterion or a new story F2-2.
- **"Invite link is invalid" is no longer labelled ASSUMED in F2-1 #4**, because the contract (NotFound response, previewInvite) and ADR-003 give that text verbatim. It stays ASSUMED from the brief's point of view, because the contract is still Proposed. Other texts ("Email already registered", "Invalid email or password", "You already belong to an organization") were not re-labelled; they are untouched.
- **Display-name trimming is contract-sourced now** (contract conventions and SignupRequest: trim, then validate 1-80, store the trimmed value). The Orchestrator said to keep it ASSUMED unless the contract states it, so I removed the ASSUMED label from the story; brief.md still says "ASSUMED trimming" (Q6).
- **F1-1 out-of-scope line.** PR #4 had already reduced it to "... avatars, session renewal, log out and rate limiting (these three are in F1-2)". I removed that part completely, since those three are now in scope (F1-2, F1-3).
- **Security-review line also added to F1-1** (not in the Orchestrator's list), because sign-up and login handle passwords and issue sessions. Remove it if not wanted.
- **Rate-limit numbers follow the approved brief.md** (10 per 60 s per IP per endpoint, ASSUMED) and not ADR-002's defaults (Q1). The per-account login limit is not in the brief; it comes from the contract and ADR-002 and uses ADR-002's 5 failed attempts per 900 s, ASSUMED.
- **Whether a 6th login attempt with the correct password is blocked** (F1-3 #5) follows from ADR-002's remark that the limit "lets an attacker lock a victim's login", and is marked ASSUMED.
- **E2E-1 #10 added** (journey now 10 criteria) instead of folding the token check into step 3, so it can fail separately. RATE_LIMIT_ENABLED=false is written as a test-environment setting (ADR-002 and the Orchestrator); rate-limit criteria are not part of the journey.
- **TASK-039 handoff corrections.** Line 9 no longer says the repo is private. I did not verify why the earlier fetch of TEAM-CONVENTIONS.md failed, and that file lives in the separate Saas_Bot repo, whose visibility I did not check; the handoff says so. Q5 (logout 429) is marked resolved and Q9 (no revocation) superseded, because PR #2 removed the logout 429 and added server-side revocation. Q11 (403 ORG_REQUIRED) is kept as a leftover and all ASSUMED labels are kept.
- **Spec files TASK-039.md and TASK-040.md** are retroactive, written from the Orchestrator's messages as relayed to me; they carry that note.

## Open questions
1. **Rate-limit numbers conflict.** brief.md (approved): ASSUMED 10 per 60 s per IP per endpoint. ADR-002 (Proposed): sign-up 5/3600 s, login 20/900 s, per account 5 failed/900 s, refresh 60/900 s, invite preview 20/900 s, accept 10/900 s per user, organization create 5/3600 s per user. The stories use the brief's number (and ADR-002's per-account number). Orchestrator and architect-bot: pick one set; tests should set values through the environment variables (ADR-002) either way.
2. **PR #2 is still moving.** Contract status is "Proposed, awaiting Orchestrator approval"; ADR-003 awaits security-bot re-review; ADR-002 is "Proposed". Any change to the guard header value, the leeway (10 s), the 43-character token, the pending_invite key, or the 429 scope changes F1-2, F1-3, F2-1, F3-1, F3-2 or E2E-1. The head I checked is 0459573.
3. **Invite accept 429:** the contract and ADR-002 say per user; brief.md says per IP per endpoint. F3-2 #6 uses one user from one IP, so both readings pass. Confirm which is meant.
4. **Contract note on POST /organizations rate limit:** the contract adds a per-user 429 on organization creation "added after the security review; drop it if it is out of scope". It is not in brief.md and not in any story. Orchestrator: keep (then F2-1 or a small story needs a criterion) or drop.
5. **Active-family cap (10 per user, ASSUMED in ADR-002)** and the 403 ORG_REQUIRED rule (known leftover, Q11 of the TASK-039 handoff) have no criterion. Say if you want them added; F2-1, F4-1 and F7-1 are full at 6 criteria.
6. **brief.md calls display-name trimming ASSUMED**, the contract states it. Orchestrator may align the brief.
7. **Retry-After "greater than 0"** is still ASSUMED in F1-2 #5, #6, F1-3 #5 and F3-1 #6 (the contract says only integer seconds).
8. **401 is ASSUMED in the contract** (conventions, Unauthorized response); the same holds for the bearer-misuse 401 in F1-3 #6. Needs the Orchestrator's confirmation, as before.
9. **Whether the 6th login attempt with a correct password is blocked** (F1-3 #5) is inferred from ADR-002, not stated as a rule.
10. **Test environment:** rate limits are off in e2e (RATE_LIMIT_ENABLED=false), so F1-2 #5, #6, F1-3 #5, F3-1 #6 and F3-2 #6 must be backend or component tests with small limits. qa-bot to plan.
11. **403 ORG_REQUIRED stays a leftover** (carried over from TASK-039 Q11, unchanged).

## Suggested follow-up tasks
- Orchestrator: resolve Q1 and Q3 with architect-bot, and update brief.md for trimming (Q6); get PR #2 approved, then ask me for a small recheck of the "Contract check (TASK-040)" lines once it is on main.
- ba-bot (small): refresh the "Contract check (TASK-039)" lines in F4-1, F6-1 and F9-1 once api-contract.yaml is on main (they were not touched here, as instructed).
- qa-bot and security-bot: review F1-2, F1-3, F2-1, F3-1, F3-2 and E2E-1; security-bot should confirm the F1-3 #6 and #5 interpretations.
- backend-bot and qa-bot: derive tests from F1-3 and F3-2; make the log-inspection test (F3-2 #2) part of the suite.
