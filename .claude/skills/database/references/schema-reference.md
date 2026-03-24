---
name: schema-reference
description: This document lists all database tables, views, and columns across all layers of the portfolio data pipeline.
---

# Database Schema Reference

## Architecture Overview

The pipeline has three layers. Each layer has a specific role and should be referenced accordingly:

- `raw` — Partitioned ingestion tables holding the full broker API payload as `jsonb`. Never query directly in application logic. Bronze views (`v_bronze_*`) extract fields from the payload and are the canonical source for staging ingestion.
- `staging` — Materialised, typed tables ready for analytics and AI consumption. Always query staging for reads. `asset_computed` and `account_computed` are 1:1 extensions of their parent tables.
- `analytics` — Aggregated, business-ready Kimball star schema. Use for dashboard queries and reporting.

---

## What to Read

- **Pipeline work (ingestion):** Layer 1 — Raw and Layer 2 — Staging only
- **Dashboard queries:** See `docs/02-architecture/design/schema/schema-analytics.md` for the full gold schema
- **Specific table lookup:** Jump directly to that section by name
- **Migration or upsert question:** Business Keys & Deduplication section

---

## Layer 1 — Raw

> Partitioned by `ingested_date`. Tables are append-only. Do not query raw tables directly — use the `v_bronze_*` views instead.

### `raw.account`

| Column | Type | Nullable | Notes |
| --- | --- | --- | --- |
| `id` | text | YES | Broker-assigned account ID (stored in payload) |
| `payload` | jsonb | NO | Full raw JSON response from broker API |
| `ingested_date` | date | NO | Partition key — date record was ingested |
| `ingested_timestamp` | timestamptz | NO | Exact ingest time, defaults to `now()` |

### `raw.asset`

| Column | Type | Nullable | Notes |
| --- | --- | --- | --- |
| `id` | text | YES | Broker-assigned position/asset ID |
| `payload` | jsonb | NO | Full raw JSON response from broker API |
| `ingested_date` | date | NO | Partition key — date record was ingested |
| `ingested_timestamp` | timestamptz | NO | Exact ingest time, defaults to `now()` |

### `raw.v_bronze_account`

> View over `raw.account`. Extracts and names all fields from the `payload` jsonb column.

| Field | Type | Source | Description |
| --- | --- | --- | --- |
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
| --- | --- | --- | --- |
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
| --- | --- | --- | --- |
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

### `staging.account_computed`

> 1:1 extension of `staging.account`. Join on `account_id = staging.account.id`. Contains portfolio-level computed metrics.

| Field | Type | Constraint | Description |
| --- | --- | --- | --- |
| `account_id` | uuid | UNIQUE, FK → `staging.account.id` | Links to the parent account row |
| `total_return_abs` | double | — | Total absolute return (value - cost) |
| `total_return_pct` | double | — | Total return as a percentage |
| `cash_deployment_ratio` | double | — | `(total_value - cash_available) / total_value` |
| `daily_change_abs` | double | — | Day-over-day absolute change in portfolio value |
| `daily_change_pct` | double | — | Day-over-day percentage change in portfolio value |
| `portfolio_volatility_weighted` | double | — | `Σ(position_weight × volatility_30d)` across all positions |
| `created_timestamp` | timestamptz | `DEFAULT now()` | Row insert time |

### `staging.asset`

| Field | Type | Constraint | Description |
| --- | --- | --- | --- |
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
| `quantity_in_pies` | double | — | Shares held inside pie portfolios |
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
| --- | --- | --- | --- |
| `asset_id` | uuid | UNIQUE, FK → `staging.asset.id` | Links to the parent asset row |
| `cost_basis` | double | — | Total cash invested in this position (renamed from `cashflow` in migration 011) |
| `daily_return` | double | — | Single-day return (price change %) |
| `cumulative_return` | double | — | Total return since position opened |
| `pnl_pct` | double | — | Unrealised P&L as a percentage of cost basis |
| `dca_bias` | double | — | `price / avg_price` — below 1.0 signals a DCA opportunity |
| `pct_drawdown` | double | — | Drawdown from `value_high` as a percentage |
| `recent_value_high_30d` | double | — | Rolling 30-day high of position value |
| `recent_value_low_30d` | double | — | Rolling 30-day low of position value |
| `recent_profit_high_30d` | double | — | Rolling 30-day high of unrealised profit |
| `recent_profit_low_30d` | double | — | Rolling 30-day low of unrealised profit |
| `profit_range_30d` | double | — | `recent_profit_high_30d - recent_profit_low_30d` |
| `value_high` | double | — | All-time high value for this position |
| `value_low` | double | — | All-time low value for this position |
| `ma_20d` | double | — | 20-day moving average of price |
| `ma_30d` | double | — | 30-day moving average of price |
| `ma_50d` | double | — | 50-day moving average of price |
| `volatility_20d` | double | — | 20-day price volatility (std dev) |
| `volatility_30d` | double | — | 30-day price volatility (std dev) |
| `volatility_50d` | double | — | 50-day price volatility (std dev) |
| `var_95_1d` | double | — | Parametric 1-day VaR at 95% confidence: `volatility_30d × value × 1.65` |
| `ma_crossover_signal` | double | — | `ma_20d - ma_50d` — positive = short-term uptrend |
| `position_weight_pct` | double | — | Position value as % of total portfolio value |
| `created_timestamp` | timestamptz | `DEFAULT now()` | Row insert time |

