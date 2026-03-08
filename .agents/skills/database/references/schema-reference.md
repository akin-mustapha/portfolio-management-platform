---
name: schema-reference
description: This document lists all database tables, views, and columns across all layers of the portfolio data pipeline.
---

# Database Schema Reference

## Architecture Overview

The pipeline has three layers. Each layer has a specific role and should be referenced accordingly:

- `raw` — Partitioned ingestion tables holding the full broker API payload as `jsonb`. Never query directly in application logic. Bronze views (`v_bronze_*`) extract fields from the payload and are the canonical source for staging ingestion.
- `staging` — Materialised, typed tables ready for analytics and AI consumption. Always query staging for reads. `asset_computed` is a 1:1 extension of `staging.asset`.
- `gold` — Aggregated, business-ready tables built on top of staging. Use for dashboard queries and reporting.

---

## Layer 1 — Raw

> Partitioned by `ingested_date`. Tables are append-only. Do not query raw tables directly — use the `v_bronze_*` views instead.

### `raw.account`

| Column | Type | Nullable | Notes |
|---|---|---|---|
| `id` | text | YES | Broker-assigned account ID (stored in payload) |
| `payload` | jsonb | NO | Full raw JSON response from broker API |
| `ingested_date` | date | NO | Partition key — date record was ingested |
| `ingested_timestamp` | timestamptz | NO | Exact ingest time, defaults to `now()` |

### `raw.asset`

| Column | Type | Nullable | Notes |
|---|---|---|---|
| `id` | text | YES | Broker-assigned position/asset ID |
| `payload` | jsonb | NO | Full raw JSON response from broker API |
| `ingested_date` | date | NO | Partition key — date record was ingested |
| `ingested_timestamp` | timestamptz | NO | Exact ingest time, defaults to `now()` |

### `raw.v_bronze_account`

> View over `raw.account`. Extracts and names all fields from the `payload` jsonb column.

| Field | Type | Source | Description |
|---|---|---|---|
| `external_id` | text | `payload->>'id'` | Broker-assigned account identifier |
| `cash_in_pies` | text | `payload->'cash'->>'inPies'` | Cash allocated inside pie portfolios |
| `cash_available_to_trade` | text | `payload->'cash'->>'availableToTrade'` | Free cash ready for trading |
| `cash_reserved_for_orders` | text | `payload->'cash'->>'reservedForOrders'` | Cash locked for pending orders |
| `currency` | text | `payload->>'currency'` | Account base currency |
| `total_value` | text | `payload->>'totalValue'` | Total portfolio value in base currency |
| `investments_total_cost` | text | `payload->'investments'->>'totalCost'` | Total cost basis of all investments |
| `investments_realized_pnl` | text | `payload->'investments'->>'realizedProfitLoss'` | Realised profit/loss to date |
| `investments_unrealized_pnl` | text | `payload->'investments'->>'unrealizedProfitLoss'` | Open unrealised profit/loss |
| `ingested_date` | date | `raw.ingested_date` | Partition date carried forward |
| `ingested_timestamp` | timestamptz | `raw.ingested_timestamp` | Ingest timestamp carried forward |
| `business_key` | text | derived | `external_id \|\| '_' \|\| currency \|\| '_' \|\| ingested_timestamp` |

### `raw.v_bronze_asset`

> View over `raw.asset`. Extracts and names all fields from the `payload` jsonb column.

| Field | Type | Source | Description |
|---|---|---|---|
| `ticker` | text | `instrument->>'ticker'` | Exchange ticker symbol |
| `instrument_name` | text | `instrument->>'name'` | Full instrument name |
| `isin` | text | `instrument->>'isin'` | ISIN identifier |
| `instrument_currency` | text | `instrument->>'currency'` | Currency of the instrument |
| `created_at` | timestamp | `payload->>'createdAt'` | Position creation timestamp |
| `quantity` | numeric | `payload->>'quantity'` | Total shares/units held |
| `quantity_available` | numeric | `payload->>'quantityAvailableForTrading'` | Shares available to sell |
| `quantity_in_pies` | numeric | `payload->>'quantityInPies'` | Shares held inside pies |
| `current_price` | numeric | `payload->>'currentPrice'` | Latest market price |
| `average_price_paid` | numeric | `payload->>'averagePricePaid'` | DCA average cost per share |
| `wallet_currency` | text | `walletImpact->>'currency'` | Wallet/account currency |
| `total_cost` | numeric | `walletImpact->>'totalCost'` | Total cost in wallet currency |
| `current_value` | numeric | `walletImpact->>'currentValue'` | Current market value in wallet currency |
| `unrealized_pnl` | numeric | `walletImpact->>'unrealizedProfitLoss'` | Open P&L in wallet currency |
| `fx_impact` | numeric | `walletImpact->>'fxImpact'` | FX rate impact on returns |
| `external_id` | text | `asset.id` | Broker-assigned position ID |
| `ingested_date` | date | `raw.ingested_date` | Partition date carried forward |
| `ingested_timestamp` | timestamptz | `raw.ingested_timestamp` | Ingest timestamp carried forward |
| `business_key` | text | derived | `external_id \|\| '_' \|\| ticker \|\| '_' \|\| ingested_timestamp` |

