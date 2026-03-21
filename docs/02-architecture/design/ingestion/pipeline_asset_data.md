---
name: Asset-data-pipeline
description: Documentation on asset data ingestion pipeline
---

# Asset Data Pipeline

## Overview

Pipeline to ingest the Trading 212 Positions API. Each position is one held asset (stock/ETF) in the portfolio. Three pipelines run in sequence per orchestration cycle.

## Flow

```
Bronze → Silver → Computed Silver
```

---

## Bronze Layer

**Class:** `PipelineAssetBronze`
**Source:** Trading 212 Positions API
**Destination:** `PostgresAssetFullLoader` → `raw.asset`

### What It Does

1. Fetches all positions from the Trading 212 API.
2. Validates each record against `AssetAPIRecord` (Pydantic). Raises on structural failure.
3. Inserts the full payload into `raw.asset`, partitioned by `ingested_date`.
4. Drops and recreates `raw.v_bronze_asset` to expose the current day's partition with a computed `business_key`.

### Bronze Tables

| Object | Type | Description |
|--------|------|-------------|
| `raw.asset` | Table (partitioned by date) | Append-only raw payload |
| `raw.asset_YYYY_MM_DD` | Partition | Daily partition |
| `raw.v_bronze_asset` | View | Flattened fields + `business_key` |

### Known Issues

- API can return rate-limit errors when multiple pipelines run concurrently. No retry logic implemented in the bronze pipeline itself — Prefect task retries provide the fallback.

---

## Silver Layer

**Class:** `PipelineAssetSilver`
**Extends:** `BaseSilverPipeline`
**Source:** `raw.v_bronze_asset`
**Destination:** `staging.asset` (upsert on `business_key`)

### What It Does

1. Incremental extract: reads from `v_bronze_asset` rows not yet in `staging.asset`, keyed on `business_key`.
2. Maps fields to `staging.asset` columns, adds `broker = "Trading 212"`.
3. Validates each record through `AssetRecord` (Pydantic). Invalid records are logged and skipped; the batch continues.
4. Upserts valid records to `staging.asset`.

### Silver Tables

| Table | Description |
|-------|-------------|
| `staging.asset` | Typed, deduplicated per-position records |

---

## Computed Silver Layer

**Class:** `PipelineAssetComputedSilver`
**Extends:** `Pipeline` (bare — not `BaseSilverPipeline`)
**Source:** `staging.asset` (SQL window functions)
**Destination:** `staging.asset_computed` (upsert on `asset_id`)

### What It Does

1. Runs a single SQL query against `staging.asset` computing all metrics as window functions (partitioned by `ticker`, ordered by `created_timestamp`).
2. Python transformation handles null-coercion and the 4 derived metrics that can't be expressed purely in SQL.
3. Maps output to `AssetComputed` dataclass (not Pydantic — no validation layer).
4. Upserts to `staging.asset_computed` using `asset_id` as unique key.

### Computed Metrics

| Field | Computed In | Notes |
|-------|-------------|-------|
| `cashflow` | SQL | Aliased from `cost` |
| `daily_return` | SQL | LAG-based % change in value per ticker |
| `cumulative_return` | SQL | `EXP(SUM(LN(1 + daily_return)))` over all rows |
| `dca_bias` | SQL | `(value - cost) / cost` |
| `pct_drawdown` | SQL | `(value - recent_value_high_30d) / recent_value_high_30d` |
| `recent_value_high_30d` | SQL | 30-row rolling MAX(value) per ticker |
| `recent_value_low_30d` | SQL | 30-row rolling MIN(value) per ticker |
| `recent_profit_high_30d` | SQL | 30-row rolling MAX(profit) per ticker |
| `recent_profit_low_30d` | SQL | 30-row rolling MIN(profit) per ticker |
| `value_high` | SQL | All-time MAX(value) per ticker |
| `value_low` | SQL | All-time MIN(value) per ticker |
| `ma_20d` | SQL | 20-row rolling AVG(value) per ticker |
| `ma_30d` | SQL | 30-row rolling AVG(value) per ticker |
| `ma_50d` | SQL | 50-row rolling AVG(value) per ticker |
| `volatility_20d` | SQL | 20-row rolling STDDEV(daily_return) per ticker |
| `volatility_30d` | SQL | 30-row rolling STDDEV(daily_return) per ticker |
| `volatility_50d` | SQL | 50-row rolling STDDEV(daily_return) per ticker |
| `pnl_pct` | Python | `profit / cashflow * 100` |
| `var_95_1d` | Python | `volatility_30d * value * 1.65` |
| `profit_range_30d` | Python | `recent_profit_high_30d - recent_profit_low_30d` |
| `ma_crossover_signal` | Python | `ma_20d - ma_50d` |

### Computed Tables

| Table | Description |
|-------|-------------|
| `staging.asset_computed` | One row per asset position; upserted on each run |

### Known Issues

- No Pydantic validation layer — transformation errors raise and halt the pipeline.
- Source query recomputes all window functions across the full history on every run. No incremental optimisation.
