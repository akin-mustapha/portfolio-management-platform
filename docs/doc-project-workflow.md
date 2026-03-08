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

- A task should be a single unit of work, covering just one intent and problem.
- It should be focused on just one architectural layer (e.g. do not make database changes and pipeline changes in the same task).
- **Layers in this project:** *(define your architectural layers here, e.g. database, API, pipeline, UI)*

## Bug

When you encounter a bug:

- **Document the bug**
  - Document bugs in *(specify location, e.g. `/docs/bugs` or the project wiki)*
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

**Pull Requests:**

- Open a PR when the branch is ready for review
- Assign a reviewer before merging
- PRs should be linked to their corresponding issue
- Do not merge without at least one approval
