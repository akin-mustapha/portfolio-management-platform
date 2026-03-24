# Role: Product Manager

**Who** — You decide what to build and why. Every feature must answer a real question you have about your portfolio. If you can't name the question, you shouldn't build the feature.

**What**
- Define which portfolio questions the dashboard should answer
- Prioritise features against business value (your actual investment decisions)
- Ensure every new table, column, or chart is tied to a specific question
- Keep `ui-design.md` and `metrics-reference.md` current

**When**
- Starting a new feature or branch
- Deciding between two implementation approaches
- Adding a new metric or KPI
- Something exists in the dashboard that you never actually look at

**Where**
- `docs/01-product/business-requirements.md` — the why behind the system
- `docs/02-architecture/design/ui-design.md` — dashboard questions
- `docs/02-architecture/design/metrics-reference.md` — metric catalogue

**Why** — Without this hat, you build technically correct features that don't answer real questions. The dashboard fills with charts you never use. The gold layer grows speculatively.

**How**
- For every new feature: write one sentence — "This answers the question: ..."
- Check `metrics-reference.md` before adding a new metric — it may already exist
- Do not add gold layer columns speculatively; only build what a dashboard question requires
- Delete or archive charts you haven't looked at in 2+ sprints

## Checklist
- [ ] The feature is tied to a named dashboard question
- [ ] The metric is in `metrics-reference.md` (or added to it)
- [ ] No new columns or tables added "in case we need them later"
- [ ] `ui-design.md` updated if a new question is being answered
