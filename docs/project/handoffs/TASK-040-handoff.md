# Handoff: TASK-040 Align stories with the revised auth and invite design
Bot: ba-bot   Attempt: 3   PR: https://github.com/Gopi-Git001/feedback_borard/pull/5   Branch: fix/TASK-040-auth-and-invite-redesign

Security review: touches authentication (security-bot review required). Stories that touch authentication: F1-1, F1-2, F1-3 (new in Attempt 1), F1-4, F1-5, F1-6, F2-2, F3-3 (new in Attempt 3), F2-1, F3-1, F3-2 (new in Attempt 1), E2E-1.

Checked against PR #2 (https://github.com/Gopi-Git001/feedback_borard/pull/2), branch feature/TASK-001-stack-and-contracts, **head 6a961c348b35439b5b1ddc5aa88d615885b2b9cc** (Attempt 3 of the PR #2 design; the parent agent named this head and I re-read the files from it on 2026-10-27, America/Chicago). Files read from that head: docs/project/architecture/api-contract.yaml, architecture/data-model.md, decisions/ADR-002, ADR-003, ADR-004, handoffs/TASK-001-handoff.md. Attempts 1 and 2 of this task were checked against head **0459573b4c6ece0c2af58794b345520060b00fc1**; **the PR #2 head moved during Attempt 3** (my first re-fetch in this attempt showed 0459573, and the statement "head unchanged" that I wrote then was wrong by the time of this commit). Main was at 2240765 (PR #4 merged); api-contract.yaml is still not on main. See "PR #2 delta" below for the values that changed between 0459573 and 6a961c3.

Open questions: see "Open questions" below. Conflicts and accepted risks have their own sections.

