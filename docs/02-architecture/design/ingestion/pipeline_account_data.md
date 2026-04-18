---
name: Account-data-pipeline
description: Documentation on account data ingestion pipeline
---

# Account Data Pipeline

## Overview

Pipeline to ingest the Trading 212 Account Summary API (`equity/account/summary`). The account represents the overall portfolio state — cash, investments, and unrealized/realized P&L — as a single record per run.

> **Note:** Bronze and Silver are unified pipelines — `PipelineT212Bronze` and `PipelineT212Silver` handle both asset and account data in a single run. There are no separate account-only pipeline classes.

## Flow

```
Bronze → Silver → Gold
```

Orchestrated as a Prefect flow with sequential task execution. Each stage retries up to 2 times with a 60-second delay on failure. Account-level metrics (daily change, total return) are computed in the Gold layer via SQL — there is no Computed Silver stage.

---

## Bronze Layer

**Class:** `PipelineT212Bronze`
**File:** `src/pipelines/application/runners/pipeline_bronze_t212.py`
**Source:** `Trading212AccountSource` — calls `equity/account/summary` endpoint
**Destination:** `PostgresAccountFullLoader` → `raw.account`

### What It Does

1. Fetches the account summary JSON from the Trading 212 API.
2. Validates the response structure against `AccountAPIResponse` (Pydantic). Raises if invalid.
3. Inserts the full JSON payload as a single row into `raw.account`, partitioned by `ingested_date`.
4. Drops and recreates the view `raw.v_bronze_account` to expose the current day's partition with parsed fields and a `business_key`.

### Bronze Tables

| Object | Type | Description |
|--------|------|-------------|
| `raw.account` | Table (partitioned by date) | Append-only raw JSON payload |
| `raw.account_YYYY_MM_DD` | Partition | Daily partition |
| `raw.v_bronze_account` | View | Flattened fields + `business_key` |

### `v_bronze_account` — Exposed Fields

| Field | Source JSON Path |
|-------|-----------------|
| `external_id` | `payload->>'id'` |
| `cash_in_pies` | `payload->'cash'->>'inPies'` |
| `cash_available_to_trade` | `payload->'cash'->>'availableToTrade'` |
| `cash_reserved_for_orders` | `payload->'cash'->>'reservedForOrders'` |
| `currency` | `payload->>'currency'` |
| `total_value` | `payload->'totalValue'` |
| `investments_total_cost` | `payload->'investments'->>'totalCost'` |
| `investments_realized_pnl` | `payload->'investments'->>'realizedProfitLoss'` |
| `investments_unrealized_pnl` | `payload->'investments'->>'unrealizedProfitLoss'` |
| `ingested_date` | From `raw.account` |
| `ingested_timestamp` | From `raw.account` |
| `business_key` | `external_id || '_' || currency || '_' || ingested_timestamp` |

---

## Silver Layer

**Class:** `PipelineT212Silver`
**File:** `src/pipelines/application/runners/pipeline_silver_t212.py`
**Extends:** `BaseSilverPipeline`
**Source:** `Trading212AccountSourceSilver` — queries `raw.v_bronze_account`
**Destination:** `staging.account` (upsert on `business_key`)

### What It Does

1. Extracts rows from `raw.v_bronze_account` that do not yet exist in `staging.account` (incremental, keyed on `business_key`). Skips rows with null `external_id`.
2. Transforms: maps fields to `staging.account` columns, adds `broker = "Trading 212"` and `updated_timestamp`.
3. Validates each record through `AccountRecord` (Pydantic). Invalid records are logged and skipped; the batch continues.
4. Upserts valid records to `staging.account` using `business_key` as the unique key.

### Silver Tables

| Table | Description |
|-------|-------------|
| `staging.account` | Typed, deduplicated account records |

### `staging.account` — Fields Written

| Field | Notes |
|-------|-------|
| `external_id` | Account ID from Trading 212 |
| `broker` | Hardcoded `"Trading 212"` |
| `currency` | Account currency |
| `total_value` | Total portfolio value |
| `cash_in_pies` | Cash allocated to pies |
| `cash_available_to_trade` | Free cash |
| `cash_reserved_for_orders` | Cash held for pending orders |
| `investments_total_cost` | Total invested cost basis |
| `investments_realized_pnl` | Realized profit/loss |
| `investments_unrealized_pnl` | Unrealized profit/loss |
| `data_timestamp` | Sourced from `ingested_timestamp` — used for ordering |
| `updated_timestamp` | Set at pipeline run time |
| `business_key` | Unique key for upsert |

---

## Gold Layer

**Class:** `PipelineT212Gold`
**File:** `src/pipelines/application/runners/pipeline_gold_t212.py`

Account-level facts (`fact_portfolio_daily`) are computed and written here. The gold pipeline reads directly from `staging.account` — it does not depend on any computed silver table. See `doc-pipelines.md` for the Gold pattern and `schema-analytics.md` for the fact table schema.

---

## Known Issues

- `v_bronze_account` is dropped and recreated on every bronze run, so it always reflects the current day's partition only. Historical rows are preserved in the partitioned table and accessible via direct query.
