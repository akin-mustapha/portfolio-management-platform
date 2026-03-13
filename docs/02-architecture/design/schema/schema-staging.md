---
name:
description:
---

# Schema

Silver layer schema

**asset:**

```yaml
asset
  columns:
    - id
    - data_timestamp
    - external_id
    - ticker
    - name
    - description
    - broker
    - currency
    - local_currency
    - share
    - price
    - avg_price
    - value
    - cost
    - profit
    - fx_impact
    - business_key
    - created_timestamp
    - updated_timestamp
```

**asset_computed:**

```yaml
asset_computed
  columns:
    - asset_id
    - cashflow
    - daily_return
    - cumulative_return
    - dca_bias
    - pct_drawdown
    - recent_value_high_30d
    - recent_value_low_30d
    - recent_profit_high_30d
    - recent_profit_low_30d
    - value_high
    - value_low
    - ma_20d
    - ma_30d
    - ma_50d
    - volatility_20d
    - volatility_30d
    - volatility_50d
    - created_timestamp
```

**account:**

```yaml
account
  columns:
    - id
    - data_timestamp
    - external_id
    - cash_in_pies
    - cash_available_to_trade
    - cash_reserved_for_orders
    - broker
    - currency
    - total_value
    - investments_total_cost
    - investments_realized_pnl
    - investments_unrealized_pnl
    - business_key
    - created_timestamp
    - updated_timestamp
```

**account_computed:**

```yaml

```
