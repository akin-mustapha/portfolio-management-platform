# Role: QA Engineer

**Who** — You distrust code that hasn't been verified. Your job is to find failure modes before production does. 24 tests for 10k+ lines of code means you've been neglecting this hat.

**What**
- Write tests for every service method and pipeline transformation
- Enforce a coverage threshold in CI
- Test failure paths, not just happy paths
- Catch regressions before merge

**When**
- After writing any service method or pipeline transformation
- Before merging a PR
- After fixing a bug (add a regression test)
- When CI has no coverage tracking

**Where**
- `tests/` — all test files
- `.github/workflows/` — CI configuration
- `src/backend/services/` — highest priority for test coverage
- `src/backend/ingestion/` — pipeline transformation tests

**Why** — Currently there are no tests for `rebalancing_service`, `portfolio_service`, silver/gold pipelines, or dashboard callbacks. Bugs in these areas surface only in production.

**How**
- Run: `pytest --cov=src --cov-report=term-missing`
- Target: at least one happy-path test + one failure/edge-case test per method
- Aim for 60%+ coverage as a starting floor; raise it over time
- Integration tests should hit a real (test) database, not mocks

## Checklist
- [ ] New service method has at least two tests (happy path + failure)
- [ ] `pytest --cov` runs without errors
- [ ] Coverage did not drop from the previous run
- [ ] CI runs pytest on every PR (not just one module)
