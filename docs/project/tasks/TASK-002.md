# TASK-002: User stories with testable acceptance criteria for F1-F9
Owner: ba-bot   Milestone: M0   Size: M   Attempt: 1
Blocked by: none   Branch: feature/TASK-002-user-stories

## Goal
One story file per feature in docs/project/stories/, each with Given/When/Then acceptance criteria, so every later task is testable.

## Context (read these)
- docs/project/brief.md (MVP features F1-F9, roles, ASSUMED list)
- TEAM-CONVENTIONS.md (github.com/Gopi-Git001/Saas_Bot)

## Scope
- Stories for F1-F9 as docs/project/stories/F<n>-<slug>.md, using your write-user-stories skill.
- Run review-story-readiness on each; fix anything not ready.
- Cover: validation errors, duplicate email, wrong password, invite link invalid, vote twice (rejected or toggle per ASSUMED list), member trying admin actions (403), cross-organization access (404), empty board, filters and sort by votes (ties break by newest).
- Also add one end-to-end journey story matching the owner's definition of done: sign up, create org, invite a second user, post, vote, comment, change status.
- Do NOT change scope. If an acceptance question is unclear, list it under Open questions in the handoff; do not invent requirements.

## Acceptance criteria
- Given each feature F1-F9, then a story exists with at least one happy path and one failure-path criterion in Given/When/Then.
- Given the cross-organization rule, then at least one criterion per data-reading feature checks isolation.
- Given the journey story, then it maps step by step to the owner's done definition.

## Out of scope
Code, architecture, API design.

## Deliverables
- PR titled `TASK-002: ...` on the branch above
- Handoff report docs/project/handoffs/TASK-002-handoff.md
- Use your skills: write-user-stories, review-story-readiness, write-handoff-report
