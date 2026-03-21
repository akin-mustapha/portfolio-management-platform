# Dashboard Design

The gold layer is built to answer these questions. Each question maps to data the dashboard needs to display.
Add questions here first — then figure out what tables/columns are needed to answer them.

---

## Dashboard Tabs

The portfolio page is split into four tabs:

| Tab | Primary tables |
|---|---|
| Portfolio | `fact_portfolio_daily`, `fact_valuation` |
| Valuation | `fact_price`, `fact_return`, `fact_signal` |
| Risk | `fact_technical`, `fact_valuation` (`position_weight_pct`) |
| Opportunities | `fact_signal`, `fact_technical` (`pct_drawdown`, `volatility_*`) |

---

## Portfolio View

Questions the portfolio page should answer:

| Question | Table | Key columns |
|---|---|---|
| What is my total portfolio value right now? | `fact_portfolio_daily` | `total_value` |
| What is my total return (absolute and %) since I started? | `fact_portfolio_daily` | `unrealized_pnl`, `unrealized_pnl_pct` |
| How much have I invested in total (cost basis)? | `fact_portfolio_daily` | `total_cost` |
| What is my portfolio return today vs. yesterday? | `fact_portfolio_daily` | `daily_change_abs`, `daily_change_pct` |
| Which assets are my best and worst performers? | `fact_valuation` | `unrealized_pnl`, `unrealized_pnl_pct` |
| How is my portfolio distributed across assets? | `fact_valuation` | `position_weight_pct` |
| What is my overall portfolio risk (volatility)? | `fact_portfolio_daily` | `portfolio_volatility_weighted` |
| How much cash do I have available? | `fact_portfolio_daily` | `cash_available` |

---

## Asset View

Questions the asset detail page should answer:

| Question | Table | Key columns |
|---|---|---|
| How much have I spent on this asset (avg cost, cost basis)? | `fact_valuation`, `fact_price` | `cost_basis`, `avg_price` |
| What is my current return on this asset (absolute and %)? | `fact_valuation` | `unrealized_pnl`, `unrealized_pnl_pct` |
| What is the daily return trend over time? | `fact_return` | `daily_return`, `cumulative_return` |
| What is the current drawdown — how far is it from its peak? | `fact_technical` | `pct_drawdown`, `value_high` |
| Is now a good time to buy more? (DCA signal) | `fact_signal` | `dca_bias` |
| What is the risk of buying more right now? | `fact_technical` | `volatility_30d`, `var_95_1d` |
| Is this asset undervalued relative to its recent range? | `fact_technical` | `recent_value_high_30d`, `recent_value_low_30d`, `recent_profit_high_30d`, `recent_profit_low_30d` |
| What are the moving averages showing (20d, 30d, 50d)? | `fact_technical`, `fact_signal` | `ma_20d`, `ma_30d`, `ma_50d`, `ma_crossover_signal`, `price_above_ma_20d`, `price_above_ma_50d` |
| How volatile has this asset been recently? | `fact_technical` | `volatility_20d`, `volatility_30d`, `volatility_50d` |

---

## Questions Not Yet Categorised

> Drop new questions here, then move them to the right section once you know where they belong.
