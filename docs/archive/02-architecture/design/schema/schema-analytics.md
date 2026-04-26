---
name: schema
description: Gold layer schema documentation for the analytics database
---

# Schema

Gold layer data are stored on a Postgres database.

**schema**: `analytics`

---

## Dimensions

**dim_date:**
```yaml
dim_date:
  columns:
    - id::integer           # YYYYMMDD (e.g. 20260320) — human-readable, fast joins
    - date::date
    - year::integer
    - quarter::integer
    - month::integer
    - month_name::varchar
    - day_of_month::integer
    - day_of_week::integer
    - day_name::varchar
    - is_weekend::boolean
    - is_month_start::boolean
    - is_month_end::boolean
    - is_year_start::boolean
    - is_year_end::boolean
    - created_timestamp::timestamptz
    - updated_timestamp::timestamptz
```

> Populated from 2000-01-01 to 2035-12-31 by migration 006. Reference a date by its YYYYMMDD integer, e.g. `WHERE date_id = 20260320`.

**dim_asset:**
```yaml
dim_asset:
  columns:
    - id::uuid (auto generated)
    - asset_id::uuid
    - ticker::varchar
    - name::varchar
    - asset_type::varchar
    - exchange::varchar
    - currency::varchar
    - created_timestamp::timestamptz
    - updated_timestamp::timestamptz
```

**dim_asset_type:**
```yaml
dim_asset_type:
  columns:
    - id::uuid (auto generated)
    - asset_type_id::varchar
    - name::varchar
    - description::varchar
    - created_timestamp::timestamptz
    - updated_timestamp::timestamptz
```

**dim_industry:**
```yaml
dim_industry:
  columns:
    - id::uuid (auto generated)
    - industry_id::varchar
    - name::varchar
    - description::varchar
    - created_timestamp::timestamptz
    - updated_timestamp::timestamptz
```

**dim_portfolio:**
```yaml
dim_portfolio:
  columns:
    - id::uuid (auto generated)
    - portfolio_id::varchar
    - name::varchar
    - base_currency::varchar
    - created_timestamp::timestamptz
    - updated_timestamp::timestamptz
```

**dim_sector:**
```yaml
dim_sector:
  columns:
    - id::uuid (auto generated)
    - sector_id::varchar
    - industry_id::uuid  # FK: dim_industry
    - name::varchar
    - description::varchar
    - created_timestamp::timestamptz
    - updated_timestamp::timestamptz
```

**dim_tag:**
```yaml
dim_tag:
  columns:
    - id::uuid (auto generated)
    - tag_id::varchar
    - name::varchar
    - description::varchar
    - created_timestamp::timestamptz
    - updated_timestamp::timestamptz
```

> `dim_time` was removed — pipeline is daily snapshots, sub-daily granularity has no use case.

---

## Facts

### FK conventions
All position-level fact tables share the same FK pattern:

| Column | Type | Nullable | References |
|---|---|---|---|
| `date_id` | INTEGER | NOT NULL | `dim_date.id` (YYYYMMDD) |
| `asset_id` | UUID | NOT NULL | `dim_asset.asset_id` |
| `portfolio_id` | UUID | NOT NULL | `dim_portfolio.id` |
| `sector_id` | UUID | **NULL** | `dim_sector.id` — nullable, external data not always available |
| `tag_id` | UUID | **NULL** | `dim_tag.id` — nullable, manually maintained |
| `asset_type_id` | UUID | **NULL** | `dim_asset_type.id` — nullable |

All fact tables have a `UNIQUE(date_id, asset_id)` constraint to prevent duplicate daily rows.

---

**fact_price:**
```yaml
fact_price:
  unique: (date_id, asset_id)
  columns:
    - id::uuid
    - date_id::integer        # FK: dim_date
    - asset_id::uuid          # FK: dim_asset
    - portfolio_id::uuid      # FK: dim_portfolio
    - sector_id::uuid null    # FK: dim_sector
    - tag_id::uuid null       # FK: dim_tag
    - asset_type_id::uuid null # FK: dim_asset_type
    - price::numeric          # current snapshot price from broker
    - avg_price::numeric      # DCA average cost per share
    - created_timestamp::timestamptz
    - updated_timestamp::timestamptz
```

> OHLC columns (open/close/high/low) removed — broker API delivers snapshot price only, not candlestick data.

**fact_valuation:**
```yaml
fact_valuation:
  unique: (date_id, asset_id)
  columns:
    - id::uuid
    - date_id::integer
    - asset_id::uuid
    - portfolio_id::uuid
    - sector_id::uuid null
    - tag_id::uuid null
    - asset_type_id::uuid null
    - value::numeric                 # shares × current price
    - cost_basis::numeric            # total cash invested
    - unrealized_pnl::numeric        # value - cost_basis
    - unrealized_pnl_pct::numeric    # unrealized_pnl / cost_basis × 100 (nullable: cost_basis may be 0)
    - realized_pnl::numeric null
    - position_weight_pct::numeric   # value / portfolio total_value × 100
    - fx_impact::numeric null
    - created_timestamp::timestamptz
    - updated_timestamp::timestamptz
```

