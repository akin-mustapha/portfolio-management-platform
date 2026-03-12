---
name: metrics-catalog
description: Complete catalog of all tracked financial metrics, their source columns, layers, and dashboard placements. Also lists gap metrics not yet implemented.
---

# Metrics Catalog

## How to Read This Catalog

- **Layer**: where the metric lives (`staging` = computed per-position, `account` = portfolio-wide, `analytics` = gold aggregated)
- **Source columns**: raw inputs used to derive the metric
- **Dashboard**: which page/component displays it (file path relative to `src/dashboard/`)
- **Status**: `tracked` = in DB and on dashboard, `db-only` = in DB but not surfaced on dashboard, `gap` = not yet implemented

---

## Asset / Position Metrics

| Metric | Column | Layer | Source | Dashboard Component | Status |
|---|---|---|---|---|---|
| Current price | `staging.asset.price` | staging | broker API `currentPrice` | `pages/asset/components/kpi.py` → `asset_kpi_section` | tracked |
| Average cost | `staging.asset.avg_price` | staging | broker API `averagePricePaid` | `pages/asset/components/figures.py` | tracked |
| Position value | `staging.asset.value` | staging | broker API `currentValue` | `pages/asset/components/tables.py` | tracked |
| Cost basis | `staging.asset.cost` | staging | broker API `totalCost` | `pages/asset/components/tables.py` | tracked |
| Unrealised P&L | `staging.asset.profit` | staging | `value - cost` | `pages/asset/components/tables.py` | tracked |
| FX impact | `staging.asset.fx_impact` | staging | broker API `fxImpact` | — | db-only |
| Daily return | `staging.asset_computed.daily_return` | staging | price delta % | — | db-only |
| Cumulative return | `staging.asset_computed.cumulative_return` | staging | total price % from open | — | db-only |
| Net cashflow | `staging.asset_computed.cashflow` | staging | derived from cost changes | — | db-only |
| DCA bias | `staging.asset_computed.dca_bias` | staging | `price / avg_price` | `pages/asset/components/kpi.py` → `asset_kpi_section` | tracked |
| Drawdown | `staging.asset_computed.pct_drawdown` | staging | `(value - value_high) / value_high` | `pages/asset/components/kpi.py` → `asset_kpi_section` | tracked |
| All-time high value | `staging.asset_computed.value_high` | staging | rolling max | — | db-only |
| All-time low value | `staging.asset_computed.value_low` | staging | rolling min | — | db-only |
| 30D value high | `staging.asset_computed.recent_value_high_30d` | staging | 30-day rolling max value | `pages/asset/components/figures.py` | tracked |
| 30D value low | `staging.asset_computed.recent_value_low_30d` | staging | 30-day rolling min value | `pages/asset/components/figures.py` | tracked |
| 30D profit high | `staging.asset_computed.recent_profit_high_30d` | staging | 30-day rolling max profit | — | db-only |
| 30D profit low | `staging.asset_computed.recent_profit_low_30d` | staging | 30-day rolling min profit | — | db-only |
| MA 20D | `staging.asset_computed.ma_20d` | staging | 20-day price moving avg | `pages/asset/components/figures.py` | tracked |
| MA 30D | `staging.asset_computed.ma_30d` | staging | 30-day price moving avg | `pages/asset/components/figures.py` | tracked |
| MA 50D | `staging.asset_computed.ma_50d` | staging | 50-day price moving avg | `pages/asset/components/figures.py` | tracked |
| Volatility 20D | `staging.asset_computed.volatility_20d` | staging | 20-day price std dev | — | db-only |
| Volatility 30D | `staging.asset_computed.volatility_30d` | staging | 30-day price std dev | `pages/asset/components/kpi.py` → `asset_kpi_section` | tracked |
| Volatility 50D | `staging.asset_computed.volatility_50d` | staging | 50-day price std dev | — | db-only |

---

## Account / Portfolio Metrics

