# Schema

Gold layer data are stored on a postgres database

**schema**: `analytics`

## Dimensions

**dim_asset**:

```yaml
dim_asset
  columns:
    - id::uuid (auto generated)
    - asset_id::uuid
    - ticker::varchar
    - name::varchar
    - asset_type
    _ exchange
    - currency
    - created_timestamp
    - updated_timestamp
```

**dim_asset_type**:

```yaml
dim_asset_type
  columns:
    - id::uuid (auto generated)
    - asset_id::uuid
    - ticker::varchar
    - name::varchar
    - asset_type
    _ exchange
    - currency
    - created_timestamp
    - updated_timestamp
```

**dim_industry**:

```yaml
dim_industry
  columns:
    - id::uuid (auto generated)
    - industry_id::uuid
    - name::varchar
    - description::varchar
    - created_timestamp
    - updated_timestamp
```

**dim_portfolio**:

```yaml
dim_portfolio
  columns:
    - id::uuid (auto generated)
    - portfolio_id::uuid
    - name::varchar
    - base_currency::varchar
    - created_timestamp
    - updated_timestamp
```

**dim_sector**:

```yaml
dim_sector
  columns:
    - id::uuid (auto generated)
    - sector_id::uuid
    - industry_id::varchar
    - name::varchar
    - description
    - created_timestamp
    - updated_timestamp
```

**dim_tag**:

```yaml
dim_tag
  columns:
    - id::uuid (auto generated)
    - tag_id::uuid
    - name::varchar
    - description::varchar
    - created_timestamp
    - updated_timestamp
```

**dim_date**:

```yaml
dim_date
  columns:
    - id::uuid (auto generated)
    - date
    - year
    - quarter
    - month
    - month_name
    - day_of_month
    - day_of_week
    - day_name
    - is_weekend
    - is_month_start
    - is_month_end
    - is_year_start
    - is_year_end
    - created_timestamp
    - updated_timestamp
```

**dim_time**:

```yaml
dim_time
  columns:
    - id::uuid (auto generated)
    - time::uuid
    - hour::varchar
    - minute::varchar
    - second
    - created_timestamp
    - updated_timestamp
```

## Facts