---

## Layer 2 — Staging

> Typed, deduplicated tables. Use these for all analytics, AI tools, and dashboard queries.

### `staging.account`

| Field | Type | Constraint | Description |
|---|---|---|---|
| `id` | uuid | PK, `gen_random_uuid()` | Surrogate primary key |
| `data_timestamp` | timestamptz | NOT NULL | Timestamp of the source data snapshot |
| `external_id` | text | NOT NULL | Broker account identifier |
| `cash_in_pies` | double | — | Cash inside pie portfolios |
| `cash_available_to_trade` | double | — | Tradeable cash balance |
| `cash_reserved_for_orders` | double | — | Cash held for pending orders |
| `broker` | text | — | Broker identifier |
| `currency` | text | — | Account base currency |
| `total_value` | double | — | Total portfolio value |
| `investments_total_cost` | double | — | Total cost basis |
| `investments_realized_pnl` | double | — | Realised P&L |
| `investments_unrealized_pnl` | double | — | Unrealised P&L |
| `business_key` | text | UNIQUE, NOT NULL | Natural dedup key |
| `created_timestamp` | timestamptz | `DEFAULT now()` | Row insert time |
| `updated_timestamp` | timestamptz | — | Last update time |

### `staging.asset`

| Field | Type | Constraint | Description |
|---|---|---|---|
| `id` | uuid | PK, `gen_random_uuid()` | Surrogate primary key |
| `data_timestamp` | timestamptz | NOT NULL | Timestamp of the source data snapshot |
| `external_id` | text | — | Broker position ID |
| `ticker` | text | — | Ticker symbol |
| `name` | text | NOT NULL | Instrument display name |
| `description` | text | — | Additional instrument description |
| `broker` | text | — | Broker identifier |
| `currency` | text | — | Instrument currency |
| `local_currency` | text | — | Wallet/account currency |
| `share` | double | — | Shares/units held |
| `price` | double | — | Current market price |
| `avg_price` | double | — | DCA average cost per share |
| `value` | double | — | Current market value |
| `cost` | double | — | Total cost basis |
| `profit` | double | — | Unrealised P&L |
| `fx_impact` | double | — | FX impact on returns |
| `business_key` | text | UNIQUE, NOT NULL | Natural dedup key |
| `created_timestamp` | timestamptz | `DEFAULT now()` | Row insert time |
| `updated_timestamp` | timestamptz | — | Last update time |

### `staging.asset_computed`

> 1:1 extension of `staging.asset`. Join on `asset_id = staging.asset.id`. Contains all calculated metrics.

| Field | Type | Constraint | Description |
|---|---|---|---|
| `asset_id` | uuid | FK → `staging.asset.id` | Links to the parent asset row |
| `cashflow` | double | — | Net cashflow for the position |
| `daily_return` | double | — | Single-day return (price change %) |
| `cumulative_return` | double | — | Total return since position opened |
| `dca_bias` | double | — | DCA signal: current price vs `avg_price` ratio |
| `pct_drawdown` | double | — | Drawdown from `value_high` as a percentage |
| `recent_value_high_30d` | double | — | Rolling 30-day high of position value |
| `recent_value_low_30d` | double | — | Rolling 30-day low of position value |
| `recent_profit_high_30d` | double | — | Rolling 30-day high of profit |
| `recent_profit_low_30d` | double | — | Rolling 30-day low of profit |
| `value_high` | double | — | All-time high value for this position |
| `value_low` | double | — | All-time low value for this position |
| `ma_20d` | double | — | 20-day moving average of price |
| `ma_30d` | double | — | 30-day moving average of price |
| `ma_50d` | double | — | 50-day moving average of price |
| `volatility_20d` | double | — | 20-day price volatility (std dev) |
| `volatility_30d` | double | — | 30-day price volatility (std dev) |
| `volatility_50d` | double | — | 50-day price volatility (std dev) |
| `created_timestamp` | timestamptz | `DEFAULT now()` | Row insert time |

---

## Layer 3 — Gold

> Aggregated, business-ready views and tables built on top of staging. Use for dashboard queries and reporting.

*Tables to be defined.*

---

## Business Keys & Deduplication

UNIQUE INDEX enforced on `business_key` in all staging tables. Upsert on conflict using `business_key`.

| Table | Formula |
|---|---|
| `staging.account` | `external_id \|\| '_' \|\| currency \|\| '_' \|\| data_timestamp` |
| `staging.asset` | `external_id \|\| '_' \|\| ticker \|\| '_' \|\| data_timestamp` |