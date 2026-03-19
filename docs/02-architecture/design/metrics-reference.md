# Dashboard Metrics Reference

Maps every dashboard question to the metric that answers it, the formula, data source, and a plain-English explanation.

Use this document when designing gold layer tables — each row here is a potential column or derived field.

**Data source shorthand:**
- `staging.account` → `stg.acc`
- `staging.asset` → `stg.ast`
- `staging.asset_computed` → `stg.cmp`
- `External` → requires data outside the current pipeline

---

## Portfolio View

Questions the portfolio page should answer.

| Question | Metric | Formula | Data Source | Explanation |
|---|---|---|---|---|
| What is my total portfolio value right now? | Total Portfolio Value | Direct from broker | `stg.acc.total_value` | Current market value of all open positions plus all cash balances, as reported by the broker at last snapshot. |
| What is my total return since I started investing? (absolute) | Total Return — Absolute | `investments_unrealized_pnl + investments_realized_pnl` | `stg.acc` | Sum of all locked-in gains (closed positions) and open gains (current positions). Represents the full P&L of the portfolio. |
| What is my total return since I started investing? (%) | Total Return — % | `(unrealized_pnl + realized_pnl) / investments_total_cost × 100` | `stg.acc` | Total P&L as a percentage of total capital deployed. A return of 15% means every £1 invested is now worth £1.15. |
| How much have I invested in total (cost basis)? | Total Cost Basis | Direct from broker | `stg.acc.investments_total_cost` | The total amount of money that has been deployed into positions. Does not include cash. |
| What is my portfolio return today vs. yesterday? | Daily Portfolio Change — Absolute | `total_value(T) − total_value(T−1)` | `stg.acc` joined on consecutive `data_timestamp` | Requires comparing the latest snapshot with the previous day's snapshot. Both snapshots exist in the staging table. |
| What is my portfolio return today vs. yesterday? (%) | Daily Portfolio Change — % | `(total_value(T) − total_value(T−1)) / total_value(T−1) × 100` | `stg.acc` joined on consecutive `data_timestamp` | Day-over-day percentage change in total portfolio value. |
| Which assets are my best performers? | Position Return — % (ranked descending) | `profit / cost × 100` or `cumulative_return` | `stg.ast.profit`, `stg.ast.cost`, `stg.cmp.cumulative_return` | Ranks all positions by total return %. The top N positions are the best performers. |
| Which assets are my worst performers? | Position Return — % (ranked ascending) | `profit / cost × 100` or `cumulative_return` | `stg.ast.profit`, `stg.ast.cost`, `stg.cmp.cumulative_return` | Same metric, sorted ascending. Negative values indicate a loss on that position. |
| Which assets are dragging down the portfolio? | Unrealised P&L — Absolute (negative positions) | `profit` where `profit < 0` | `stg.ast.profit` | Positions with negative unrealised P&L are currently losing money. Sorting by profit ascending shows the biggest drags first. |
| How is my portfolio distributed across assets? | Position Weight — % | `asset.value / account.total_value × 100` | `stg.ast.value`, `stg.acc.total_value` | The percentage of total portfolio value held in each position. High concentration in one position increases idiosyncratic risk. |
| What is my overall portfolio volatility? | Portfolio Volatility (weighted) | `Σ (weight_i × volatility_30d_i)` | `stg.cmp.volatility_30d`, `stg.ast.value`, `stg.acc.total_value` | Weighted average of per-position 30D volatility. Weight = position value / total portfolio value. Approximates portfolio-level price uncertainty. |
| What is my overall portfolio market sensitivity? | Portfolio Beta | `Σ (weight_i × beta_i)` where `beta_i = Cov(r_asset_i, r_market) / Var(r_market)` | `stg.cmp.daily_return` + **External: market index daily returns** | Beta measures how much the portfolio moves relative to the market. Beta = 1.2 means a 10% market move causes a ~12% portfolio move. Requires an external index feed (e.g. S&P 500 or MSCI World). |
| How much cash do I have available? | Available Cash | Direct from broker | `stg.acc.cash_available_to_trade` | Free cash balance ready to be deployed into new or existing positions. |
| How much cash is locked in pending orders? | Reserved Cash | Direct from broker | `stg.acc.cash_reserved_for_orders` | Cash held aside for limit orders or pending trades. Not available to deploy elsewhere until the order is filled or cancelled. |
| What percentage of my portfolio is invested vs. sitting in cash? | Cash Deployment Ratio | `(total_value − cash_available_to_trade) / total_value × 100` | `stg.acc` | Shows how much of the portfolio is actively working in positions. A high ratio means most capital is deployed; a low ratio means significant idle cash. |
| What is the total FX drag across all positions? | Total FX Impact | `SUM(fx_impact)` across all positions | `stg.ast.fx_impact` | Aggregate currency drag (or tailwind) across all positions denominated in a foreign currency. Negative = FX headwind reducing returns; positive = FX tailwind boosting returns. |