**fact_return:**
```yaml
fact_return:
  unique: (date_id, asset_id)
  columns:
    - id::uuid
    - date_id::integer
    - asset_id::uuid
    - portfolio_id::uuid
    - sector_id::uuid null
    - tag_id::uuid null
    - asset_type_id::uuid null
    - daily_value_return::numeric    # day-over-day % change of position value (value_t - value_t-1) / value_t-1
    - cumulative_value_return::numeric  # cumulative product of daily_value_return since position opened
    - created_timestamp::timestamptz
    - updated_timestamp::timestamptz
```

**fact_technical:**
```yaml
fact_technical:
  unique: (date_id, asset_id)
  columns:
    - id::uuid
    - date_id::integer
    - asset_id::uuid
    - portfolio_id::uuid
    - sector_id::uuid null
    - tag_id::uuid null
    - asset_type_id::uuid null
    - value_drawdown_pct_30d::numeric   # (value - recent_value_high_30d) / recent_value_high_30d — position-value based, used by dashboard
    - price_drawdown_pct_30d::numeric   # (price - recent_price_high_30d)  / recent_price_high_30d  — NULL until 30 trading days of history
    - price_drawdown_pct_90d::numeric   # (price - recent_price_high_90d)  / recent_price_high_90d  — NULL until 90 trading days of history
    - price_drawdown_pct_180d::numeric  # (price - recent_price_high_180d) / recent_price_high_180d — NULL until 180 trading days of history
    - price_drawdown_pct_365d::numeric  # (price - recent_price_high_365d) / recent_price_high_365d — NULL until 365 trading days of history
    - value_high_alltime::numeric       # all-time high position value (MAX over all rows)
    - value_low_alltime::numeric        # all-time low position value (MIN over all rows)
    - value_ma_20d::numeric             # 20-day moving average of position value (AVG(value))
    - value_ma_30d::numeric             # 30-day moving average of position value (AVG(value))
    - value_ma_50d::numeric             # 50-day moving average of position value (AVG(value))
    - price_ma_20d::numeric             # 20-day moving average of asset price (AVG(price))
    - price_ma_50d::numeric             # 50-day moving average of asset price (AVG(price))
    - volatility_20d::numeric
    - volatility_30d::numeric
    - volatility_50d::numeric
    - var_95_1d::numeric             # volatility_30d × value × 1.65 (parametric VaR, 95% confidence)
    - profit_range_30d::numeric      # recent_profit_high_30d - recent_profit_low_30d
    - recent_profit_high_30d::numeric  # highest unrealized_pnl over the past 30 days
    - recent_profit_low_30d::numeric   # lowest unrealized_pnl over the past 30 days
    - recent_value_high_30d::numeric   # highest position value over the past 30 days
    - recent_value_low_30d::numeric    # lowest position value over the past 30 days
    - created_timestamp::timestamptz
    - updated_timestamp::timestamptz
```

**fact_signal:**
```yaml
fact_signal:
  unique: (date_id, asset_id)
  columns:
    - id::uuid
    - date_id::integer
    - asset_id::uuid
    - portfolio_id::uuid
    - sector_id::uuid null
    - tag_id::uuid null
    - asset_type_id::uuid null
    - dca_bias::numeric                  # price / avg_price; <1.0 = below average cost (DCA signal)
    - value_ma_crossover_signal::numeric # value_ma_20d - value_ma_50d; positive = short-term uptrend in position value
    - price_above_ma_20d::boolean        # price > price_ma_20d
    - price_above_ma_50d::boolean        # price > price_ma_50d
    - created_timestamp::timestamptz
    - updated_timestamp::timestamptz
```

**fact_portfolio_daily:**
```yaml
fact_portfolio_daily:
  unique: (date_id, portfolio_id)
  columns:
    - id::uuid
    - date_id::integer               # FK: dim_date
    - portfolio_id::uuid             # FK: dim_portfolio
    - total_value::numeric
    - total_cost::numeric
    - unrealized_pnl::numeric
    - unrealized_pnl_pct::numeric null
    - realized_pnl::numeric null
    - daily_value_change_abs::numeric null  # total_value(T) - total_value(T-1)
    - daily_value_change_pct::numeric null  # daily_value_change_abs / total_value(T-1) × 100
    - cash_available::numeric null
    - cash_reserved::numeric null
    - cash_in_pies::numeric null
    - cash_deployment_ratio::numeric null  # (total_value - cash_available) / total_value
    - fx_impact_total::numeric null        # SUM(fx_impact) across all positions
    - portfolio_volatility_weighted::numeric null  # Σ(weight_i × volatility_30d_i)
    - created_timestamp::timestamptz
    - updated_timestamp::timestamptz
```

---

## Dashboard Tab Mapping

| Tab | Primary tables |
|---|---|
| Portfolio | `fact_portfolio_daily`, `fact_valuation` |
| Valuation | `fact_price`, `fact_return`, `fact_signal` |
| Risk | `fact_technical`, `fact_valuation` (position_weight_pct) |
| Opportunities | `fact_signal`, `fact_technical` (pct_drawdown, volatility) |

---

## References

Star schema diagram: `docs/02-architecture/assets/analytics_star_schema_vx.x.x_latest.png`
