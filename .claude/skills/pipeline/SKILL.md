---
name: pipeline
description: Use this skill when building, debugging, or modifying data pipelines in the ingestion layer.
---

# Why

This provides the context needed to work on pipelines correctly. Pipelines are the most common source of subtle bugs in this project — wrong file modified, unapplied migration columns referenced, upsert bugs that silently insert only 1 row.

# Rules (enforce before touching any code)

1. **Read the target pipeline file first.** Never modify a pipeline without reading it. The silver and computed-silver pipelines look similar but have different logic.
2. **Never reference a column from an unapplied migration.** If a new column is needed, confirm the migration has been applied (`alembic current`) before writing code that reads or writes it.
3. **Upserts must be verified.** The most common upsert bug is an early return that inserts only 1 row. After implementing an upsert, trace the loop and confirm it iterates over all records.
4. **Confirm the correct file before editing.** There are pairs of similarly named files (e.g. account vs asset, silver vs computed-silver). State the filename you are editing before making changes.
5. **One layer per task.** Pipeline changes stay in `src/backend/ingestion/`. Do not mix with dashboard or service changes.

# Pipeline Pattern — Source / Transformation / Destination

Every pipeline follows this structure:

```python
class MySource(Source):
    def extract(self) -> List[Dict]:
        # reads from previous layer (e.g. raw.v_bronze_asset)

class MyTransformation(Transformation):
    def transform(self, records) -> List[MySchema]:
        # validates with Pydantic, computes derived fields

class MyDestination(Destination):
    def load(self, records) -> None:
        # upserts into target table (staging.* or analytics.*)

class MyPipeline(BaseSilverPipeline):  # or BaseGoldPipeline
    def run(self):
        records = self.source.extract()
        transformed = self.transformation.transform(records)
        self.destination.load(transformed)
```

Each component is a separate class implementing its protocol. The `Pipeline.run()` wires them together. Never put business logic inside `run()`.

# Pipeline Inventory

| File | Layer | Source → Destination |
|---|---|---|
| `pipeline_asset_bronze.py` | Bronze | Trading212 API → `raw.asset` |
| `pipeline_account_bronze.py` | Bronze | Trading212 API → `raw.account` |
| `pipeline_asset_silver.py` | Silver | `raw.v_bronze_asset` → `staging.asset` |
| `pipeline_account_silver.py` | Silver | `raw.v_bronze_account` → `staging.account` |
| `pipeline_asset_computed_silver.py` | Silver (computed) | `staging.asset` → `staging.asset_computed` |
| `pipeline_account_computed_silver.py` | Silver (computed) | `staging.account` → `staging.account_computed` |
| `pipeline_asset_gold.py` | Gold (in progress) | `staging.*` → `analytics.*` |
| `pipeline_account_gold.py` | Gold (in progress) | `staging.*` → `analytics.*` |
| `pipeline_asset_portfolio.py` | Portfolio enrichment | cross-layer |

# Common Failure Modes

**JSONB mismatch** — A Python dict is being inserted into a column that expects a scalar, or vice versa. Check the Pydantic schema field type and the DB column type.

**FK violation** — A record references a parent row that doesn't exist yet. Check insertion order — parent tables must be populated before child tables.

**Upsert inserts only 1 row** — Usually an early `return` inside a loop, or `executemany` called with a single-item list by mistake. Read the `load()` method carefully.

**Column does not exist** — Almost always a migration that was written but not applied. Run `alembic current` and `alembic upgrade head`.

**Import fails in Prefect but works locally** — Prefect workers resolve Python paths differently. Use absolute imports from the package root, not relative imports.

# Validation

Pydantic schemas live in `src/backend/ingestion/domain/schemas/`. Each pipeline layer has its own schema:
- Bronze: minimal, stores raw API response fields
- Silver: typed, required fields validated, computed fields added
- Gold: shaped for dashboard queries

# Docs Reference

Full pipeline design: `docs/02-architecture/design/ingestion/doc-pipelines.md`
Schema reference: use `/database` skill