---

## Asset View

Questions the asset detail page should answer.

| Question | Metric | Formula | Data Source | Explanation |
|---|---|---|---|---|
| How much have I spent on this asset total (cost basis)? | Total Cost Basis | Direct from broker | `stg.ast.cost` | The total cash invested into this position across all purchases. |
| What is my average cost per share? | Average Cost per Share (DCA) | Direct from broker | `stg.ast.avg_price` | The average price paid per share, accounting for all buy transactions. Buying more shares at a lower price reduces this. |
| What is my current return on this asset? (absolute) | Unrealised P&L — Absolute | `value − cost` | `stg.ast.profit` | How much this position has gained or lost in monetary terms since it was opened. |
| What is my current return on this asset? (%) | Unrealised P&L — % | `profit / cost × 100` | `stg.ast.profit`, `stg.ast.cost` | Return as a percentage of invested capital. 20% means the position is worth 20% more than what was paid for it. |
| What is the total return of this asset since opened? | Cumulative Return — % | `(price_now − price_at_open) / price_at_open × 100` | `stg.cmp.cumulative_return` | Total percentage gain or loss in market price since the position was first opened. Reflects asset price movement, not cost averaging. |
| What is the daily return trend over time? | Daily Return — % | `(price_today − price_yesterday) / price_yesterday × 100` | `stg.cmp.daily_return` | Day-over-day percentage price change. Plotting this over time reveals whether momentum is accelerating, fading, or reversing. |
| What is the current drawdown — how far is it from its peak? | Drawdown — % | `(value − value_high) / value_high × 100` | `stg.cmp.pct_drawdown`, `stg.cmp.value_high` | How far the current position value has fallen from its all-time high. A −25% drawdown means the position is currently worth 25% less than it was at peak. |
| Is now a good time to buy more (DCA opportunity)? | DCA Bias | `current_price / avg_price` | `stg.cmp.dca_bias` | A ratio below 1.0 means the current price is below your average cost — buying now would lower your average. Above 1.0 means buying now would raise it. The further below 1.0, the stronger the DCA signal. |
| What is the risk of buying more right now? | Volatility (30D) + Drawdown | Volatility: `std_dev(daily_returns, 30 days)` × `√252` to annualise; Drawdown: `pct_drawdown` | `stg.cmp.volatility_30d`, `stg.cmp.pct_drawdown` | High volatility means price is swinging widely — buying into high volatility increases the chance of an immediate paper loss. Deep drawdown signals the position is already significantly underwater. |
| Is this asset undervalued or overvalued relative to its price history? | MA Crossover Signal + DCA Bias | MA signal: `ma_20d − ma_50d` (positive = short-term uptrend, negative = downtrend); DCA bias vs. 1.0 | `stg.cmp.ma_20d`, `stg.cmp.ma_50d`, `stg.cmp.dca_bias` | When the 20D MA is above the 50D MA ("golden cross"), price momentum is positive. Combined with DCA bias < 1.0 gives a relative entry signal. This is a technical signal, not fundamental valuation. |
| What are the moving averages showing? | MA 20D / MA 30D / MA 50D | Simple moving average of closing price over N days: `SUM(price, N) / N` | `stg.cmp.ma_20d`, `stg.cmp.ma_30d`, `stg.cmp.ma_50d` | Smoothed price trends over different lookback windows. When current price is above all MAs, momentum is broadly positive. When short MA crosses below long MA ("death cross"), it signals weakening momentum. |
| How volatile has this asset been recently? | Volatility 20D / 30D / 50D | `std_dev(daily_returns, N days)` × `√252` | `stg.cmp.volatility_20d`, `stg.cmp.volatility_30d`, `stg.cmp.volatility_50d` | Standard deviation of daily returns, annualised. Higher = more price uncertainty. Useful for comparing risk levels between holdings. A stock at 40% annualised vol is substantially riskier than one at 15%. |
| Is the profit on this position stable or swinging wildly? | Profit Range — 30D | `recent_profit_high_30d − recent_profit_low_30d` | `stg.cmp.recent_profit_high_30d`, `stg.cmp.recent_profit_low_30d` | The width of the profit band over the last 30 days. A wide range means profits are volatile and unreliable. A narrow range means the position is steady. Useful for understanding how much day-to-day P&L swings on a position. |
| What is my downside exposure in monetary terms? | Value at Risk (VaR) — 95%, 1-day | `volatility_30d × value × 1.65` | `stg.cmp.volatility_30d`, `stg.ast.value` | Parametric VaR at 95% confidence interval. Means: there is a 5% chance of losing more than this amount in a single day. E.g. VaR = £150 means on 1 in 20 days, the position could fall by more than £150. The 1.65 factor is the z-score for 95% confidence. |
| What percentage of my holding is locked in pies vs. available to sell? | Pie-locked Quantity Ratio | `quantity_in_pies / quantity × 100` | `raw.v_bronze_asset.quantity_in_pies`, `raw.v_bronze_asset.quantity` | Shows liquidity of the position. Shares held inside Trading212 pies may have restricted selling. High pie ratio means most of the holding cannot be freely sold. Note: `quantity_in_pies` is in the bronze view but not currently promoted to `staging.asset`. |
| How does this asset correlate with the rest of my portfolio? | Pearson Correlation | `Cov(r_asset, r_portfolio) / (std_dev(r_asset) × std_dev(r_portfolio))` | `stg.cmp.daily_return` history + portfolio daily returns — requires **gold layer daily fact table** | Correlation of 1.0 means the asset moves in lockstep with the portfolio (no diversification benefit). Close to 0 means it moves independently. Negative values mean it acts as a partial hedge. Low correlation positions are the most valuable from a risk diversification perspective. |
| Is the short-term trend above or below the long-term trend? | MA Crossover — Signal | `ma_20d − ma_50d` (sign and magnitude) | `stg.cmp.ma_20d`, `stg.cmp.ma_50d` | Derived signal from existing MA columns. Positive = short-term price is trending above the longer-term average (bullish). Negative = short-term trend is deteriorating relative to the longer-term baseline (bearish). |
| What is the FX drag on this position? | FX Impact | Direct from broker | `stg.ast.fx_impact` | The portion of unrealised P&L attributable to currency movements, not price appreciation. Negative FX impact means currency movements have reduced returns on a foreign-denominated holding. |

