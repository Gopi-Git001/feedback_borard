# F5-1: Upvote a post (one vote per user per post)
Status: READY
As a member, I want to upvote a post once, so that the team can see which feedback matters most.

## Acceptance criteria
1. Given I am a member of "Acme" and I have not voted on post P (0 votes), When I click upvote on P, Then P shows 1 vote and my upvote control shows as active.
2. Given I have already voted on post P (1 vote from me), When I click upvote on P again (or the same vote request is sent a second time), Then my vote is removed and P shows 0 votes; I never have more than 1 vote on P.
3. Given two members A and B of "Acme" who have not voted on P, When A and B each upvote P once, Then P shows 2 votes, and each of them sees their own control as active.
4. Given post P belongs to organization "Beta", When a member of "Acme" tries to vote on P, Then the response is 404 and P's vote count is unchanged.
5. Given no post exists with the requested id, When I try to vote on it, Then the response is 404 and no vote is created.
6. Given I am not logged in, When I try to vote, Then the response is 401 and no vote is created.

## Business rules
- At most one vote per user per post, enforced by the data store, not only the UI.
- Vote toggling (removing own upvote) is allowed (brief ASSUMED); a second vote action by the same user removes the vote.
- Vote count = number of users who currently have a vote on the post.
- A user may vote on their own post (ASSUMED; not excluded by the brief).

## UI notes
- Each post shows an upvote control with the current count; the control looks active when I have voted.

## Data touched
- Vote: post, user, created time (unique per post + user).
- Post: vote count (derived).

## Out of scope
Downvotes, vote history, who-voted lists, vote limits per user.

## Assumptions / Questions
- ASSUMED: a user may upvote their own post.
- Brief status was DRAFT (fast-track) when this was written; READY status is conditional on brief approval (see handoff Open questions #1).
- ASSUMED (all stories): an admin has every member ability (post, vote, comment, view board). Authenticated user = valid login token; a missing/invalid token gives 401.
- API contract (TASK-001) did not exist yet. The TASK-002 spec names 403 (member on admin action) and 404 (cross-organization access); stories use no other HTTP code. ASSUMED: 401 for a missing or invalid login token (standard meaning; named in neither TASK-002 nor the brief). Recheck all codes against the contract when it lands.
