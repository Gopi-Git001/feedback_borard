# ADR-004: Security baseline (headers, CSP, CSRF guard, CORS, logging, database role)
Status: Proposed (new in attempt 2b, from the security-bot review of PR #2, should-fix 5 and 6 and notes 7, 9, 11, 12, 13)
Date: 2026-10-27   Deciders: architect-bot (proposes), Orchestrator (approves); security-bot to re-review

## Context
The review found that browser hardening, CSRF handling, cache and log rules and the database role were not specified. This ADR is the one place where those cross-cutting rules live; ADR-002 (auth, rate limits) and ADR-003 (invite token) refer to it. It adds no feature and no endpoint.

## Decision

### 1. Response headers
| Header | Value | Where |
|---|---|---|
| `Content-Security-Policy` (SPA) | `default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'` | every response of the frontend nginx |
| `Content-Security-Policy` (API) | `default-src 'none'; frame-ancestors 'none'` | every backend response |
| `X-Content-Type-Options` | `nosniff` | everywhere |
| `Referrer-Policy` | `no-referrer` | everywhere (ADR-003) |
| `Cache-Control` | `no-store` | **every response under `/api/v1/*`**, success and error (401, 403, 404, 429 too), set by the backend middleware; the SPA's hashed static assets may be cached (`immutable`), `index.html` is `no-cache` |
| `Strict-Transport-Security` | `max-age=31536000` | **only on HTTPS responses**: in the nginx `server` block that terminates TLS (or when a trusted proxy reports `X-Forwarded-Proto: https`), never on plain http, so the local http compose sends no HSTS (a test asserts the header is absent there); no `preload`; `includeSubDomains` only when the operator knows every subdomain is HTTPS-only (not the default) |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` | everywhere |
| `Cross-Origin-Opener-Policy` | `same-origin` | SPA |
- The SPA must work under this CSP: **no inline scripts, no `<style>` elements and no `style="..."` attributes in served or injected HTML** (use CSS classes; `style-src 'self'` blocks them; styles that React applies through the DOM `style` property are set via CSSOM and are not blocked by CSP, but the Playwright console check must prove it, and anything that fails it is not allowed); no third-party scripts, fonts or images. If frontend-bot proves that a library needs inline style attributes, the only allowed relaxation is `style-src-attr 'unsafe-inline'` (decided in a PR, not silently). The Vite dev server needs a looser policy and is for local development only. The Playwright harness must fail a test on any CSP violation in the browser console.
- The backend sets its headers with one middleware; the frontend container sets its own in nginx with `add_header ... always`. **nginx `add_header` inheritance:** directives are inherited from the enclosing level only if the current level has no `add_header` of its own, so one `add_header` inside a `location` silently drops all server-level headers there. Therefore the security headers live in one file `security-headers.conf` that is `include`d in **every** `location` (static files, `/api/`, error pages) next to any location-specific header, and a test (devops-bot, qa-bot) requests `/`, a static asset, `/api/v1/health`, a 404 and a proxied 502 and asserts the headers on each.

### 2. XSS and user content
- All user-supplied text (post title and description, comments, display names, organization names) is **rendered as text only**: React's default escaping, **no `dangerouslySetInnerHTML`, no Markdown or HTML rendering**, no URL auto-linking in the MVP. frontend-bot adds a lint rule against `dangerouslySetInnerHTML` (the lint stack is pinned in stack.md; the exact rule is the owner's choice).
- This matters because an XSS bug would still be able to call `POST /auth/refresh` (ADR-002, residual risk).

### 3. CSRF, cookies, CORS
- The refresh cookie is `HttpOnly; Secure; SameSite=Strict; Path=/api/v1/auth`.
- **Origin check plus custom header on the cookie endpoints** (`/auth/refresh`, `/auth/logout`): `X-Requested-With: feedback-board` is required and a present `Origin` must equal `FRONTEND_ORIGIN` exactly; otherwise 403 `FORBIDDEN`, no state change. **`Origin: null` is present and unequal, so it gets 403**. Because every response sends `Referrer-Policy: no-referrer`, a browser sends `Origin: null` on a non-GET request whose fetch mode is not `cors` (WHATWG Fetch, "append a request Origin header", checked 2026-10-27): so the SPA must call the API with the default `fetch()` mode `cors` and never `mode: 'same-origin'` or `'no-cors'`, and must not use form posts or navigations for `/auth/*`; a Playwright test must show that refresh and logout from the real SPA are not rejected. (Sandboxed iframes and some cross-origin redirects also send `Origin: null`; a correctly written SPA never does.) `FRONTEND_ORIGIN` must be a bare origin (`scheme://host[:port]`, no path, no trailing slash, validated at startup). All other endpoints use the `Authorization` header (not sent automatically by browsers), so they are not CSRF-prone.
- **The `Secure` flag is on by default.** `APP_ENV` is required and fails closed (ADR-002: unset or not `development`/`test`/`production` means the app does not start). The environment variable `COOKIE_SECURE` (default `true`) may switch it off only when `APP_ENV` is `development` or `test`, for plain-http local development; the app **refuses to start** when `APP_ENV=production` and the flag is off.
- **CORS:** the SPA and the API are same-origin through the nginx proxy, so no CORS is needed in compose. If the backend is called cross-origin (local dev), allow exactly `FRONTEND_ORIGIN` (one explicit origin, never `*`), with credentials, methods `GET, POST, PATCH, DELETE`, headers `Authorization, Content-Type, X-Requested-With`.

### 4. Logging and error responses
- Never logged: request bodies of `/auth/*` and `/invites/*`, and the `Authorization`, `Cookie` and `Set-Cookie` headers; passwords, hashes, tokens, `JWT_SECRET`, `INVITE_TOKEN_KEY`. Error tracking (if added) strips bodies and those headers before sending.
- 400 `VALIDATION_ERROR` `details` contain the field name and the rule only, **never the submitted value** (the FastAPI `input` and `ctx` values are dropped when 422 is remapped to 400). The same applies to logs of validation errors.
- Structured access log: method, route template, status, duration, request id; user id and organization id when known. Emails are not written in clear in error logs.

### 5. Database access
- The backend connects as a **non-owner, non-superuser PostgreSQL role** with SELECT, INSERT, UPDATE, DELETE on the application tables and USAGE on sequences if any; no DDL, no `BYPASSRLS`. The backend reads `DATABASE_URL` (the restricted role); Alembic migrations run with a separate owner role given by `DATABASE_MIGRATION_URL` (a one-shot compose service or the same image with that variable). The compose `db` init creates both roles.
- Row-Level Security is **scheduled** as the next hardening step (data-model.md section 1): with a non-owner role in place, `ENABLE ROW LEVEL SECURITY` plus a policy on `organization_id = current_setting('app.organization_id')::uuid` per tenant table and `SET LOCAL app.organization_id` per transaction can be added without changing the API. Not in the MVP.
- Tenant checks: authentication (401), then lookup scoped to the organization (404 for another organization's rows), then role (403), on **every** endpoint that takes a post id, including sub-resources `/posts/{id}/vote`, `/posts/{id}/comments`, `/posts/{id}/status` and `DELETE /posts/{id}` (conventions in api-contract.yaml).

### 6. Accounts and passwords (what is and is not done)
- Minimum 8 characters stays (story F1-1); maximum 128; Argon2id (ADR-002). **Not met, follow-ups:** the minimum is below NIST SP 800-63B-4 (15 for single-factor use; OWASP ASVS 5.0.0 6.2.1 requires 8 and recommends 15, so 8 meets the ASVS minimum), there is no password blocklist (ASVS 6.2.4, top 3000, level 1) and no check against breached-password lists (ASVS 6.2.12, level 2), and there is no password change, reset or email verification flow (no emails in the MVP). When a change or reset flow is added it must revoke all refresh-token families of the user.
- `409 EMAIL_TAKEN` on signup is required by story F1-1 and is an enumeration oracle; mitigated by the per-IP signup limit only (ADR-002). A generic response would contradict the story and is not done.
- Rate limits, counter store, proxy trust and the env vars that tune them: ADR-002 (10 requests per 60 s per IP per endpoint by default, rolling window). Every environment variable with default and owner is in the table in `stack.md`. **End-to-end, load and CI test runs (TASK-010, TASK-013) must set `RATE_LIMIT_ENABLED=false` or raise the limits through the `RATE_LIMIT_*` variables**, because the SPA calls refresh on every page load and one client IP would otherwise hit 429 after 10 calls in 60 s; this is allowed only with `APP_ENV` `development` or `test` and never in production.

### 7. Known limits (accepted risks, not fixed in the MVP)
- **No rate limit on authenticated writes** (posts, comments, votes, status changes, deletes): the approved scope (brief, F1-2) limits only signup, login, refresh, invite preview/accept (plus the architect-added organization create). A signed-in member can therefore create posts and comments as fast as the server allows; the damage stays inside the member's own organization. Follow-up: nginx `limit_req` or a per-user write limit using the same `rate_limit_hits` table.
- **Request body size:** nginx sets `client_max_body_size 64k` (ASSUMED; the largest legitimate body is a 2000-character description, at most about 8 KB in UTF-8 plus JSON) so the backend never buffers large bodies. Over-size requests get nginx's 413, which is not a JSON error body and not in the contract; the SPA treats any non-2xx as an error. Pydantic field limits (contract) apply inside that size.
- Access tokens stay valid until they expire after logout, reuse detection or eviction (at most 15 minutes, plus 30 s leeway), ADR-002.

### Accepted-risk register (needs human acceptance)
Approver: **Gopi Thungam (pending, asked 2026-10-27)**. Status of every row is **pending**; nothing here is approved until the Orchestrator reports that he confirmed it.

| # | Accepted risk | Why accepted for the MVP | Status |
|---|---|---|---|
| R1 | **No per-account lockout.** Per-account lockout is out of scope (story F1-2) and not offered; only the per-IP limit exists | Story scope; avoids a lockout denial-of-service on a victim's account | pending |
| R2 | **Access token stays valid up to 15 min (plus 30 s leeway, so up to 15 min 30 s) after logout, reuse detection or eviction** (ADR-002) | Stateless access token; no per-request revocation lookup | pending |
| R3 | **Per-IP limit versus NAT users:** many users behind one shared IP share the 10 per 60 s budget and can lock each other out of signup, login and refresh; one attacker with many IPs is not stopped | Approved per-IP design (brief, F1-2); the limits are configurable (`RATE_LIMIT_*`) | pending |
| R4 | **Signup `409 EMAIL_TAKEN` is an account-enumeration oracle**; mitigated by the per-IP signup limit only | Required by story F1-1 | pending |
| R5 | **No rate limit on authenticated writes** (posts, comments, votes, status changes, deletes) | Not in the approved scope; damage stays inside the member's own organization | pending |
| R6 | **Invite link has no expiry, no revoke and no regenerate, and there is no remove-member** | Out of the approved MVP scope (not in the brief's list); a key rotation (ADR-003) is the only way to invalidate links | pending |
| R7 | **The DDL and the contract were not run against PostgreSQL** (design only); SQL in data-model.md and ADR-002 is untested | No application or database exists in TASK-001; backend tests must prove it | pending |

## Consequences
- Easier: one checklist for backend-bot, frontend-bot, devops-bot and qa-bot; each rule is testable (header assertions, CSP-violation check in Playwright, log-content tests, startup refusal tests).
- Harder: the CSP rules out inline styles and third-party assets; two database roles must be provisioned; the SPA must send the CSRF header on refresh and logout.
- Not covered (honest limits): HSTS and TLS termination are only meaningful with a real HTTPS deployment, which is out of scope for the MVP (local docker compose); no WAF, no dependency-vulnerability gate beyond what CI adds later; no audit-log table (data-model.md section 8).

## Sources
- Browser header semantics: MDN Web Docs (Content-Security-Policy, Referrer-Policy, Strict-Transport-Security, Permissions-Policy); not re-read in this attempt beyond what the security-bot review quoted, so backend-bot and security-bot should confirm exact syntax at implementation time.
- Findings: security-bot comment on PR #2 (https://github.com/Gopi-Git001/feedback_borard/pull/2#issuecomment-6457850545).
