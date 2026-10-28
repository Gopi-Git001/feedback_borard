# Product Brief: Team Feedback Board
Status: DRAFT (fast-track; approval requested together with stack and plan)

## Problem
Teams collect ideas and bug reports in scattered places. They need one shared board per team where members post, upvote and discuss feedback, and admins triage it by status.

## Target users and roles
- admin: creates the organization, invites members, changes post status, deletes posts.
- member: creates posts, upvotes, comments.

## Business model
Free. No billing, no plans.

## Tenancy
Multi-tenant by organization. A user only ever sees their own organization's data. A user belongs to one organization (ASSUMED for MVP).

## MVP features
| ID | Feature | User story | Priority |
|----|---------|-----------|----------|
| F1 | Sign up / log in | As a user, I sign up with email + password so I can access my board | Must |
| F2 | Organization | As a new user, I create an organization (and become admin) or join one via an invite link | Must |
| F3 | Invites | As an admin, I generate an invite link to copy and share | Must |
| F4 | Posts | As a member, I create a post with title, description, and type (idea or bug) | Must |
| F5 | Upvotes | As a member, I upvote a post once (one vote per user per post) | Must |
| F6 | Comments | As a member, I comment on a post | Must |
| F7 | Board | As a member, I see posts sorted by votes and filter by type and status | Must |
| F8 | Status | As an admin, I move a post New -> Planned -> In Progress -> Done | Must |
| F9 | Delete | As an admin, I delete a post | Must |

## Later (post-MVP)
Email notifications, billing, multiple orgs per user, SSO, edit/delete own posts, search.

## Out of scope
Billing, emails, mobile apps, cloud deployment, paid services, external auth services.

## Integrations
None.

## Non-functional requirements
- Passwords hashed; JWT auth; tenant isolation enforced on every query and test-covered.
- `docker compose up` starts everything (db, backend, frontend).
- CI on GitHub Actions runs backend tests, frontend checks, and Playwright e2e.

## Constraints
Pre-approved stack: FastAPI, PostgreSQL, SQLAlchemy + Alembic, React + TypeScript (Vite), built-in email/password + JWT, pytest, Playwright, docker compose, GitHub Actions. architect-bot verifies and pins current stable versions.

## Assumptions (ASSUMED)
- One organization per user for the MVP.
- Invite links are single org, reusable until revoked (revocation is not in MVP); the token is long and random.
- Status can be changed in any direction by an admin, not only forward.
- Members cannot edit or delete posts.
- Vote toggling (remove own upvote) is allowed.

## Open questions
None blocking.

## Change log
- 2026-10-27: initial draft from the user's requirements.
