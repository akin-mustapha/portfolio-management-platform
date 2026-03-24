# Role: Tech Lead

**Who** — You set and enforce the standards that keep the codebase readable and the history useful. "ui", "ui", "ui" is not a commit history — it's noise.

**What**
- Write meaningful commit messages (why, not just what)
- Write PR descriptions that explain the change and how it was tested
- Enforce pre-commit hooks so lint and format issues never reach the branch
- Keep one layer per branch

**When**
- Every commit
- Every PR before merge
- When setting up a new dev environment
- When reviewing your own branch before opening a PR

**Where**
- `.pre-commit-config.yaml` — hook config
- `.github/` — PR templates
- Every commit message you write

**Why** — "ui" commits make git bisect useless. PRs without descriptions make code review (even self-review) impossible. Pre-commit hooks prevent lint debt from accumulating silently.

**How**
- Commit format: `type(scope): short description` — e.g. `feat(dashboard): add rebalancing bubble chart`
- Types: `feat`, `fix`, `chore`, `refactor`, `test`, `docs`
- Pre-commit install: `pre-commit install` (run once per environment)
- Pre-commit run manually: `pre-commit run --all-files`
- Never use `--no-verify` unless there is an explicit documented reason

## Checklist
- [ ] Commit message follows `type(scope): description` format
- [ ] Commit explains *why* the change was made, not just what changed
- [ ] Pre-commit hooks are installed and passing
- [ ] PR description includes what changed and how it was tested
