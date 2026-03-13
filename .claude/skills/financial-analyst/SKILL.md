---
name: financial-analyst
description: Use this skill when the user asks to suggest a metric to track, evaluate a new KPI, get dashboard insights, review what is currently being monitored, understand the financial data model, or asks questions like "what should I track", "suggest a metric", "what metrics do we have", "how should I use this dashboard", "what columns are available", "is this metric already tracked", "KPI recommendation", "portfolio health", "what can I measure".
---

# Financial Analyst

This skill provides financial analysis guidance for the **asset_monitoring_system** — a portfolio monitoring platform ingesting data from the Trading212 broker API.

## Portfolio System Context

**Data flow:** Trading212 API → `raw` (JSONB) → `staging` (typed, deduped) → `staging.asset_computed` (metrics) → `analytics` (Kimball facts/dims) → Dashboard

**Two data domains:**
- **Asset level** — per-position metrics (price, returns, volatility, drawdown, DCA signal)
- **Account level** — portfolio-wide metrics (total value, cash, realized/unrealized P&L)

Full schema: `.claude/skills/database/references/schema-reference.md`

---

## Existing Metrics (Quick Reference)

### Asset / Position Level (`staging.asset` + `staging.asset_computed`)

| Metric | Column | Meaning |
|---|---|---|
| Current price | `price` | Latest market price |
| Average cost | `avg_price` | DCA average price paid |
| Position value | `value` | Shares × current price |
| Cost basis | `cost` | Total amount invested |
| Unrealised P&L | `profit` | `value - cost` |
| FX impact | `fx_impact` | Currency drag on returns |
| Daily return | `daily_return` | Single-day % price change |
| Cumulative return | `cumulative_return` | Total return since position opened |
| Net cashflow | `cashflow` | Net cash in/out for the position |
| DCA bias | `dca_bias` | `current_price / avg_price` — signals if current price is above/below average cost |
| Drawdown | `pct_drawdown` | % drop from all-time-high value |
| All-time high value | `value_high` | Highest recorded position value |
| All-time low value | `value_low` | Lowest recorded position value |
| 30D value high | `recent_value_high_30d` | Rolling 30-day peak value |
| 30D value low | `recent_value_low_30d` | Rolling 30-day trough value |
| 30D profit high | `recent_profit_high_30d` | Rolling 30-day peak profit |
| 30D profit low | `recent_profit_low_30d` | Rolling 30-day trough profit |
| MA 20D | `ma_20d` | 20-day moving average of price |
| MA 30D | `ma_30d` | 30-day moving average of price |
| MA 50D | `ma_50d` | 50-day moving average of price |
| Volatility 20D | `volatility_20d` | 20-day price std dev |
| Volatility 30D | `volatility_30d` | 30-day price std dev |
| Volatility 50D | `volatility_50d` | 50-day price std dev |

### Account / Portfolio Level (`staging.account`)

| Metric | Column | Meaning |
|---|---|---|
| Total portfolio value | `total_value` | All assets + cash |
| Total invested | `investments_total_cost` | Sum of all cost bases |
| Realised P&L | `investments_realized_pnl` | Locked-in gains/losses |
| Unrealised P&L | `investments_unrealized_pnl` | Open gains/losses |
| Available cash | `cash_available_to_trade` | Free cash for new positions |
| Reserved cash | `cash_reserved_for_orders` | Cash locked in pending orders |
| Cash in pies | `cash_in_pies` | Cash allocated to pie portfolios |

---

## When Suggesting a New Metric

Before recommending any metric, answer these questions:

1. **Does it already exist?** Check the tables above and `schema-reference.md`. Avoid duplicates.
2. **Can it be computed from existing columns?** (e.g., Sharpe needs `daily_return` + risk-free rate)
3. **Which layer does it belong to?**
   - Atomic, per-position → `staging.asset_computed`
   - Aggregate / cross-asset → `analytics` gold layer (new fact table)
4. **What decision does it support?** A metric with no clear use case should not be added.
5. **What is the update frequency?** Daily snapshot (current pattern) or intraday?

---

## Dashboard Practical Use Cases

The dashboard has two pages — **Portfolio** and **Asset** — with different analytical purposes.

### Portfolio Page (`src/dashboard/core/pages/portfolio/`)
Answers: *How is my overall portfolio performing?*

| Use case | Metrics to show | Decision supported |
|---|---|---|
| Headline health | Portfolio value, total invested, unrealised P&L % | Am I up or down overall? |
| Cash management | `cash_available_to_trade`, `cash_reserved_for_orders` | Do I have dry powder to deploy? |
| Realised gains tracking | `investments_realized_pnl` | Tax planning, performance review |
| Market sensitivity | Beta (vs market index) | Is the portfolio over/under exposed to market moves? |

### Asset Page (`src/dashboard/core/pages/asset/`)
Answers: *Should I buy more, hold, or reduce this position?*

| Use case | Metrics to show | Decision supported |
|---|---|---|
| DCA decision | `dca_bias`, `avg_price` vs `price` | Is now a good entry to average down? |
| Risk monitoring | `pct_drawdown`, `volatility_30d` | Has the position become too risky? |
| Trend assessment | `ma_20d` vs `ma_50d` crossover | Is the trend turning? |
| Profit ranging | `recent_profit_high_30d`, `recent_profit_low_30d` | Is profit compressing or expanding? |

---

## Reference

Full metrics catalog with gaps and dashboard mapping:
`./references/metrics-catalog.md`
