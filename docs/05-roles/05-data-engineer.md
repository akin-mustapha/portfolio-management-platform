# Role: Data Engineer

**Who** — You build and maintain the pipelines that move data from Trading212 through bronze → silver → gold. Your job is reliable, correct data flow — not features.

**What**
- Design and implement ingestion pipelines (Source / Transformation / Destination pattern)
- Maintain data quality across the three medallion layers
- Write Pydantic validation schemas for incoming data
- Handle schema drift and API contract changes from Trading212

**When**
- Adding a new data source or endpoint
- A pipeline fails or produces incorrect output
- The gold layer is stale or missing data
- A new metric requires a new column in silver or gold

**Where**
- `src/pipelines/` — pipeline implementations
- `src/pipelines/domain/schemas/` — Pydantic schemas
- `raw`, `staging`, `analytics` schemas in Postgres
- `docs/02-architecture/design/ingestion/doc-pipelines.md` — pipeline contract

**Why** — If this hat is neglected, the gold layer drifts from source truth. Dashboard metrics become stale or silently wrong. Downstream services trust bad data.

**How**
- Always read `doc-pipelines.md` before building anything new
- Follow the Source / Transformation / Destination class structure
- Append-only to `raw`, deduplicate in `staging`, aggregate in `analytics`
- Test pipeline output against known fixture data

## Checklist
- [ ] Pipeline runs end-to-end without errors
- [ ] Bronze data is raw and unmodified from source
- [ ] Silver data is typed, deduplicated, and validated by Pydantic
- [ ] Gold data answers the specific dashboard question it was built for
- [ ] New pipeline or schema change has a corresponding Alembic migration
