---
name: schema
description: Gold layer schema documentation for the analytics database
---

# Schema

Gold layer data are stored on a Postgres database.

**schema**: `analytics`

## Dimensions

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
    - asset_type_id::uuid
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
    - industry_id::uuid
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
    - portfolio_id::uuid
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
    - sector_id::uuid
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
    - tag_id::uuid
    - name::varchar
    - description::varchar
    - created_timestamp::timestamptz
    - updated_timestamp::timestamptz
```

**dim_date:**

```yaml
dim_date:
  columns:
    - id::integer (auto generated)
    - date::date
    - year::smallint
    - quarter::smallint
    - month::smallint
    - month_name::varchar
    - day_of_month::smallint
    - day_of_week::smallint
    - day_name::varchar
    - is_weekend::boolean
    - is_month_start::boolean
    - is_month_end::boolean
    - is_year_start::boolean
    - is_year_end::boolean
    - created_timestamp::timestamptz
    - updated_timestamp::timestamptz
```

**dim_time:**

```yaml
dim_time:
  columns:
    - id::integer (auto generated)
    - time::timetz
    - hour::smallint
    - minute::smallint
    - second::smallint
    - created_timestamp::timestamptz
    - updated_timestamp::timestamptz
```

## Facts

**fact_cashflow:**

```yaml
fact_cashflow:
  columns:
    - id::uuid (auto generated)
    - date_id::integer       # FK: dim_date
    - asset_id::uuid         # FK: dim_asset
    - portfolio_id::uuid     # FK: dim_portfolio
    - sector_id::uuid        # FK: dim_sector
    - tag_id::uuid           # FK: dim_tag
    - asset_type_id::uuid    # FK: dim_asset_type
    - cashflow::numeric
    - created_timestamp::timestamptz
    - updated_timestamp::timestamptz
```

**fact_price:**

```yaml
fact_price:
  columns:
    - id::uuid (auto generated)
    - date_id::integer       # FK: dim_date
    - asset_id::uuid         # FK: dim_asset
    - portfolio_id::uuid     # FK: dim_portfolio
    - sector_id::uuid        # FK: dim_sector
    - tag_id::uuid           # FK: dim_tag
    - asset_type_id::uuid    # FK: dim_asset_type
    - price::numeric
    - average_price::numeric
    - open_price::numeric
    - close_price::numeric
    - high::numeric
    - low::numeric
    - created_timestamp::timestamptz
    - updated_timestamp::timestamptz
```

**fact_return:**

```yaml
fact_return:
  columns:
    - id::uuid (auto generated)
    - date_id::integer       # FK: dim_date
    - asset_id::uuid         # FK: dim_asset
    - portfolio_id::uuid     # FK: dim_portfolio
    - sector_id::uuid        # FK: dim_sector
    - tag_id::uuid           # FK: dim_tag
    - asset_type_id::uuid    # FK: dim_asset_type
    - return::numeric
    - cumulative_return::numeric
    - created_timestamp::timestamptz
    - updated_timestamp::timestamptz
```

**fact_signal:**

```yaml
fact_signal:
  columns:
    - id::uuid (auto generated)
    - date_id::integer       # FK: dim_date
    - asset_id::uuid         # FK: dim_asset
    - portfolio_id::uuid     # FK: dim_portfolio
    - sector_id::uuid        # FK: dim_sector
    - tag_id::uuid           # FK: dim_tag
    - asset_type_id::uuid    # FK: dim_asset_type
    - dca_bias::varchar
    - created_timestamp::timestamptz
    - updated_timestamp::timestamptz
```

**fact_technical:**

```yaml
fact_technical:
  columns:
    - id::uuid (auto generated)
    - date_id::integer       # FK: dim_date
    - asset_id::uuid         # FK: dim_asset
    - portfolio_id::uuid     # FK: dim_portfolio
    - sector_id::uuid        # FK: dim_sector
    - tag_id::uuid           # FK: dim_tag
    - asset_type_id::uuid    # FK: dim_asset_type
    - pct_drawdown::numeric
    - ma_20d::numeric
    - ma_30d::numeric
    - ma_50d::numeric
    - volatility_20d::numeric
    - volatility_30d::numeric
    - volatility_50d::numeric
    - created_timestamp::timestamptz
    - updated_timestamp::timestamptz
```

**fact_valuation:**

```yaml
fact_valuation:
  columns:
    - id::uuid (auto generated)
    - date_id::integer       # FK: dim_date
    - asset_id::uuid         # FK: dim_asset
    - portfolio_id::uuid     # FK: dim_portfolio
    - sector_id::uuid        # FK: dim_sector
    - tag_id::uuid           # FK: dim_tag
    - asset_type_id::uuid    # FK: dim_asset_type
    - value::numeric
    - unrealized_pnl::numeric
    - created_timestamp::timestamptz
    - updated_timestamp::timestamptz
```

References

**analytics_star_schema:** `docs/03-architecture/analytics_star_schema_vx.x.x_latest.png`