| Metric | Column | Layer | Source | Dashboard Component | Status |
|---|---|---|---|---|---|
| Total portfolio value | `staging.account.total_value` | account | broker API `totalValue` | `pages/portfolio/components/kpis.py` → `kpi_row` | tracked |
| Total invested | `staging.account.investments_total_cost` | account | broker API `investments.totalCost` | `pages/portfolio/components/kpis.py` → `kpi_row` | tracked |
| Realised P&L | `staging.account.investments_realized_pnl` | account | broker API `investments.realizedProfitLoss` | `pages/portfolio/components/kpis.py` → `kpi_row` | tracked |
| Unrealised P&L | `staging.account.investments_unrealized_pnl` | account | broker API `investments.unrealizedProfitLoss` | `pages/portfolio/components/kpis.py` → `kpi_row` | tracked |
| Available cash | `staging.account.cash_available_to_trade` | account | broker API `cash.availableToTrade` | — | db-only |
| Reserved cash | `staging.account.cash_reserved_for_orders` | account | broker API `cash.reservedForOrders` | — | db-only |
| Cash in pies | `staging.account.cash_in_pies` | account | broker API `cash.inPies` | — | db-only |
| Beta | *(not in DB)* | — | requires market index reference data | `pages/portfolio/components/kpis.py` → `kpi_row` | **gap** ⚠️ |

> **Note on Beta**: The portfolio KPI card renders a `beta` field (`kpis.py:48`) but this column does not exist in `staging.account`. It defaults to `1`. This is a known gap — implementing it requires an external market index (e.g. S&P 500) price feed.

---

## Gap Metrics (Not Yet Implemented)

These are valuable metrics computable from existing data or with minor additions.

### Computable from Existing Columns

| Metric | Formula / Source | Suggested Layer | Use Case |
|---|---|---|---|
| Position weight (%) | `value / total_value` | `staging.asset_computed` or analytics gold | Concentration risk — which positions dominate the portfolio |
| P&L % per position | `profit / cost * 100` | `staging.asset_computed` | Quick win/loss % per holding |
| MA crossover signal | `ma_20d > ma_50d` → bullish | `staging.asset_computed` | Trend confirmation for buy/hold decisions |
| Profit range width | `recent_profit_high_30d - recent_profit_low_30d` | `staging.asset_computed` | Measures profit stability vs swings |
| Value at risk (VaR) | `volatility_30d * value * 1.65` (95% 1-day) | `staging.asset_computed` | Downside exposure in currency terms |
| Cash deployment ratio | `(total_value - cash_available_to_trade) / total_value` | analytics / account | How much of the portfolio is invested vs idle |

### Requires Additional Data

| Metric | What's Needed | Suggested Layer | Use Case |
|---|---|---|---|
| Beta (vs index) | Market index price feed (e.g. S&P 500, MSCI World) | analytics gold | Measures portfolio sensitivity to market moves |
| Sharpe ratio | Risk-free rate + `daily_return` history | analytics gold | Risk-adjusted return quality |
| Time-weighted return (TWRR) | Full cashflow history + `daily_return` | analytics gold | True performance excluding cash flow timing effects |
| Sector allocation % | `dim_sector` populated + `value` per sector | analytics gold | Diversification analysis |
| Win rate | Count of positions where `cumulative_return > 0` | analytics gold | Portfolio batting average |
| Max drawdown (all-time) | `value_high` and `value_low` history | analytics gold | Worst historical loss scenario |

---

## Dashboard Component Map

| Dashboard File | Metrics Consumed |
|---|---|
| `pages/asset/components/kpi.py` | `price`, `pct_drawdown`, `volatility_30d`, `dca_bias`, trend (derived) |
| `pages/asset/components/figures.py` | `ma_20d`, `ma_30d`, `ma_50d`, `recent_value_high_30d`, `recent_value_low_30d`, `avg_price` |
| `pages/asset/components/tables.py` | `value`, `cost`, `profit`, `share`, `price` |
| `pages/portfolio/components/kpis.py` | `total_value`, `investments_total_cost`, `investments_unrealized_pnl`, `investments_realized_pnl`, beta (gap) |
| `pages/portfolio/components/charts.py` | portfolio-level aggregations (check for latest) |
| `pages/portfolio/components/tables.py` | per-asset summary rows |
