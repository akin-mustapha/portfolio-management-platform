---
name: Account-data-pipeline
description: Documentation on account data ingestion pipeline
---

# Account Data Pipeline

## Overview

Pipeline to ingest the Trading 212 Account Summary API (`equity/account/summary`). The account represents the overall portfolio state — cash, investments, and unrealized/realized P&L — as a single record per run.

## Flow

```
Bronze → Silver → Computed Silver
```

Orchestrated as a Prefect flow (`flow_t212_account`) with sequential task execution. Each stage retries up to 2 times with a 60-second delay on failure.

---

## Bronze Layer

**Class:** `PipelineAccountBronze`
**Source:** `Trading212AccountSource` — calls `equity/account/summary` endpoint
**Destination:** `Trading212AccountDestination` → `PostgresAccountFullLoader` → `raw.account`

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

**Class:** `PipelineAccountSilver`
**Extends:** `BaseSilverPipeline`
**Source:** `Trading212AccountSourceSilver` — queries `raw.v_bronze_account`
**Destination:** `Trading212AccountDestination` → `staging.account` (upsert on `business_key`)

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

## Computed Silver Layer

**Class:** `PipelineAccountComputedSilver`
**Extends:** `Pipeline` (bare — not `BaseSilverPipeline`)
**Source:** `Trading212AccountComputedSourceSilver` — queries `staging.account`
**Destination:** `Trading212AccountComputedDestination` → `staging.account_computed` (upsert on `account_id`)

### What It Does

1. Extracts all rows from `staging.account`, including `LAG(total_value) OVER (ORDER BY data_timestamp)` to compute day-over-day change.
2. Computes 5 metrics per account row (see table below). Nulls are treated as 0 to avoid division errors.
3. Maps output to `AccountComputed` dataclass (not Pydantic — no validation layer).
4. Upserts to `staging.account_computed` using `account_id` as the unique key.

### Computed Metrics

| Field | Formula |
|-------|---------|
| `total_return_abs` | `unrealized_pnl + realized_pnl` |
| `total_return_pct` | `total_return_abs / investments_total_cost * 100` |
| `cash_deployment_ratio` | `(total_value - cash_available_to_trade) / total_value * 100` |
| `daily_change_abs` | `total_value - prev_total_value` |
| `daily_change_pct` | `daily_change_abs / prev_total_value * 100` |

All metrics default to `0` when divisor is zero or source value is null.

### Computed Tables

| Table | Description |
|-------|-------------|
| `staging.account_computed` | One row per account; upserted on each run |

---

## Known Issues

- `v_bronze_account` is dropped and recreated on every bronze run, so it always reflects the current day's partition only. Historical rows are preserved in the partitioned table and accessible via direct query.
- `PipelineAccountComputedSilver` has no Pydantic validation layer — transformation errors raise and halt the pipeline.
