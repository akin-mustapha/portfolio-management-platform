# FRED Ingestion Pipeline

## Context

The gold layer computes Sharpe Ratio (needs risk-free rate) and Beta (needs a market benchmark). Both require external macro data that Trading212 does not provide. The FRED API (Federal Reserve Bank of St. Louis) supplies two daily series: `DTB3` (3-Month T-Bill rate) and `SP500` (S&P 500 index). This pipeline ingests those series into the medallion stack so the gold layer can join against them in a future task.

**Scope:** Bronze + Silver layers only. Gold layer integration (joining FRED data into Sharpe/Beta computation) is a separate task per the one-layer-per-branch rule.

---

## API Endpoints

Single endpoint, two series:

```
GET https://api.stlouisfed.org/fred/series/observations
  ?series_id=DTB3          # or SP500
  &observation_start=YYYY-MM-DD
  &file_type=json
  &api_key=<FREED_API_KEY>
```

Response: `{ "observations": [{"date": "YYYY-MM-DD", "value": "4.5"}, ...] }`

Missing values return `"."` — filtered at the SQL layer in the silver source query.

Env var: `FREED_API_KEY` (already in `.env.example`)

---

## Trigger and Frequency

- **Schedule**: Daily at `07:30 UTC` (`interval: 86400`, `anchor_date: "2026-01-01T07:30:00Z"`)
- **Why daily**: FRED publishes within 1 business day of the reference date. Hourly would be wasteful.
- **Why 07:30 UTC**: After the existing `rebalance_plan` anchor (07:00 UTC), avoiding same-slot worker contention.

---

## New Tables

### `raw.fred_observations` — Bronze, JSONB, date-partitioned

```sql
CREATE TABLE raw.fred_observations (
    id                  TEXT NOT NULL,
    series_id           VARCHAR(20) NOT NULL,   -- 'DTB3' | 'SP500'
    ingested_date       DATE NOT NULL,
    ingested_timestamp  TIMESTAMPTZ DEFAULT now(),
    observation_start   DATE NOT NULL,
    observations        JSONB NOT NULL,         -- raw [{date, value}, ...]
    processed_at        TIMESTAMPTZ
) PARTITION BY RANGE (ingested_date);
```

One row per series per daily run. The full FRED response is stored as JSONB to keep the bronze layer schema-agnostic.

### `staging.fred_observation` — Silver, normalized

```sql
CREATE TABLE staging.fred_observation (
    id                UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    series_id         VARCHAR(20) NOT NULL,
    observation_date  DATE NOT NULL,
    value             NUMERIC(18, 6) NOT NULL,
    business_key      TEXT UNIQUE NOT NULL,    -- '{series_id}_{observation_date}'
    ingested_date     DATE,
    created_timestamp TIMESTAMPTZ DEFAULT now(),
    updated_timestamp TIMESTAMPTZ DEFAULT now()
);
```

Business key: `f"{series_id}_{observation_date}"` (e.g. `"DTB3_2026-04-03"`). The `UNIQUE` constraint enables idempotent upserts.

---

## Files

### Migrations

| File | Description |
|------|-------------|
| `migrations/postgres/versions/raw/004_raw_fred_observations.py` | revision `1100000000a4` revises `a3` |
| `migrations/postgres/versions/staging/013_staging_fred_observation.py` | revision `2200000000b13` revises `b12` |

### Pipeline Source Files

| File | Contents |
|------|----------|
| `src/pipelines/infrastructure/api/api_client_fred.py` | `FredAPIClient` — sync httpx, `get_observations(series_id, observation_start)` |
| `src/pipelines/domain/schemas/bronze/fred_api.py` | `FredObservationItem`, `FredObservationsResponse` (Pydantic) |
| `src/pipelines/domain/schemas/silver/fred_observation.py` | `FredObservationRecord` (Pydantic, `value: Decimal`) |
| `src/pipelines/infrastructure/queries/silver/fred_silver_source.sql` | Unwinds JSONB, filters `"."` values |
| `src/pipelines/application/runners/loaders/loader_bronze_fred.py` | `FullLoaderPostgresFred(FullLoader)` |
| `src/pipelines/application/runners/pipeline_bronze_fred.py` | `FredBronzeSource`, `FredBronzeDestination`, `PipelineFredBronze` |
| `src/pipelines/application/runners/pipeline_silver_fred.py` | `FredSilverSource`, `FredObservationTransformation`, `FredObservationDestination`, `PipelineFredSilver` |
| `src/orchestration/prefect/flow_fred.py` | `task_fred_bronze`, `task_fred_silver`, `flow_fred` |

### Modified Files

| File | Change |
|------|--------|
| `src/pipelines/factories/pipeline_factory.py` | Add `fred_bronze` and `fred_silver` entries |
| `prefect.yaml` | Add `fred_daily` deployment block |

---

## Key Design Decisions

**Single bronze source fetches both series** — `FredBronzeSource.extract()` makes two sequential HTTP requests (DTB3 + SP500) and returns a list of two dicts. No separate pipelines per series.

**Incremental watermark from `staging.fred_observation`** — the bronze source queries `MAX(observation_date) WHERE series_id = :id` before each call. First run defaults to a 30-day lookback; subsequent runs use `max_date - 1 day` (one-day overlap to catch FRED revisions). The silver upsert's `ON CONFLICT (business_key) DO UPDATE` handles revised values cleanly.

**JSONB stored in raw, unwound in SQL** — bronze stays schema-agnostic per medallion convention. The silver source query uses `jsonb_array_elements()` to unwind, filtering `"."` values at the SQL layer.

**`processed_at` marking inside `PipelineFredSilver.run()`** — silver overrides `run()` to call `super().run()` then `UPDATE raw.fred_observations SET processed_at = now() WHERE processed_at IS NULL`.

**`RepositoryFactory` needs no changes** — it is dynamic; `RepositoryFactory.get("fred_observation", schema_name="staging")` works as-is.

---

## Verification

1. Apply both migrations: `alembic -c migrations/postgres/alembic.ini upgrade head`
2. Run bronze: `PipelineFactory.get("fred_bronze").run()` → check `raw.fred_observations` has rows for `DTB3` and `SP500`
3. Run silver: `PipelineFactory.get("fred_silver").run()` → check `staging.fred_observation` has scalar rows with numeric values
4. Confirm `processed_at` is set on raw rows after silver runs
5. Re-run silver → zero new rows (idempotency via `business_key` upsert)
6. Deploy: `prefect deploy --name fred_daily` → confirm daily schedule in Prefect UI
