---
name: Asset-data-pipeline
description: Documentation on asset data ingestion pipeline
---

# Asset Data Pipeline

## Overview

Pipeline to ingest the Trading 212 Positions API. Each position is one held asset (stock/ETF) in the portfolio. Two pipelines run in sequence per orchestration cycle.

> **Note:** Bronze and Silver are unified pipelines — `PipelineT212Bronze` and `PipelineT212Silver` handle both asset and account data in a single run. There are no separate asset-only pipeline classes.

## Flow

```
Bronze → Silver → Gold
```

Metrics (moving averages, rolling volatility, LAG-based returns, drawdown) are computed in the Gold layer via SQL window functions inside `PipelineT212Gold`. There is no Computed Silver stage for assets.

---

## Bronze Layer

**Class:** `PipelineT212Bronze`
**File:** `vault/pipeline/etl/runners/pipeline_bronze_t212.py`
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

**Class:** `PipelineT212Silver`
**File:** `vault/pipeline/etl/runners/pipeline_silver_t212.py`
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

## Gold Layer

**Class:** `PipelineT212Gold`
**File:** `vault/pipeline/etl/runners/pipeline_gold_t212.py`

All computed metrics for assets are produced here via SQL window functions. See `doc-pipelines.md` for the full Gold pattern and `schema-analytics.md` for the fact table schema.
