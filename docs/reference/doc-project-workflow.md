---
name: project-workflow
description: Document highlighting project workflow
---

# Overview

This documentation provides the branch strategy for this project.

## New Feature

When adding a new feature:

- Create a story or epic
- Link the story/epic to a Git issue
- Set up a project branch named after the issue (e.g. `feature/issue-123-branch-name`)
- Limit branch changes to just the scope of the feature

## Documentation

When making documentation changes or adding new documentation:

- Create a branch using the format `doc/example-branch`
- Link the branch to a Git issue
- Keep changes focused on documentation only — do not mix with feature or bug changes

## Task

When working on a task:

- Identify the task and confirm it covers a single intent and problem
- Confirm the work belongs to a single architectural layer — do not mix changes across layers in one task
- Create a Git issue describing the task
- Set up a branch named after the issue (e.g. `feature/issue-123-branch-name`)
- Implement the change, limited to that layer
- Open a PR linked to the issue

**Layers in this project:**

| Layer | Responsibility |
|-------|---------------|
| `event_producer` | External data ingestion from Trading212 API via Kafka |
| `event_consumer` | Kafka event consumption and processing |
| `ingestion` | ETL pipelines — Bronze, Silver, and Gold transformations |
| `orchestration` | Prefect workflow scheduling and management |
| `services` | Portfolio domain business logic |
| `dashboard` | Analytics UI and frontend |
| `shared` | Cross-cutting infrastructure (database client, repos, utils) |
| `config` | Application configuration |

## Bug

When you encounter a bug:

- **Document the bug**
  - Document bugs in `docs/bugs/`
  - Name bug docs using the format: `bug-<issue-number>-<short-description>` (e.g. `bug-42-null-pointer-login`)
  - Include the error code, steps to reproduce, and how to generate the bug
- Create a TODO for the bug
- Research the bug
- Further document findings
- Create a Git issue
- Set up a project branch
- Limit branch changes to just the bug fix

## Git

**When to create a branch:** Branches should always be linked to an issue.

**How to name a branch:** Branches should be named after the issue (e.g. `feature/issue-123-branch-name` or `bug/issue-42-fix-name`).

**Commit messages:** Use clear, imperative commit messages referencing the issue number (e.g. `fix: resolve null pointer on login (#42)`).

**Merge strategy:**

- Squash merge feature and bug branches into `dev`
- Rebase-merge `dev` into `main` for releases

**Branch cleanup:**

- Delete the branch after the PR is merged (locally and remote)
- Any branch with no commits in 30 days should be reviewed and deleted or revived

**Pull Requests:**

- Use the PR template (`.github/pull_request_template.md`) to confirm readiness before requesting review
- Open a PR when the branch is ready for review
- Assign a reviewer before merging
- PRs should be linked to their corresponding issue
- Do not merge without at least one approval
