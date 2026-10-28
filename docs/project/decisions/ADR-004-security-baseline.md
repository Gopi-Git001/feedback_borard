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
| `Cache-Control` | `no-store` | `/api/v1/auth/*`, `/api/v1/organizations*`, `/api/v1/invites/*` (tokens, tenant data); also `/api/v1/auth/me` |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | only when served over HTTPS (not in local http compose); no `preload` |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` | everywhere |
| `Cross-Origin-Opener-Policy` | `same-origin` | SPA |
- The SPA must work under this CSP: **no inline scripts and no inline `style` attributes** (use CSS classes); no third-party scripts, fonts or images. If frontend-bot proves that a library needs inline style attributes, the only allowed relaxation is `style-src-attr 'unsafe-inline'` (decided in a PR, not silently). The Vite dev server needs a looser policy and is for local development only. The Playwright harness must fail a test on any CSP violation in the browser console.
- The backend sets its headers with one middleware; the frontend container sets its own in nginx (`add_header ... always`).

### 2. XSS and user content
- All user-supplied text (post title and description, comments, display names, organization names) is **rendered as text only**: React's default escaping, **no `dangerouslySetInnerHTML`, no Markdown or HTML rendering**, no URL auto-linking in the MVP. frontend-bot adds a lint rule against `dangerouslySetInnerHTML` (the lint stack is pinned in stack.md; the exact rule is the owner's choice).
- This matters because an XSS bug would still be able to call `POST /auth/refresh` (ADR-002, residual risk).

### 3. CSRF, cookies, CORS
- The refresh cookie is `HttpOnly; Secure; SameSite=Strict; Path=/api/v1/auth`.
- **Origin check plus custom header on the cookie endpoints** (`/auth/refresh`, `/auth/logout`): `X-Requested-With: feedback-board` is required and a present `Origin` must equal `FRONTEND_ORIGIN`; otherwise 403 `FORBIDDEN`, no state change. All other endpoints use the `Authorization` header (not sent automatically by browsers), so they are not CSRF-prone.
- **The `Secure` flag is on unless `APP_ENV` is not `production`.** A config flag may switch it off only for plain-http local development; the app **refuses to start** when `APP_ENV=production` and the flag is off.
- **CORS:** the SPA and the API are same-origin through the nginx proxy, so no CORS is needed in compose. If the backend is called cross-origin (local dev), allow exactly `FRONTEND_ORIGIN` (one explicit origin, never `*`), with credentials, methods `GET, POST, PATCH, DELETE`, headers `Authorization, Content-Type, X-Requested-With`.

### 4. Logging and error responses
- Never logged: request bodies of `/auth/*` and `/invites/*`, and the `Authorization`, `Cookie` and `Set-Cookie` headers; passwords, hashes, tokens, `JWT_SECRET`, `INVITE_TOKEN_KEY`. Error tracking (if added) strips bodies and those headers before sending.
- 400 `VALIDATION_ERROR` `details` contain the field name and the rule only, **never the submitted value** (the FastAPI `input` and `ctx` values are dropped when 422 is remapped to 400). The same applies to logs of validation errors.
- Structured access log: method, route template, status, duration, request id; user id and organization id when known. Emails are not written in clear in error logs.

### 5. Database access
- The backend connects as a **non-owner, non-superuser PostgreSQL role** with SELECT, INSERT, UPDATE, DELETE on the application tables and USAGE on sequences if any; no DDL, no `BYPASSRLS`. Alembic migrations run with a separate owner role (one extra compose service or env var `DATABASE_MIGRATION_URL`). The compose `db` init creates both roles.
- Row-Level Security is **scheduled** as the next hardening step (data-model.md section 1): with a non-owner role in place, `ENABLE ROW LEVEL SECURITY` plus a policy on `organization_id = current_setting('app.organization_id')::uuid` per tenant table and `SET LOCAL app.organization_id` per transaction can be added without changing the API. Not in the MVP.
- Tenant checks: authentication (401), then lookup scoped to the organization (404 for another organization's rows), then role (403), on **every** endpoint that takes a post id, including sub-resources `/posts/{id}/vote`, `/posts/{id}/comments`, `/posts/{id}/status` and `DELETE /posts/{id}` (conventions in api-contract.yaml).

### 6. Accounts and passwords (what is and is not done)
- Minimum 8 characters stays (story F1-1); maximum 128; Argon2id (ADR-002). **Not met, follow-ups:** the minimum is below NIST SP 800-63B-4 (15 for single-factor use) and OWASP ASVS (12), there is no check against breached-password lists, and there is no password change, reset or email verification flow (no emails in the MVP). When a change or reset flow is added it must revoke all refresh-token families of the user.
- `409 EMAIL_TAKEN` on signup is required by story F1-1 and is an enumeration oracle; mitigated by the per-IP signup limit only (ADR-002). A generic response would contradict the story and is not done.
- Rate limits, counter store, proxy trust and the env vars that tune them: ADR-002.

## Consequences
- Easier: one checklist for backend-bot, frontend-bot, devops-bot and qa-bot; each rule is testable (header assertions, CSP-violation check in Playwright, log-content tests, startup refusal tests).
- Harder: the CSP rules out inline styles and third-party assets; two database roles must be provisioned; the SPA must send the CSRF header on refresh and logout.
- Not covered (honest limits): HSTS and TLS termination are only meaningful with a real HTTPS deployment, which is out of scope for the MVP (local docker compose); no WAF, no dependency-vulnerability gate beyond what CI adds later; no audit-log table (data-model.md section 8).

## Sources
- Browser header semantics: MDN Web Docs (Content-Security-Policy, Referrer-Policy, Strict-Transport-Security, Permissions-Policy); not re-read in this attempt beyond what the security-bot review quoted, so backend-bot and security-bot should confirm exact syntax at implementation time.
- Findings: security-bot comment on PR #2 (https://github.com/Gopi-Git001/feedback_borard/pull/2#issuecomment-6457850545).
