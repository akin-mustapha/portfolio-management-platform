---
name: docs
description: Use this skill when updating, auditing, or creating project documentation. Covers which docs exist, what each owns, and which are trustworthy vs. aspirational.
---

# Why

Docs in this project drift from the code after refactors. This skill tells you which doc to update for a given change, which docs to trust, and which to treat as design intent only.

# The Golden Rule

**The code is the authority. Docs are intent.** When a doc contradicts the code, the code is correct — and the doc needs updating. Never adjust code to match a doc.

# Trustworthiness Rating

| Doc | Trust | Notes |
|---|---|---|
| `schema-reference.md` (skill reference) | ✅ High | Kept in sync manually — most accurate schema source |
| `docs/02-architecture/design/schema/schema-staging.md` | ✅ High | Most accurate schema doc in the docs folder |
| `docs/02-architecture/design/schema/schema-analytics.md` | ✅ High | Most accurate schema doc in the docs folder |
| `docs/02-architecture/architecture.md` | ⚠️ Medium | Accurate structure, some detail may lag code |
| `docs/02-architecture/design/ingestion/doc-pipelines.md` | ⚠️ Medium | Pattern is correct, specific implementations may drift |
| `docs/02-architecture/design/doc-data-model.md` | ⚠️ Medium | Field names have drifted — `tag_type` in doc is `Category` in code |
| `docs/02-architecture/design/ui-design.md` | 🔵 Design intent | Gold layer tables referenced don't exist yet (now implemented) |
| `docs/03-engineering/doc-commands.md` | ✅ High | Commands are stable and accurate |
| `docs/03-engineering/doc-project-workflow.md` | ✅ High | Git/PR workflow — rarely changes |
| `docs/04-bugs/bug_prefect.md` | 🔵 Historical | Bug log, not a living doc |

# Doc Map — What Each File Owns

```
docs/
  01-product/
    business-requirements.md     — Product goals and what the system must do

  02-architecture/
    architecture.md              — 4-layer architecture overview (source of truth for structure)

    design/
      doc-data-model.md          — Tagging model: Asset, Tag, Category, Industry, Sector
      doc-migration.md           — Migration strategy and Alembic workflow
      metrics-reference.md       — Metrics definitions (what each KPI means)
      ui-design.md               — Dashboard questions driving gold layer design

      ingestion/
        doc-pipelines.md         — Pipeline pattern: Source/Transformation/Destination
        pipeline_asset_data.md   — Asset pipeline design detail
        pipeline_account_data.md — Account pipeline design detail
        events.md                — Kafka event design

      schema/
        schema-staging.md        — Silver layer schema (most accurate doc)
        schema-analytics.md      — Gold layer schema (design intent, not built)

  03-engineering/
    doc-commands.md              — All CLI commands: Alembic, Docker, Prefect, tests
    doc-project-workflow.md      — Git branching, PR process, merge strategy
    doc-setup.md                 — Local environment setup
    refactor-ingestion-clean-architecture.md — Record of the clean architecture refactor

  04-bugs/
    bug_prefect.md               — Prefect-specific bug notes
```

# Update Checklist — After a Code Change

Use this to decide what docs need touching after each type of change:

**Schema change (new table, column, or migration)**
- [ ] Update `schema-staging.md` or `schema-analytics.md`
- [ ] Update `schema-reference.md` in the `/database` skill references
- [ ] If it changes a business key: update the Business Keys section in `schema-reference.md`

**New or modified pipeline**
- [ ] Check `doc-pipelines.md` — update if the pattern changed
- [ ] Check `pipeline_asset_data.md` or `pipeline_account_data.md` if the specific pipeline changed

**Architecture restructuring**
- [ ] Update `architecture.md`
- [ ] Check all import paths referenced in docs are still valid

**New dashboard feature or tab**
- [ ] Update `ui-design.md` — add the dashboard question it answers
- [ ] If it needs a gold layer table: add the question to `ui-design.md` first, then design the table

**New metric or KPI**
- [ ] Update `metrics-reference.md` with the definition and formula

# What NOT to Update

- Do not update `schema-analytics.md` speculatively. Only update it when a gold layer table is actually being built.
- Do not update `bug_prefect.md` unless you've confirmed it's a new, reproducible Prefect issue.
- Do not update `doc-data-model.md` field names to match the doc — the code field names are correct.
