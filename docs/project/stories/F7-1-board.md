# F7-1: Board sorted by votes with type and status filters
Status: READY
As a member, I want to see my organization's posts sorted by votes and filter them by type and status, so that I can quickly find what matters.

## Acceptance criteria
1. Given "Acme" has posts X (3 votes), Y (5 votes) and Z (1 vote), When I open the board, Then the order is Y, X, Z (votes descending); and given posts X and Y both have 2 votes and Y was created later than X, Then Y is listed before X (ties break by newest created time first).
2. Given "Acme" has posts of type idea and bug and statuses New and Planned, When I filter by type "bug", then only bug posts are shown; when I filter by status "Planned", only Planned posts are shown; when I apply both, only posts matching both are shown; and in each case the sort order of criterion 1 still applies.
3. Given "Acme" has 0 posts, When I open the board, Then I see "No posts yet" and a "New post" action (ASSUMED texts); and given posts exist but none match my filters, Then I see "No posts match these filters" and a "Clear filters" action (ASSUMED texts).
4. Given organization "Beta" has 4 posts and "Acme" has 2, When a member of "Acme" opens the board (with or without filters), Then exactly the 2 "Acme" posts are listed and none from "Beta".
5. Given I am a member of "Acme", When I request the board with an unknown type value "feature" or an unknown status value "Blocked", Then the request is rejected with a validation error naming the filter, and no posts are returned (ASSUMED behaviour; the brief does not define it).
6. Given I am not logged in, When I request the board, Then the response is 401 and no posts are returned.

## Business rules
- Sort: vote count descending, then created time descending (newest first). Applies after filtering.
- Type filter values: idea, bug. Status filter values: New, Planned, In Progress, Done. No filter selected means all.
- Filters combine with AND (ASSUMED).
- A filter value outside the lists above is rejected with a validation error and no posts are returned (ASSUMED; criterion 5).
- All matching posts are shown on one page, no pagination in the MVP (ASSUMED).

## UI notes
- Each board row shows title, type, status, vote count with upvote control, and comment count (comment count is ASSUMED display only).
- Two filter controls (type, status) with an "All" option (ASSUMED label).

## Data touched
- Post (read): title, type, status, created time, organization.
- Vote (read, count per post). Comment (read, count per post).

## Out of scope
Search, other sort orders, pagination, saving filters, per-user views.

## Assumptions / Questions
- ASSUMED: filters combine with AND; no pagination; invalid filter value gives a validation error (criterion 5; see handoff Open questions).
- ASSUMED: exact UI texts "No posts yet", "No posts match these filters", "New post", "Clear filters", "All" (the brief gives no wording).
- Brief status was DRAFT (fast-track) when this was written; READY status is conditional on brief approval (see handoff Open questions #1).
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- HTTP codes: 403 and 404 are named in TASK-002; 429 and the other error codes come from the API contract; 401 is ASSUMED (the contract lists it but itself marks it ASSUMED). Recheck once the contract is merged to main.
