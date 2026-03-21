---
name: database
description: Use this skill when answering schema questions, writing queries, or working on migrations. Covers all three medallion layers.
---

# Why

This gives you the full schema context so you can answer database questions, write correct queries, and validate migration changes without reading the codebase.

# Rules

1. **Never query `raw.*` tables directly in application code.** Always use the `v_bronze_*` views — they extract named fields from the JSONB payload.
2. **Always query `staging.*` for reads.** Staging tables are typed and deduplicated. `asset_computed` is a 1:1 extension of `staging.asset` — join on `asset_id`.
3. **Upsert on `business_key`.** All staging tables have a UNIQUE INDEX on `business_key`. Conflicts are resolved by updating the existing row.
4. **Migrations are managed by Alembic.** Never add, remove, or rename columns without a migration. See `docs/03-engineering/doc-commands.md` for commands.
5. **Never reference a column that doesn't exist in an applied migration.** Run `alembic current` to check. If a column is missing, create the migration first.

# Storage Model

PostgreSQL running in Docker. Three schemas map to three medallion layers:

| Schema | Layer | Purpose |
|---|---|---|
| `raw` | Bronze | Append-only. Stores full broker API payload as JSONB. Partitioned by `ingested_date`. |
| `staging` | Silver | Typed, deduplicated tables. Source of truth for all analytics and dashboard queries. |
| `analytics` | Gold | Aggregated business-ready tables. Not yet fully built — designed dashboard-question-first. |

# Schema Reference

Full column-level detail for all tables and views:

→ [schema-reference.md](./references/schema-reference.md)

Covers:
- `raw.account`, `raw.asset` — the raw partition tables
- `raw.v_bronze_account`, `raw.v_bronze_asset` — the canonical Bronze views (use these, not the raw tables)
- `staging.account`, `staging.asset`, `staging.asset_computed` — the Silver tables
- Business key formulas and deduplication rules

# Migration Quick Reference

```bash
alembic current            # show current revision
alembic upgrade head       # apply all pending migrations
alembic revision -m "msg"  # create a new migration file
alembic downgrade -1       # roll back one migration
```

Full migration workflow: `docs/02-architecture/design/doc-migration.md`
