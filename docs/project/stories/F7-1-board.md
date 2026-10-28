# F7-1: Board sorted by votes with type and status filters
Status: READY
As a member, I want to see my organization's posts sorted by votes and filter them by type and status, so that I can quickly find what matters.

## Acceptance criteria
1. Given "Acme" has posts X (3 votes), Y (5 votes) and Z (1 vote), When I open the board, Then the order is Y, X, Z (votes descending).
2. Given posts X and Y both have 2 votes and Y was created later than X, When I open the board, Then Y is listed before X (ties break by newest created time first).
3. Given "Acme" has posts of type idea and bug and statuses New and Planned, When I filter by type "bug", then only bug posts are shown; when I filter by status "Planned", only Planned posts are shown; when I apply both, only posts matching both are shown; and in each case the sort order of criteria 1 and 2 still applies.
4. Given "Acme" has 0 posts, When I open the board, Then I see "No posts yet" and a "New post" action; and given posts exist but none match my filters, Then I see "No posts match these filters" and a "Clear filters" action.
5. Given organization "Beta" has 4 posts and "Acme" has 2, When a member of "Acme" opens the board (with or without filters), Then exactly the 2 "Acme" posts are listed and none from "Beta".
6. Given I am not logged in, When I request the board, Then the response is 401 and no posts are returned.

## Business rules
- Sort: vote count descending, then created time descending (newest first). Applies after filtering.
- Type filter values: idea, bug. Status filter values: New, Planned, In Progress, Done. No filter selected means all.
- Filters combine with AND (ASSUMED).
- A filter value outside the lists above is rejected with a validation error and no posts are returned (ASSUMED).
- All matching posts are shown on one page, no pagination in the MVP (ASSUMED).

## UI notes
- Each board row shows title, type, status, vote count with upvote control, and comment count (comment count is ASSUMED display only).
- Two filter controls (type, status) with an "All" option.

## Data touched
- Post (read): title, type, status, created time, organization.
- Vote (read, count per post). Comment (read, count per post).

## Out of scope
Search, other sort orders, pagination, saving filters, per-user views.

## Assumptions / Questions
- ASSUMED: filters combine with AND; no pagination; invalid filter value gives a validation error.
- Brief status was DRAFT (fast-track) when this was written; READY status is conditional on brief approval (see handoff Open questions #1).
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- ASSUMED (all stories): API contract (TASK-001) did not exist yet; HTTP codes are used only where the task spec names them (401/403/404); recheck against the contract when it lands.