Review history: Attempt 1 = commit 280c465 (PR #5 head 7c40954 is the same content applied on main 2240765). Attempt 2 = commit 0e79ec2, pushed as PR #5 head 005347b (Orchestrator decisions: drop the login lockout, rate limits per IP as in the brief, stale contract lines fixed, leftovers recorded). Attempt 2 = CHANGES_REQUESTED by qa-bot (PR #5 comment 6458217382, head 005347b): two must-fix issues (false "F4-1 to F9-1 unchanged" statements; stale old-design text and numbering in the TASK-039 handoff) and suggestions. Attempt 3 = this version (security-bot comment on PR #5: PASS with should-fix items, https://github.com/Gopi-Git001/feedback_borard/pull/5#issuecomment-6458253424; architect-bot's story-vs-contract mismatch list in the TASK-001 handoff; parent steering message with PR #2 head 6a961c3).

## Summary
F1-2 now follows the revised session design (rotation, family revoked by logout, 7-day absolute cap, no 429 on logout) and a new F1-3 holds reuse detection, the X-Requested-With and Origin guard and the bearer-token rule. F3-1 now uses the link /join#<token> with POST preview and accept; a new F3-2 covers hash-only storage, no token in any request URL, fragment removal, the logged-out sessionStorage flow, the uniform 404 and the accept rate limit. F2-1, E2E-1 and F1-1 were updated, the TASK-039 handoff was corrected, and TASK-039.md and TASK-040.md were written retroactively. Nothing outside docs/project/stories/, handoffs/ and tasks/ changed.

## Summary of Attempt 3 additions
New stories: F1-4 (cookie flags, headers on success and error responses, log hygiene), F1-5 (logout versus refresh races, session cap), F1-6 (password 8 and 128 accepted, 7 and 129 rejected), F2-2 (403 ORG_REQUIRED, ASSUMED), F3-3 (invite key rotation). Changed: F1-1, F1-2, F1-3 (new criterion 6, Origin: null), F2-1, F3-1, F3-2, E2E-1 (#1 cookie flags, #10 extended) and the footers of F4-1, F6-1, F9-1.

## Attempt 2 changes
- **F1-3: per-account login limit removed** (5 failed attempts per 900 s). Account lockout is out of scope (Orchestrator decision; architect-bot is dropping it from the contract and ADR-002). F1-3 now has 5 criteria (reuse, leeway, header guard, Origin guard, bearer rule), which is still within 3-6. Cross-references fixed in F1-1, F1-2 and this handoff; E2E-1 and F3-x never mentioned it.
- **Rate limits decided:** the brief's 10 requests per 60 s per IP per endpoint is the decision, including invite accept per IP. F3-2 now says per IP in the criterion, the business rule and the assumptions (it said per user).
- **Stale contract-check lines** in F4-1, F6-1 and F9-1 replaced (only those lines). Finding: api-contract.yaml is still absent from origin/main (`git ls-tree -r origin/main` shows no contract file), so the lines now say it is on PR #2 (Proposed, head 0459573).
- **Known leftovers** recorded in one Open-questions entry (no new criteria).
- **PR #2 head in Attempt 2: 0459573b4c6ece0c2af58794b345520060b00fc1** (fetched in Attempt 2; same commit as in Attempt 1, so nothing I relied on had changed then). It moved later (see Attempt 3). Note: the contract and ADR-002 on that head still contain the per-account login limit and the per-user accept limit until architect-bot aligns them, so the stories and the contract disagree on those two points for now.

## Attempt 3 changes
- **False "unchanged" statements fixed** (qa-bot Issue 1) in this handoff and in tasks/TASK-040.md: F5-1, F7-1 and F8-1 are untouched; F4-1, F6-1 and F9-1 changed only in their last "Contract check" footer line (Attempt 2); no criterion of F4-1 to F9-1 changed. Checked with `git diff --name-only origin/main` and by grepping "unchanged" and F4-1 to F9-1 in this handoff, TASK-040.md and TASK-039.md. In Attempt 3 the footer line of F4-1, F6-1 and F9-1 was changed once more, only to say head 6a961c3 (still the same footer line; no criterion changed).
- **TASK-039 handoff** (qa-bot Issue 2): a note at the top says it is superseded in part by TASK-040 (PR #5); the GET /invites/{token} text now points to POST /invites/preview and /invites/accept with {token} in the body and /join#<token>; F1-2 numbers updated (#1 to #4 refresh, rotation, 7-day cap, logout; #5 sign-up and login 429; #6 refresh 429; 6 criteria); "rolling 60 seconds" replaced. Also added a supersession note to tasks/TASK-039.md. Grep of that handoff for "GET /", "private", "lockout", "rolling" and old criterion numbers is clean except the explicit "(TASK-040 numbering ...)" notes.
- **Rate-limit wording** (qa-bot suggestion 1): "rolling 60 seconds" and "last 60 seconds" replaced in F1-2, F3-1, F3-2 and the TASK-039 handoff by "10 requests per 60-second window per IP per endpoint; window type is an implementation detail and tests must not depend on the boundary". Criteria now say "within one 60-second window ... the 11th request in that window"; F1-2 Assumptions give a boundary-independent test technique (a burst of 21 and at least one 429; no assertion on which request is the first 429; a valid request succeeds after the Retry-After seconds). The contract and ADR-002 at head 6a961c3 describe a rolling (sliding) window; the stories do not depend on the window type. (The phrases "rolling" and "last 60" now appear in the stories and handoffs only where this handoff or a story quotes the contract.)
- **F3-2 #5** (qa-bot suggestion 2): the examples are now a 10-character token (too short) and a 100-character token of valid base64url characters (too long; valid under both contract heads). Contract finding at head 0459573 (maxLength removed at 6a961c3, see the PR #2 delta): InviteTokenRequest.token is `type: string, maxLength: 512` ("Any value that is not a valid token gives 404, not 400"); the conventions and ADR-003 say malformed, wrong-length or unknown tokens give 404 INVITE_NOT_FOUND, never 400; preview and accept declare no 400 response. The contract does not state what a token longer than 512 characters, or a missing or non-string `token`, returns (by schema validation probably 400 VALIDATION_ERROR). No separate criterion (it would need a slot); see Open question 9.
- **Message-text labels made consistent** (qa-bot suggestion 3, small, beyond the Orchestrator's list): all four texts that the contract gives verbatim are now labelled contract-sourced with their location, none as ASSUMED: "Invite link is invalid" (api-contract.yaml NotFound response and previewInvite description; ADR-003 Decision), "Email already registered" (Conflict response, EMAIL_TAKEN), "You already belong to an organization" (Conflict response, ALREADY_IN_ORGANIZATION), "Invalid email or password" (login operation description). The contract is still Proposed. Touches F1-1, F2-1, F3-2. Revert if the Orchestrator prefers ASSUMED.
- **TASK-040.md** header now Attempt 3, scope, acceptance criteria and out-of-scope updated (F1-3 and F3-2 criteria, lockout removed, rate-limit decision, footer lines), plus a Files list.
- **Not changed on purpose:** qa-bot suggestions 5 to 9 (the tasks/ folder question is for the Orchestrator; the F3-1 note about a new token family and invite key rotation are informational and belong to architect-bot).
- **PR #2 head: the first fetch in Attempt 3 showed 0459573; the later fetch and the parent's message show 6a961c348b35439b5b1ddc5aa88d615885b2b9cc.** The earlier text of this handoff said "no value changed"; that was wrong for 6a961c3 and is replaced by the PR #2 delta below.
- **Steering items (parent agent, security-bot PASS comment, architect-bot mismatch list), all in the same commit:**
  1. Refresh cookie flags and no-store, asserted in e2e: F1-4 #1, #2, #3, #4 and E2E-1 #1 (context.cookies()).
  2. Logout-versus-refresh race and the other concurrency tests: F1-5 #1, #2, #6 (and #3 to #5 for the cap and re-login).
  3. INVITE_TOKEN_KEY rotation: F3-3 (6 criteria, including the ADR-003 test vector that I re-computed and that matches).
  4. Per-account login limit stays out of scope: Out-of-scope lines of F1-1, F1-2, F1-3, and the "Accepted risks" section below; no criterion.
  5. Rate limits 10 per 60 s per IP per endpoint on sign-up, login, refresh, invite preview and invite accept, env-configurable (RATE_LIMIT_*_PER_IP), RATE_LIMIT_ENABLED=false in e2e, boundary-independent: F1-2 #5, #6; F3-1 #6; F3-2 #6; stale ADR-002 numbers, "per user" accept wording and "Retry-After greater than 0 ASSUMED" removed (the contract now says Retry-After minimum 1).
  6. Headers on error responses too (F1-4 #4); E2E-1 #10 extended (no Referer with the token, no console leak, no Web Storage leak except the documented `pending_invite` sessionStorage use, no #token left in the address bar).
  7. Log hygiene beyond the invite token: F1-4 #5 (passwords, tokens, Authorization, Cookie, Set-Cookie, auth and invite bodies, emails).
  8. Password boundaries: F1-6. The contract's limits are signup 8 to 128 and login 1 to 128 with 400 VALIDATION_ERROR, so they match the Orchestrator's 8 and 128 accepted, 7 and 129 rejected; no difference. A login with a 7-character password is not a validation error (INVALID_CREDENTIALS 401).
  Also: F1-3 #6 (Origin: null and Origin variants give 403, security-bot low item).
- **Architect-bot mismatch list (matched by content, not line number):** F1-2 (rate-limit numbers, Retry-After, per-account limit, cross-references, footer head); F1-1 (password limits now 8 to 128 with F1-6 cross-reference, footer head); F3-1 (43-character format with alphabet, Retry-After, ADR-002 default sentence, footer head); E2E-1 (out-of-scope line about token storage, footer head); F2-1 (shape check without a request, pasted link, ALREADY_IN_ORGANIZATION with 409, footer head); accept rate limit per IP (F3-2); 403 ORG_REQUIRED (new story F2-2, ASSUMED). F3-2: the "contract wording still says per user" sentence and the maxLength 512 note were updated. Nothing from the list is left over except the items in Open questions.
- **PR #2 delta, 0459573 to 6a961c3, and its effect on the stories:** (1) the contract has no `maxLength: 512` on InviteTokenRequest.token any more; any token length gives 404, only a missing or non-string token gives 400 (F3-2 #5 and its note updated); (2) Retry-After has minimum 1 (the ASSUMED "greater than 0" is removed from F1-2, F3-1, F3-2); (3) the per-account login limit is gone from the contract and ADR-002 (F1-3 footer); (4) the invite accept limit is per IP and the limiter is the first step of each limited endpoint (F3-2 #6); (5) rate limits are env-configurable with defaults 10/60 (the "different defaults" sentences removed); (6) Origin: null gives 403 (F1-3 #6); (7) per-family advisory lock, session cap of 10 with `evicted`, login revokes the presented family (F1-5); (8) ADR-004 headers on every response incl. errors, log rules (F1-4); (9) the key-rotation rule and test vector of ADR-003 (F3-3); (10) ORG_REQUIRED order of checks (F2-2). All values quoted in the stories were re-read at 6a961c3.


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
| TASK-039 handoff: repo public, Q5/Q9 updated, Q11 kept, ASSUMED kept | met (Attempt 3: also superseded notes and current numbering) | TASK-039-handoff.md top note, Summary, Q5, Q9, Q11 |
| Security review line on F1-2, F3-1, F2-1, E2E-1, F1-3, F3-2 (and in this handoff) | met | line under Status in each story; line 4 here; also added to F1-1 (see Decisions) |
| TASK-039.md and TASK-040.md exist (Goal, Scope, Acceptance criteria, retroactive note) | met | docs/project/tasks/TASK-039.md, TASK-040.md |
| F4-1 to F9-1: no criterion changed | met, except the one stale Contract-check footer line in F4-1, F6-1 and F9-1 (Orchestrator-requested in Attempt 2); F5-1, F7-1, F8-1 untouched | `git diff --name-only origin/main` lists F4-1-posts.md, F6-1-comments.md and F9-1-delete-post.md (footer line only) and none of F5-1, F7-1, F8-1 |
| Readiness re-run on every changed story | met, with the gaps below | Test results table |
| Re-check PR #2 head before finishing | met | head 0459573 in Attempts 1 and 2; head 6a961c3 in Attempt 3 (it moved during the attempt; values re-read from 6a961c3) |
| Attempt 2: login lockout criterion removed from F1-3, cross-references fixed | met | F1-3 has 5 criteria; `grep -n -i "per-account\|6th\|lock" docs/project/stories/*.md` finds only the out-of-scope notes in F1-2 and F1-3 and the contract-check note in F1-3 (it says the contract still mentions a per-account limit); this handoff also mentions it, to say it was removed |
| Attempt 2: accept limit per IP in F3-2 | met | F3-2 #6, Business rules, Assumptions |
| Attempt 2: stale contract-check lines in F4-1, F6-1, F9-1 | met | last line of each file (only those lines changed) |
| Attempt 2: leftovers recorded, header and PR link updated | met | Open questions Q4; line 2 of this file |
| Attempt 3: stale "unchanged" statements corrected everywhere | met | this file (acceptance table, Files changed, readiness paragraph), tasks/TASK-040.md scope and out of scope |
| Attempt 3: TASK-039 handoff updated to current design and numbering, supersession note | met | TASK-039-handoff.md lines 6, 11, 18, 20, 49, 66, 69, 73, 87 |
| Attempt 3: rate-limit wording boundary-independent | met | `grep -n -i "last 60\|within the last" docs/project/stories/*.md` finds nothing; the word "rolling" now appears only where a story or this handoff quotes the contract's own wording; F1-2 #5, #6, F3-1 #6, F3-2 #6 |
| Attempt 3: F3-2 #5 example within maxLength 512; contract finding reported | met | F3-2 #5 (10 and 100 characters), F3-2 open-point note; Conflicts section (ADR-003 "max 512") |
| Attempt 3: "Invite link is invalid" source checked | met (verbatim in the contract) | F2-1 #4 and Assumptions, F3-2 Business rules; locations named in Attempt 3 changes |
| Attempt 3: F1-4 cookie flags, headers on success and error responses, log hygiene | met | F1-4 #1 to #6, E2E-1 #1 |
| Attempt 3: F1-5 concurrency tests and session cap | met | F1-5 #1 to #6 (ADR-002 tests a to d) |
| Attempt 3: F3-3 key rotation | met | F3-3 #1 to #6 |
| Attempt 3: per-account login limit out of scope, listed as accepted risk | met | Out of scope in F1-1, F1-2, F1-3; Accepted risks section; no criterion |
| Attempt 3: rate limits aligned with head 6a961c3, boundary-independent | met | F1-2 #5, #6; F3-1 #6; F3-2 #6 and Assumptions |
| Attempt 3: E2E-1 #10 extended (Referer, console, Web Storage, address bar) | met | E2E-1 #10 |
| Attempt 3: password 8 and 128 accepted, 7 and 129 rejected | met (matches the contract) | F1-6 #1 to #4 |
| Attempt 3: 403 ORG_REQUIRED | met (ASSUMED) | F2-2 #1 to #5 |
| Attempt 3: architect-bot story-vs-contract mismatches | met | list under Attempt 3 changes |

## Files changed
- docs/project/stories/F1-1-signup-login.md (security line; trimming and display-name limits contract-sourced; password limits and message labels; cross-references to F1-4 to F1-6; accepted-risk text; footer head 6a961c3)
- docs/project/stories/F1-2-session-and-rate-limits.md (6 criteria; rate-limit wording, Retry-After and ADR-002 text aligned to 6a961c3; accepted risk; footer)
- docs/project/stories/F1-3-session-hardening.md (NEW in Attempt 1; Attempt 3: criterion 6 for Origin: null, now 6 criteria; accepted risk; footer)
- docs/project/stories/F1-4-cookie-headers-and-log-hygiene.md (NEW, 6 criteria)
- docs/project/stories/F1-5-session-concurrency-and-session-cap.md (NEW, 6 criteria)
- docs/project/stories/F1-6-password-rules.md (NEW, 6 criteria)
- docs/project/stories/F2-1-organization-create-join.md (criteria 3, 4, 5, 6; rules including the pasted link and shape check; footers)
- docs/project/stories/F2-2-organization-required.md (NEW, 5 criteria)
- docs/project/stories/F3-1-invite-link.md (link format, rules, 43-character format, rate limit, footers)
- docs/project/stories/F3-2-invite-token-protection.md (NEW in Attempt 1; Attempt 3: #5, #6, notes, footer)
- docs/project/stories/F3-3-invite-key-rotation.md (NEW, 6 criteria)
- docs/project/stories/E2E-1-owner-journey.md (step 3, criterion 1 cookie flags, criterion 10 extended, test environment, footers)
- docs/project/stories/F4-1-posts.md, F6-1-comments.md, F9-1-delete-post.md (only the last "Contract check" footer line; no criterion changed)
- docs/project/handoffs/TASK-039-handoff.md (public repo; Q5 and Q9 resolved or superseded; Attempt 3: supersession note, current numbering and wording)
- docs/project/handoffs/TASK-040-handoff.md (this file)
- docs/project/tasks/TASK-039.md (retroactive; supersession note)
- docs/project/tasks/TASK-040.md (retroactive; Attempt 3 scope, criteria, files)
Not touched: brief.md, plan.md, board.md, code, api-contract.yaml, ADRs, and the criteria of F4-1 to F9-1. F5-1, F7-1 and F8-1 are not touched at all.

## How to test locally
Docs only, nothing to run. Review: (1) `git diff --name-only origin/main` lists only the files above; (2) each new or changed criterion can be turned into a test with the values given; (3) every value in a story that is not in the contract, ADRs or the Orchestrator's list is marked ASSUMED (or, for the ORG_REQUIRED rule, the cap of 10 sessions and the 401 status, labelled as ASSUMED in the contract or ADR); (4) check the contract-sourced values against `git show 6a961c3:docs/project/architecture/api-contract.yaml` (fetch the branch first) (and ADR-002, ADR-003 in docs/project/decisions/); (5) count criteria per story: `awk '/^## Acceptance criteria/{a=1;next} /^## /{a=0} a&&/^[0-9]+\. /{c++} END{print c}' <file>`.

## Test results
No automated tests (docs task). I re-ran review-story-readiness on every changed or new story myself (not independent; qa-bot and security-bot review). Criteria counted with the awk command above: F1-1 6, F1-2 6, F1-3 6, F1-4 6, F1-5 6, F1-6 6, F2-1 6, F2-2 5, F3-1 6, F3-2 6, F3-3 6, E2E-1 10 (justified exception). No `QUESTION:` item in any story (grep). Every story has the security-review line.

| Story | Ready? | Gaps / questions |
|-------|--------|------------------|
| F1-1 signup-login (6) | READY | Attempt 3: password limits, cross-references and accepted-risk text. Criterion 3 bundles four validation groups. 401 (#6) ASSUMED. Contract is Proposed (head 6a961c3). |
| F1-2 session-and-rate-limits (6) | READY | #3 and #4 are multi-clause. Thresholds 10 per 60-second window per IP per endpoint are ASSUMED (brief.md), decided by the Orchestrator; window wording boundary-independent; Retry-After minimum 1 now contract-sourced. 7-day test needs a controllable clock (ASSUMED technique). 429 criteria must be backend tests (e2e has limits off). 401 ASSUMED in the contract. |
| F1-3 session-hardening (6) | READY | 401 for a refresh token used as a bearer token ASSUMED. A 401 inside the leeway not clearing the cookie is ASSUMED. Permission case = the 403 guard and Origin criteria (#3, #4, #6). |
| F1-4 cookie-headers-and-log-hygiene (6) NEW | READY | Exact CSP and header syntax is ADR-004's and is not re-verified (ADR-004 says so). #5 needs log access. Permission case = the 403 in #4; there is no role case on public auth endpoints. |
| F1-5 session-concurrency-and-session-cap (6) NEW | READY | The cap of 10 (#3, #4) is an architect addition (ASSUMED in ADR-002, not in the brief). Needs concurrency test hooks (technique ASSUMED, from ADR-002). Permission case = the 403 without guard in #6. |
| F1-6 password-rules (6) NEW | READY | Public endpoints, so no role permission case (error cases #3 to #5). "Refused before hashing" is an inference from ADR-002. Character counting for non-ASCII input unspecified (ASSUMED ASCII). |
| F2-1 organization-create-join (6) | READY | The logged-out sessionStorage flow is F3-2 #4 (6-criterion cap). 403 ORG_REQUIRED is now F2-2. |
| F2-2 organization-required (5) NEW | READY | The whole rule (code ORG_REQUIRED) and the 401 status are ASSUMED in the contract. Permission case = #1, error cases = #4, #5. Criterion 4 needs the test to remove a membership row. |
| F3-1 invite-link (6) | READY | Preview threshold ASSUMED (brief.md, decided). Storage and URL secrecy in F3-2; key rotation in F3-3. |
| F3-2 invite-token-protection (6) | READY | #2 bundles URL, log, body and header checks and needs log access. #3 is browser behaviour. The 400 case (missing or non-string token) has no criterion (full). ADR-003 still says "max length 512" (conflict, see Conflicts). |
| F3-3 invite-key-rotation (6) NEW | READY | ADR-003's rotation rule awaits security-bot confirmation. Needs app restart or key set by env in tests. Vector re-computed and matches. Permission case = #5. |
| E2E-1 owner-journey (10) | READY | 10 criteria on purpose (one flow). #1 now also checks cookie flags; #10 reads the whole-run trace, console and Web Storage. Secure cookie flag depends on COOKIE_SECURE in e2e. |

Definition of Ready: all boxes are checked for the rows above, except that "no conflict with other stories or the API contract" is checked against a contract that is still Proposed on PR #2 (head 6a961c3), and that "traces to the approved brief" holds for F1-4, F1-6, F3-3 and E2E-1 only through the brief's human-approved additions and the security-bot review; F1-5's cap and F2-2's rule are architect additions (ASSUMED). F4-1 to F9-1 were not re-reviewed; no criterion of them changed. F5-1, F7-1 and F8-1 are untouched; F4-1, F6-1 and F9-1 changed only in the last "Contract check" footer line.

## Decisions made (and why)
- **Contract and ADRs win over the Orchestrator's list** where they differ; the differences are listed in these decisions and under Open questions.
- **F1-2 split.** Rotation, 7-day cap, logout and the two rate-limit criteria fill F1-2's 6 slots. Reuse detection, the CSRF guard and the bearer rule went to the new F1-3-session-hardening.md. The file F1-2-session-and-rate-limits.md keeps its name so existing references stay valid.
- **F3-1 split.** F3-1 keeps its 6 criteria (link shape, same link, member 403, join and isolation, 401, preview 429). Hash-only storage, no token in request URLs or logs, fragment removal, the logged-out flow, the uniform 404 and the accept rate limit are in the new F3-2-invite-token-protection.md.
- **sessionStorage criterion lives in F3-2 #4, not F2-1.** F2-1 has 6 criteria and no slot; F2-1's rules and UI note state the flow and point to F3-2 #4. If the Orchestrator wants it inside F2-1, F2-1 needs a 7th criterion or another new story (F2-2 is now the ORG_REQUIRED story).
- **"Invite link is invalid" is not labelled ASSUMED**, because the contract (NotFound response description and previewInvite description) and ADR-003 give that text verbatim. The contract is still Proposed, so the stories say "contract-sourced" and name the location. In Attempt 3 the same rule is applied to "Email already registered", "Invalid email or password" and "You already belong to an organization" (all verbatim in the contract), which Attempt 1 had left ASSUMED.
- **Display-name trimming is contract-sourced now** (contract conventions and SignupRequest: trim, then validate 1-80, store the trimmed value). The Orchestrator said to keep it ASSUMED unless the contract states it, so I removed the ASSUMED label from the story; brief.md still says "ASSUMED trimming" (Q6).
- **F1-1 out-of-scope line.** PR #4 had already reduced it to "... avatars, session renewal, log out and rate limiting (these three are in F1-2)". I removed that part completely, since those three are now in scope (F1-2, F1-3).
- **Security-review line also added to F1-1** (not in the Orchestrator's list), because sign-up and login handle passwords and issue sessions. Remove it if not wanted.
- **Rate-limit numbers: decided by the Orchestrator (Attempt 2).** The brief's 10 requests per 60 s per IP per endpoint (ASSUMED in brief.md) is the decision, for sign-up, login, refresh, invite preview and invite accept (accept per IP). The contract and ADR-002 at head 6a961c3 use the same default (10 per 60 s per IP per endpoint), so there is no difference any more (they say "rolling"/sliding; the stories stay independent of the window type). The stories already used the brief's number.
- **Per-account login limit removed from F1-3 (Attempt 2).** Orchestrator decision: an account lockout is out of scope (it would let an attacker lock a victim out; architect-bot dropped it from the contract and ADR-002 at head 6a961c3). The criterion, its ASSUMED threshold (5 failed attempts per 900 s), the ASSUMED "6th attempt with the correct password is blocked" and the "login lock" business rule were deleted; F1-3 renumbered (the bearer-token criterion is now #5).
- **E2E-1 #10 added** (journey now 10 criteria) instead of folding the token check into step 3, so it can fail separately. RATE_LIMIT_ENABLED=false is written as a test-environment setting (ADR-002 and the Orchestrator); rate-limit criteria are not part of the journey.
- **TASK-039 handoff corrections.** Line 9 no longer says the repo is private. I did not verify why the earlier fetch of TEAM-CONVENTIONS.md failed, and that file lives in the separate Saas_Bot repo, whose visibility I did not check; the handoff says so. Q5 (logout 429) is marked resolved and Q9 (no revocation) superseded, because PR #2 removed the logout 429 and added server-side revocation. Q11 (403 ORG_REQUIRED) is kept as a leftover and all ASSUMED labels are kept.
- **Spec files TASK-039.md and TASK-040.md** are retroactive, written from the Orchestrator's messages as relayed to me; they carry that note.

- **New stories instead of extra criteria (Attempt 3).** F1-1, F1-2, F1-3, F2-1, F3-1 and F3-2 were full (6), so the steering items became F1-4, F1-5, F1-6, F2-2 and F3-3 (naming `<FEATURE-ID>-<n>-<slug>.md`, cross-referenced). F1-3 had a free slot and took the Origin: null criterion. The Orchestrator may merge them into the feature stories' numbering later.
- **ORG_REQUIRED got its own story F2-2** (5 criteria, ASSUMED label kept) instead of staying a leftover, because it fits.

## PR #2 delta and conflicts with the Orchestrator's decisions
Where the contract at head 6a961c3 or an ADR differs from the Orchestrator's decision, the stories follow the Orchestrator and the difference is listed here:
1. **Per-IP rate limit versus security-bot's concerns.** The Orchestrator keeps the brief's 10 per 60 s per IP per endpoint, including accept per IP. Security-bot's PASS comment notes that one shared IP address (NAT, office) can lock out several users, and that the sign-up 409 EMAIL_TAKEN is an account-existence oracle that only this per-IP limit slows down. Both are accepted risks below.
2. **Window type.** The contract and ADR-002 say rolling (sliding); the stories say "per 60-second window ... window type is an implementation detail, tests must not depend on the boundary". No conflict in values; the stories are deliberately looser.
3. **No account lockout and no per-account login limit** (Orchestrator). The contract at 6a961c3 already agrees; security-bot asks for the human's sign-off (accepted risk 1).
4. **ADR-003 versus the contract on token length.** ADR-003 still says the token field is a string with "max length 512"; the contract at 6a961c3 has no limit and any length gives 404. The contract wins (F3-2 note). Architect-bot should update ADR-003.
5. **Architect additions that are not in the brief:** the cap of 10 active sessions per user with `evicted` (F1-5 #3, #4) and the per-user 429 on `POST /organizations` (no criterion; leftover). Both are marked ASSUMED; the Orchestrator may drop F1-5 #3 and #4.
6. **brief.md** still says display-name trimming is ASSUMED, while the contract states it (unchanged conflict; brief.md is not mine to edit).

## Accepted risks (no criterion; need the human's sign-off, as security-bot asked)
1. **No per-account login limit or lockout.** Password guessing against one account is limited only by 10 login requests per minute per IP. Distributed guessing across IP addresses is not limited. Mitigations in the stories: password minimum 8, Argon2id, uniform INVALID_CREDENTIALS. No breached-password check, no password composition rules. Listed in Out of scope of F1-1, F1-2, F1-3 and F1-6.
2. **Shared IP address (NAT).** 10 requests per minute per endpoint per IP can block several legitimate users behind one address, especially on refresh.
3. **Account existence through sign-up (409 EMAIL_TAKEN)** is visible; only the per-IP limit slows it.
4. **Access tokens stay valid after logout, reuse or eviction** until they expire (15 minutes; ADR-002).
5. **Header syntax** (CSP, Referrer-Policy) is not verified against browser documentation (ADR-004).

## Open questions
1. **PR #2 is still moving.** Contract status is "Proposed"; ADR-002 and ADR-003 are Proposed; security-bot has not confirmed the ADR-003 rotation rule. Head checked: 6a961c3. Any change to the guard header value, the leeway (10 s), the 43-character token, the pending_invite key, the rate-limit scope, the cap of 10 sessions or the rotation rule changes F1-2 to F1-5, F2-1, F2-2, F3-1 to F3-3 or E2E-1.
2. **brief.md calls display-name trimming ASSUMED**, the contract states it. Orchestrator may align the brief.
3. **Retry-After**: resolved at head 6a961c3 (minimum 1 in the contract); no longer ASSUMED.
4. **Leftovers, no criteria:** (b) the per-user 429 on `POST /organizations` (contract note "drop it if it is out of scope"; not in brief.md; architect addition at 6a961c3 with 10/60). (a) ORG_REQUIRED is now F2-2 and (c) the 10-session cap is now F1-5 #3 and #4 (both ASSUMED).
5. **401 is ASSUMED in the contract** (conventions, Unauthorized response); the same holds for the 401 in F1-3 #5 and F2-2 #4, #5. Needs the Orchestrator's confirmation.
6. **Test environment:** rate limits are off in e2e (RATE_LIMIT_ENABLED=false), so the 429 criteria (F1-2 #5, #6, F3-1 #6, F3-2 #6, F1-4 #4's 429) are backend or component tests with small limits. F1-5 and F3-3 are backend integration tests (concurrency, key). qa-bot to plan.
7. **sessionStorage criterion in F3-2 #4**, not F2-1 (6-criterion cap); say if it should move.
8. **F1-1 also has the security-review line** (not in the original list); remove if not wanted.
9. **Missing or non-string `token`** in preview and accept gives 400 VALIDATION_ERROR (contract at 6a961c3); there is no criterion for it (F3-2 is full). Add a criterion or a new story if wanted. (The 512-character question is resolved: any length is 404.)
10. **ADR-003 says "max length 512"** while the contract has none; architect-bot to align the ADR.
11. **Accepted risks** above need the human's sign-off (security-bot's request); I cannot give it.

## Suggested follow-up tasks
- Orchestrator: update brief.md for trimming (Q2); get PR #2 approved with the contract and ADR-002 aligned to the decisions above (no per-account login limit, per-IP accept limit, brief's rate-limit numbers), then ask me for a small recheck of the "Contract check" lines once the contract is on main.
- ba-bot (small): when api-contract.yaml is on main, change the "Contract check" lines in F4-1, F6-1 and F9-1 (and the TASK-040 lines elsewhere) to say it is on main.
- qa-bot and security-bot: review F1-2, F1-3, F2-1, F3-1, F3-2 and E2E-1; security-bot should confirm the F1-3 #5 interpretation (401 for a refresh token used as a bearer token).
- backend-bot and qa-bot: derive tests from F1-3 and F3-2; make the log-inspection test (F3-2 #2) part of the suite; cover the Q4 leftovers in backend tests.
