---
name: schema-staging
description: Silver layer schema reference for staging.asset, staging.asset_computed, staging.account, staging.account_computed
---

# Schema — Staging (Silver Layer)

Silver layer schema. Source of truth is the migration files in `migrations/postgres/versions/staging/`.

---

**staging.asset**

```yaml
asset:
  columns:
    - id                   # UUID, PK
    - data_timestamp       # TIMESTAMPTZ
    - external_id          # TEXT
    - ticker               # TEXT
    - name                 # TEXT
    - description          # TEXT
    - broker               # TEXT
    - currency             # TEXT
    - local_currency       # TEXT
    - share                # FLOAT
    - price                # FLOAT
    - avg_price            # FLOAT
    - value                # FLOAT
    - cost                 # FLOAT
    - profit               # FLOAT
    - fx_impact            # FLOAT
    - quantity_in_pies     # FLOAT  (added migration 009)
    - business_key         # TEXT, unique
    - created_timestamp    # TIMESTAMPTZ
    - updated_timestamp    # TIMESTAMPTZ
```

---

**staging.asset_computed**

```yaml
asset_computed:
  columns:
    - asset_id             # UUID, FK → staging.asset(id), unique
    - cost_basis           # FLOAT  (renamed from cashflow — migration 011)
    - daily_return         # FLOAT
    - cumulative_return    # FLOAT
    - dca_bias             # FLOAT
    - pct_drawdown         # FLOAT
    - recent_value_high_30d   # FLOAT
    - recent_value_low_30d    # FLOAT
    - recent_profit_high_30d  # FLOAT
    - recent_profit_low_30d   # FLOAT
    - value_high           # FLOAT
    - value_low            # FLOAT
    - ma_20d               # FLOAT
    - ma_30d               # FLOAT
    - ma_50d               # FLOAT
    - volatility_20d       # FLOAT
    - volatility_30d       # FLOAT
    - volatility_50d       # FLOAT
    - pnl_pct              # FLOAT  (added migration 006)
    - var_95_1d            # FLOAT  (added migration 006)
    - profit_range_30d     # FLOAT  (added migration 006)
    - ma_crossover_signal  # FLOAT  (added migration 006)
    - position_weight_pct  # FLOAT  (added migration 010)
    - created_timestamp    # TIMESTAMPTZ
```

---

**staging.account**

```yaml
account:
  columns:
    - id                          # UUID, PK
    - data_timestamp              # TIMESTAMPTZ
    - external_id                 # TEXT
    - cash_in_pies                # FLOAT
    - cash_available_to_trade     # FLOAT
    - cash_reserved_for_orders    # FLOAT
    - broker                      # TEXT
    - currency                    # TEXT
    - total_value                 # FLOAT
    - investments_total_cost      # FLOAT
    - investments_realized_pnl    # FLOAT
    - investments_unrealized_pnl  # FLOAT
    - business_key                # TEXT, unique
    - created_timestamp           # TIMESTAMPTZ
    - updated_timestamp           # TIMESTAMPTZ
```

---

**staging.account_computed**

```yaml
account_computed:
  columns:
    - account_id             # UUID, FK → staging.account(id), unique
    - total_return_abs       # FLOAT
    - total_return_pct       # FLOAT
    - cash_deployment_ratio  # FLOAT
    - daily_change_abs       # FLOAT
    - daily_change_pct                 # FLOAT
    - portfolio_volatility_weighted    # FLOAT  (added migration 010)
    - created_timestamp                # TIMESTAMPTZ NOT NULL DEFAULT now()
```
