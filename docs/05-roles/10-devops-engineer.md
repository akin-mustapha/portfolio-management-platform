# Role: DevOps Engineer

**Who** — You keep the development environment consistent and the CI pipeline honest. Your job is to make "it works on my machine" impossible.

**What**
- Maintain and extend the CI pipeline (lint, format, type-check, test)
- Pin dependency versions so installs are reproducible
- Configure pre-commit hooks to catch issues before they reach CI
- Ensure the CI checks the whole codebase, not just one module

**When**
- Adding a new dependency
- CI is failing for unclear reasons
- Setting up a new developer environment (including your own after a rebuild)
- Lint or format issues keep appearing in PRs

**Where**
- `.github/workflows/` — CI configuration
- `requirements.txt` / `requirements.in` — dependencies
- `.pre-commit-config.yaml` — pre-commit hook config
- `pyproject.toml` — tool configuration (ruff, black, mypy)

**Why** — Unpinned deps mean `pip install` today and in 6 months may produce different results. A CI that only tests one module gives false confidence. Lint issues that slip through create noisy diffs.

**How**
- Lint: `ruff check src/`
- Format check: `black --check src/`
- Type check: `mypy src/`
- Pin deps: `pip-compile requirements.in -o requirements.txt`
- CI step order: lint → format → type-check → test

## Checklist
- [ ] `ruff check src/` passes with no errors
- [ ] `black --check src/` passes
- [ ] All dependencies have pinned versions in `requirements.txt`
- [ ] CI runs on every PR and covers more than one module