### SCD Tables — Tagging & Classification

> Slowly-changing dimension tables (Type 2). All use `is_current` + `from_timestamp` / `to_timestamp` to track history. Primary key is `(id, from_timestamp)`.

#### `staging.industry`

| Field | Type | Constraint | Description |
| --- | --- | --- | --- |
| `id` | uuid | PK (composite with `from_timestamp`) | Surrogate key |
| `industry_id` | uuid | — | Business identifier for the industry |
| `name` | text | — | Industry name |
| `description` | text | — | Industry description |
| `is_current` | boolean | — | `true` for the active row |
| `from_timestamp` | timestamptz | PK (composite with `id`) | When this version became active |
| `to_timestamp` | timestamptz | — | When this version was superseded (`NULL` if current) |

#### `staging.sector`

| Field | Type | Constraint | Description |
| --- | --- | --- | --- |
| `id` | uuid | PK (composite with `from_timestamp`) | Surrogate key |
| `sector_id` | uuid | — | Business identifier for the sector |
| `industry_id` | uuid | FK → `staging.industry` | Parent industry |
| `name` | text | — | Sector name |
| `description` | text | — | Sector description |
| `is_current` | boolean | — | `true` for the active row |
| `from_timestamp` | timestamptz | PK (composite with `id`) | When this version became active |
| `to_timestamp` | timestamptz | — | When this version was superseded (`NULL` if current) |

#### `staging.category`

| Field | Type | Constraint | Description |
| --- | --- | --- | --- |
| `id` | uuid | PK (composite with `from_timestamp`) | Surrogate key |
| `category_id` | uuid | — | Business identifier for the category |
| `name` | text | — | Category name |
| `description` | text | — | Category description |
| `is_current` | boolean | — | `true` for the active row |
| `from_timestamp` | timestamptz | PK (composite with `id`) | When this version became active |
| `to_timestamp` | timestamptz | — | When this version was superseded (`NULL` if current) |

#### `staging.tag`

| Field | Type | Constraint | Description |
| --- | --- | --- | --- |
| `id` | uuid | PK (composite with `from_timestamp`) | Surrogate key |
| `tag_id` | uuid | — | Business identifier for the tag |
| `name` | text | — | Tag name |
| `description` | text | — | Tag description |
| `category_id` | uuid | FK → `staging.category` | Parent category |
| `is_current` | boolean | — | `true` for the active row |
| `from_timestamp` | timestamptz | PK (composite with `id`) | When this version became active |
| `to_timestamp` | timestamptz | — | When this version was superseded (`NULL` if current) |

#### `staging.asset_tag`

> Junction table. Links assets to their tags. Also SCD Type 2 — tracks when a tag was assigned and removed.

| Field | Type | Constraint | Description |
| --- | --- | --- | --- |
| `id` | uuid | PK (composite with `from_timestamp`) | Surrogate key |
| `asset_id` | uuid | FK → `staging.asset.id` | The tagged asset |
| `tag_id` | uuid | FK → `staging.tag` | The assigned tag |
| `is_current` | boolean | — | `true` if the tag is currently assigned |
| `from_timestamp` | timestamptz | PK (composite with `id`) | When the tag was assigned |
| `to_timestamp` | timestamptz | — | When the tag was removed (`NULL` if still assigned) |

---

## Layer 3 — Gold (Analytics)

> Full gold schema (dimensions + facts) is documented in `docs/02-architecture/design/schema/schema-analytics.md`. That file is the authoritative source — do not duplicate it here.

---

## Business Keys & Deduplication

UNIQUE INDEX enforced on `business_key` in all staging tables. Upsert on conflict using `business_key`.

| Table | Formula |
| --- | --- |
| `staging.account` | `external_id \|\| '_' \|\| currency \|\| '_' \|\| data_timestamp` |
| `staging.asset` | `external_id \|\| '_' \|\| ticker \|\| '_' \|\| data_timestamp` |

---

## Dashboard Tab Mapping

| Tab | Primary tables |
| --- | --- |
| Portfolio | `fact_portfolio_daily`, `fact_valuation` |
| Valuation | `fact_price`, `fact_return`, `fact_signal` |
| Risk | `fact_technical`, `fact_valuation` (`position_weight_pct`) |
| Opportunities | `fact_signal`, `fact_technical` (`pct_drawdown`, `volatility_*`) |
