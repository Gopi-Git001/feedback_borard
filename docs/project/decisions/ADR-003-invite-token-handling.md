# ADR-003: Invite token handling (URL fragment, POST body, derived token, log hygiene)
Status: Proposed (rewritten in attempt 2b after the security-bot review of PR #2, blocker 2 and should-fix 3; **supersedes** the Attempt 2 decision "keep the token in the URL path and redact it in logs")
Date: 2026-10-27   Deciders: architect-bot (proposes), Orchestrator (approves); security-bot to re-review

## Context
Story F3-1: each organization has **one persistent invite token**, the admin sees the same link every time, it is long and random (at least 32 characters) and reusable. The token is a **bearer secret**: whoever holds it can join the organization as a member.

Attempt 2 kept the token in the URL path (`/invite/<token>`, `GET /invites/{token}`, `POST /invites/{token}/accept`) and relied on log redaction. The security review rejected that (blocker 2): the token still reaches uvicorn and proxy logs, error tracking and `Referer` if any one redaction is missed, and because the token is permanent and cannot be revoked, one leak is permanent. It also asked not to store the token in clear (finding 3).

## Options considered
Where the token travels:
1. Path or query (Attempt 2). **Rejected:** every server, proxy and tool on the path sees it by default.
2. **URL fragment for the link, POST body for the API (chosen).** The browser never sends a fragment to any server and never puts it in `Referer`; the SPA reads it and sends it in a JSON body, and request bodies are not logged by default.
3. Custom header from the SPA. Equivalent for logs, but a JSON body is simpler for the contract and for tests; not chosen.

How the token is stored (F3-1 forbids a different link on each click, so a salted hash alone cannot work):
1. Plaintext column (Attempt 2). **Rejected:** a database dump or backup reveals working links.
2. Encrypted copy with a separate key. Works, but stores a reversible secret and needs a nonce and key handling.
3. **Derived token, only its hash stored (chosen).** `token = base64url(HMAC-SHA256(INVITE_TOKEN_KEY, "invite:v" + token_version + ":" + organization_id))` without padding (43 characters, 256 bits). The database stores only `sha256(token)` in `invites.token_hash` plus `token_version`. The admin endpoint recomputes the token on demand, so the same link is shown every time; a database leak alone gives nothing usable. Bumping `token_version` would later give "regenerate link" with no schema change.

## Decision
Option 2 for transport and option 3 for storage.

**Link and API**
- The shareable link is `<frontend-origin>/join#<token>`. `POST /organizations/current/invite` (admin, get-or-create) returns `{token, created_at}`; the SPA builds the link.
- `POST /invites/preview` (public) and `POST /invites/accept` (signed in, no organization yet) take `{"token": "..."}` in the body. **No token in any path or query, ever.**
- Malformed, wrong-length, unknown tokens all give 404 `INVITE_NOT_FOUND` (message `Invite link is invalid`), never 400, so nothing distinguishes the cases (story F2-1 criterion 4). The body schema is only "string, max length 512"; validation never echoes the value.
- Lookup is `WHERE token_hash = sha256(token)` (unique index). The value has 256 bits of entropy, so lookup timing is not a practical oracle. Preview is limited per IP and accept per user (ASSUMED numbers, ADR-002).

**Server-side requirements (backend-bot, devops-bot; qa-bot tests them)**
- `INVITE_TOKEN_KEY`: a new secret, same startup rule as `JWT_SECRET` (decodes to at least 32 bytes, ADR-002), different from `JWT_SECRET`, never in the database, repo or logs. Anyone who has this key and an organization id can compute that organization's link, so it is as sensitive as `JWT_SECRET`. Rotating it invalidates all links (a deliberate "revoke everything").
- **Bodies are never logged:** the access-log middleware records method, route template, status and duration only; the bodies of `/api/v1/invites/*` and `/api/v1/auth/*` and the `Authorization`, `Cookie`, `Set-Cookie` headers are never logged, and error-tracking hooks drop request bodies and those headers. The 422-to-400 remapping must not copy the offending `input` value into the response or the log.
- **Reverse proxy (nginx):** access-log format without `$request_body`, `$http_authorization`, `$http_cookie`. (The token is not in `$request_uri` any more; this is defence in depth.)
- **Responses:** all invite responses (`POST /invites/preview`, `POST /invites/accept`, `POST /organizations/current/invite`) carry `Cache-Control: no-store`.
- **Referrer:** the SPA is served with `Referrer-Policy: no-referrer` (response header and `<meta name="referrer" content="no-referrer">`), and the `/join` page loads no third-party resources (CSP, ADR-004). A fragment is not sent in `Referer` in any case; the policy is a second layer.

**SPA requirements (frontend-bot)**
- `/join` reads `location.hash`, **immediately removes it from the address bar** with `history.replaceState` (it should not stay in history or screenshots) and keeps the token in memory.
- If the visitor is logged out, the token is kept in `sessionStorage` under one key (`pending_invite`) while they sign up or log in, then `/join` resumes; the key is deleted after accept succeeds or fails and on logout. This is the one deliberate use of Web Storage; it holds only an invite token (the access token never goes to storage, ADR-002).
- Show "Invite link is invalid" for any 404 from preview or accept.

**Tests (qa-bot):** call the invite endpoints and assert that neither the captured application log nor the proxy log contains the token string or a request body; assert `Cache-Control: no-store`; assert that no request URL in the Playwright trace contains the token.

## Consequences
- Easier: the token cannot appear in a server-visible URL, so one missed log filter no longer leaks it; a database dump gives no usable links; F3-1 behaviour (the same link every time) is kept.
- Harder: preview becomes a POST for a read (documented; no side effects); stories F2-1, F3-1, E2E-1 change their link text and flow (handoff lists them); the SPA needs a small pending-invite flow; one more secret (`INVITE_TOKEN_KEY`) to provision.
- **Residual risk, not fixed (product scope, F3-1, decided by the Orchestrator):** the link is permanent and reusable, there is **no expiry, no revoke, no regenerate and no remove-member** in the MVP. Anyone who obtains the link (chat, browser history before the fragment is stripped, shared screen) can join as a member forever and an admin cannot undo it. Follow-ups in order of value: (1) an admin "regenerate link" (bump `token_version`, one endpoint), (2) expiry, (3) remove member (needs a design for the member's posts, comments and votes; the composite FKs are `ON DELETE RESTRICT`).
- If `INVITE_TOKEN_KEY` leaks together with organization ids, links can be recomputed; the fix is rotating the key. If the team prefers fully random stored tokens, the fallback is a plaintext or encrypted `token` column (Attempt 2 design plus encryption); say so and I will revise.

## Sources
- Story F3-1 and F2-1 (docs/project/stories/ on main), data-model.md sections 3.4 and 6, api-contract.yaml (invite operations, Conventions), ADR-002, ADR-004.
- URI fragments are not part of the HTTP request: RFC 3986 section 3.5 (https://www.rfc-editor.org/rfc/rfc3986#section-3.5). HMAC: RFC 2104.
