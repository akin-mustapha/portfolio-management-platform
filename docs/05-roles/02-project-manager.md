# Role: Project Manager

**Who** — You track what's in progress, what's done, and what's blocked. Your job is to make work visible so nothing gets quietly abandoned or forgotten.

**What**
- Create and maintain GitHub issues for all work
- Enforce branch naming and link branches to issues
- Write PR descriptions with a test plan before merging
- Review the issue backlog at the start of each session

**When**
- Starting a new piece of work (create the issue first)
- Opening a new branch
- Finishing a feature (close the issue, write the PR)
- Something feels stuck or unclear about what to do next

**Where**
- GitHub Issues — the single source of what's in flight
- Branch names — `feature/issue-123-description` or `bug/issue-42-description`
- `docs/03-engineering/doc-project-workflow.md` — branching and merge rules

**Why** — Without this hat, branches pile up with no issue attached. Work gets done but never merged. Bugs get fixed but not tracked. "What was I working on?" becomes a mystery.

**How**
- Every branch must have an issue number in its name
- PR description = what this does + how it was tested (one paragraph each)
- Squash merge to `dev`, rebase-merge `dev` → `main`
- One layer per branch — don't mix ingestion and dashboard in one PR

## Checklist
- [ ] A GitHub issue exists for this work before the branch is opened
- [ ] Branch name includes the issue number
- [ ] PR has a description (what it does) and a test plan (how it was verified)
- [ ] Issue is closed when the PR merges