---

## Metrics Requiring External Data

These metrics cannot be computed from the current pipeline alone. Each requires either an external price feed or additional reference data.

| Question | Metric | Formula | External Data Needed | Data Source (internal) | Explanation |
|---|---|---|---|---|---|
| How sensitive is my portfolio to market moves? | Beta — per asset and portfolio | `Cov(r_asset, r_market) / Var(r_market)` | Market index daily returns (e.g. S&P 500 `SPY`, MSCI World `IWRD`) | `stg.cmp.daily_return` | Beta > 1 means the asset amplifies market moves. Beta of 1.3 means a 10% market drop typically causes a ~13% position drop. Portfolio beta is the position-weighted average of individual betas. |
| How good are my risk-adjusted returns? | Sharpe Ratio | `(mean_daily_return − r_f) / std_dev_daily_return × √252` | Risk-free rate (e.g. UK 3-month gilt yield or US T-bill rate) | `stg.cmp.daily_return`, `stg.cmp.volatility_30d` | The industry standard for measuring return per unit of risk. Sharpe > 1 is considered acceptable; > 2 is strong. A Sharpe of 0.5 means you're getting half a unit of return for every unit of risk taken. |
| How is my portfolio allocated across sectors? | Sector Allocation — % | `SUM(value by sector) / total_value × 100` | Ticker → sector mapping (e.g. GICS classification from a financial data API) | `stg.ast.ticker`, `stg.ast.value` | Diversification across economic sectors (Technology, Healthcare, Financials, Energy, etc.). Concentrated sector exposure increases systemic risk — a sector-wide downturn hits the portfolio harder. |
| What is my true investment performance (excluding cash flow effects)? | Time-Weighted Return (TWRR) | `PRODUCT((1 + r_t)) − 1` across sub-periods between cashflow events | Full cashflow event history (deposits, withdrawals) | `stg.cmp.daily_return`, `stg.cmp.cashflow` — requires daily time series in gold layer | The industry-standard performance metric used by fund managers. Strips out the distorting effect of when you added or withdrew cash. A portfolio that doubles is less impressive if you added a large sum right before a market rally. TWRR isolates the manager's skill from the investor's timing. |
| What % of my positions are profitable? | Win Rate — % | `COUNT(positions where cumulative_return > 0) / COUNT(all positions) × 100` | None — computable once cumulative_return is reliable | `stg.cmp.cumulative_return` | Batting average for the portfolio. 60% win rate means 6 out of 10 positions are currently in profit. Useful for assessing selection quality, though win rate alone does not account for the size of wins vs. losses. |
| What is the worst peak-to-trough loss my portfolio has experienced? | Max Drawdown — Portfolio | `(peak_total_value − trough_total_value) / peak_total_value × 100` | None — computable from account history | `stg.acc.total_value` history — requires gold layer time series | The largest decline from a portfolio high point to its subsequent low point. Key risk metric. A max drawdown of −35% means the portfolio lost 35% of its value from peak before recovering. Standard metric in professional portfolio reporting. |
