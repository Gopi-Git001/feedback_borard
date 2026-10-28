# ADR-003: Invite token handling (path token, log redaction)
Status: Proposed
Date: 2026-10-27   Deciders: architect-bot (proposes), Orchestrator (approves); security-bot to review

## Context
Story F3-1: each organization has **one persistent invite token**, the admin sees the same link every time, it is long and random (at least 32 characters) and reusable until the (post-MVP) revocation. The invite link is `<frontend-origin>/invite/<token>`; the SPA calls `GET /api/v1/invites/{token}` (public preview) and `POST /api/v1/invites/{token}/accept`. The token is therefore a **bearer secret in a URL path**. Uvicorn's default access log prints request paths, reverse proxies log them too, and browsers send the page URL in the `Referer` header. `data-model.md` said the token is "never logged", which was not true by default (qa-bot review, attempt 1). Because the story requires showing the same link again, the token is stored in clear in `invites.token` (not hashed).

## Options considered
1. **Keep the token in the path and redact it everywhere it can be logged (chosen).** Smallest change: contract, stories and the SPA route stay as they are.
2. Move the token to a request body or header (`POST /invites/preview` with `{token}`). Keeps it out of paths and logs, but changes two operations (preview becomes a POST), the contract and the frontend, and the invite page URL still contains the token (so `Referer` and browser history still need handling).
3. Token in a URL fragment (`/invite/#<token>`), read by JS and sent in a header. Fragments are not sent to servers or in `Referer`, but it changes the story's link format and every consumer.

## Decision
Option 1. Requirements (backend-bot and the frontend/devops owners must implement them; qa-bot tests them):
- **Access logs:** run uvicorn with its access log disabled (`--no-access-log`) and log requests with an application middleware that records the **route template** (`/api/v1/invites/{token}`, `/api/v1/invites/{token}/accept`) instead of the raw path, plus method, status and duration. The raw path of any `/api/v1/invites/*` request must never be written to any log.
- **Reverse proxy (nginx in docker compose):** the access log format must not contain `$request`, `$request_uri` or `$uri` for `/api/v1/invites/` and `/invite/` locations; use a `map` that replaces the token segment with `[redacted]` or turn the access log off for those locations.
- **Error tracking / exceptions:** strip or mask the token segment in URLs and breadcrumbs before sending or printing (a log filter that replaces `/invites/[A-Za-z0-9_-]{32,}` with `/invites/[redacted]`). Unhandled-exception logs must not include the request URL unredacted.
- **Responses:** all invite responses (`GET /invites/{token}`, `POST /invites/{token}/accept`, `POST /organizations/current/invite`) carry `Cache-Control: no-store`.
- **Referrer:** the SPA serves `/invite/<token>` with `Referrer-Policy: no-referrer` (response header and `<meta name="referrer" content="no-referrer">`), and the page contains no third-party resources.
- **Malformed token:** any token that does not match `^[A-Za-z0-9_-]{32,128}$` is answered with 404 `INVITE_NOT_FOUND` (message `Invite link is invalid`), the same as an unknown token, so nothing distinguishes the cases (matches story F2-1 acceptance criterion 4).
- Lookup is by exact match on the unique `invites.token` index; the token has 256 bits of entropy, so lookup timing is not a practical oracle. Preview and accept are rate limited (approved, ADR-002).
- Tests (qa-bot): a test that calls the invite endpoints and asserts that neither the captured application log nor the proxy log contains the token string.

## Consequences
- Easier: no contract or story change; the F3-1 behaviour (same link every time) is kept.
- Harder: logging must be configured deliberately in two places (app, proxy), and there is a test to keep it so.
- Residual risk: anyone who sees the link (chat, browser history, shared screen) can join the organization as a member until revocation exists; the invite link stays valid for the life of the MVP (story F3-1). Follow-up: regenerate/revoke invite (needs a new ADR because of `UNIQUE (organization_id)` on `invites`), optional encryption of `invites.token` at rest.
- If security-bot prefers option 2 or 3, that is a contract change (new ADR, Orchestrator approval).

## Sources
- Story F3-1 (docs/project/stories/F3-1-invite-link.md on main), data-model.md section 3.4 and 6, api-contract.yaml (Conventions, invite operations), ADR-002.
- uvicorn `--no-access-log` option ("Disable access log only, without changing log level"): https://github.com/Kludex/uvicorn/blob/main/docs/settings.md (docs on main, checked 2026-10-27; backend-bot to confirm against the pinned Uvicorn 0.54.0).
