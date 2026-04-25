export const metricDefinitions = {
  // --- Table columns ---
  trend: {
    title: 'Trend',
    definition:
      "Shows whether the asset's short-term momentum (20-day moving average) is above or below its medium-term trend (50-day moving average).",
    interpret:
      'An upward arrow means the short-term trend is strengthening — often a buy signal. A downward arrow means momentum is fading. Use as a directional cue, not a guarantee.',
  },
  profit: {
    title: 'P&L (£)',
    definition:
      'The unrealised gain or loss on your current holding in British pounds — what you would pocket (or lose) if you sold today.',
    interpret:
      'Positive is profit, negative is loss. This figure moves with price and exchange rates. It only becomes real when you sell.',
  },
  pnl_pct: {
    title: 'P&L %',
    definition:
      'Your unrealised gain or loss expressed as a percentage of what you originally paid for the position.',
    interpret:
      'A reading of +20% means the position is worth 20% more than your cost. More useful than the £ figure for comparing positions of different sizes.',
  },
  cumulative_value_return: {
    title: 'Cumul. Return',
    definition:
      'The total percentage return on this position from the day you first bought it to today.',
    interpret:
      'This is your full track record on the position. Unlike daily return, it accumulates every price move since entry — higher is better, and negative means you are still underwater overall.',
  },
  daily_value_return: {
    title: 'Daily Return',
    definition: "How much the asset's price moved today, expressed as a percentage.",
    interpret:
      'A +2% reading means the price rose 2% in a single session. Normal daily moves for individual stocks are typically within ±3%; anything beyond that is worth investigating.',
  },
  value_ma_crossover_signal: {
    title: 'MA Signal',
    definition:
      'A buy or sell signal derived from whether the 20-day moving average is currently above (↑ Bullish) or below (↓ Bearish) the 50-day moving average.',
    interpret:
      'Bullish means short-term momentum is outpacing the medium-term trend — a positive sign. Bearish means the opposite. Treat this as one data point, not a trading instruction.',
  },
  avg_price: {
    title: 'Avg Cost',
    definition:
      'The average price per share you have paid across all purchases of this asset, accounting for any top-ups or dollar-cost averaging.',
    interpret:
      'If the current price is above this number, the position is in profit. If below, you are holding at a loss. Useful for deciding whether adding more shares would lower your break-even price.',
  },
  weight_pct: {
    title: 'Weight %',
    definition: "This position's share of your total portfolio value as a percentage.",
    interpret:
      'A weight of 20% means one-fifth of your money is in this single stock. Most diversification guidelines suggest keeping any single position below 10–15% to limit concentration risk.',
  },
  recent_profit_high_30d: {
    title: '30D High',
    definition: 'The highest unrealised profit value this position reached over the last 30 days.',
    interpret:
      'Compare this to your current P&L to understand how much paper profit you have given back recently. A large gap between the 30D High and current P&L may suggest the position has weakened.',
  },
  value_drawdown_pct_30d: {
    title: '% Drawdown',
    definition:
      'How far the current position value has fallen from its highest point in the last 30 days, expressed as a percentage.',
    interpret:
      'A drawdown of -15% means the position is worth 15% less than its recent peak. Small drawdowns (under 10%) are normal; persistent or deepening drawdowns may indicate a trend reversal.',
  },
  volatility_30d: {
    title: 'Vol 30D',
    definition:
      'The annualised standard deviation of daily price returns over the last 30 days — a measure of how much the price has been jumping around.',
    interpret:
      'A reading of 20% is typical for a large-cap stock; above 40% is high and suggests meaningful price risk. Higher volatility means larger potential swings in both directions.',
  },
  var_95_1d: {
    title: 'VaR 95%',
    definition:
      'The maximum loss you could expect on this position in a single day, 95% of the time, based on recent price behaviour.',
    interpret:
      'A VaR of £50 means that on 19 out of 20 trading days, your daily loss should not exceed £50 — but on the remaining 1 in 20, it could be worse. Larger numbers signal higher short-term risk.',
  },
  dca_bias: {
    title: 'DCA Bias',
    definition:
      'A score that indicates whether the current price is trading below your average cost, suggesting the position may benefit from adding more shares at a lower price.',
    interpret:
      'A positive score means the current price is below your average cost — conditions where averaging down could reduce your break-even. A score near zero or negative means there is less case for adding. Not a recommendation to buy.',
  },

  // --- Secondary KPI badges (portfolio-level) ---
  daily_change_pct: {
    title: 'Daily Change %',
    definition: "The total portfolio's percentage change in value over the current trading day.",
    interpret:
      'This aggregates all your holdings — a +1% day means your portfolio grew by 1% today. Compare this to broader indices (e.g. S&P 500 daily move) to see whether you are keeping pace with the market.',
  },
  portfolio_volatility_30d: {
    title: 'Volatility 30D',
    definition:
      "The weighted average of your individual positions' 30-day volatility, giving a portfolio-level view of how turbulent your holdings have been.",
    interpret:
      'Below 15% is relatively calm; 15–30% is moderate; above 30% means your portfolio has been experiencing significant swings. A high reading does not mean you will lose — it means your daily moves are large in both directions.',
  },
  portfolio_beta: {
    title: 'Beta',
    definition:
      'Measures how much your portfolio tends to move relative to the S&P 500 over the last 60 days, weighted by position size.',
    interpret:
      'A beta of 1.0 means your portfolio moves in lockstep with the market. Above 1.0 means it amplifies market moves (higher risk, higher potential reward). Below 1.0 means it moves less than the market.',
  },
  portfolio_sharpe_30d: {
    title: 'Sharpe 30D',
    definition:
      'A risk-adjusted return measure over the last 30 days — how much return you are generating per unit of volatility taken.',
    interpret:
      'Above 1.0 is considered good; above 2.0 is strong. A negative Sharpe means the portfolio is losing money even after accounting for risk taken. Use this to compare performance quality, not just raw returns.',
  },
  portfolio_vs_sp500_30d: {
    title: 'vs S&P500 30D',
    definition:
      "The difference between your portfolio's 30-day return and the S&P 500's 30-day return, showing whether you are beating or lagging the benchmark.",
    interpret:
      'A positive reading means you outperformed the index over the last month. A negative reading means the market returned more than your portfolio did. This is the simplest measure of whether active stock picking is adding value.',
  },

  // --- Portfolio-level charts ---
  portfolio_value_chart: {
    title: 'Portfolio Value',
    definition:
      'A line chart showing how the total market value of your portfolio has changed over time, with a second line showing your cumulative cost basis (what you have invested).',
    interpret:
      'When the value line is above the cost basis line, you are in overall profit. The gap between the two lines is your unrealised gain or loss. Watch for the two lines converging or crossing — that signals portfolio-level losses mounting.',
  },
  portfolio_pnl_chart: {
    title: 'Portfolio P&L',
    definition:
      'Shows unrealised P&L (open positions), realised P&L (closed trades), and total P&L over time as separate lines.',
    interpret:
      'Realised P&L is locked in; unrealised can still move. If total P&L is rising but unrealised is falling, you may have taken profits but remaining positions are weakening. All three lines trending up together is the healthiest pattern.',
  },
  portfolio_drawdown_chart: {
    title: 'Portfolio Drawdown',
    definition:
      'Tracks how far your portfolio value has fallen from its all-time high at each point in time, expressed as a percentage.',
    interpret:
      'A reading of -10% means your portfolio is currently worth 10% less than its peak. Drawdowns under 10% are routine; sustained drawdowns above 20% may warrant reviewing your positioning. Flat lines near 0% indicate you are near all-time highs.',
  },
  position_weight_chart: {
    title: 'Position Weight',
    definition:
      'A donut chart showing how your total portfolio value is split across each holding as a percentage.',
    interpret:
      'Look for any single slice dominating — over 15–20% in one stock is a concentration risk. A healthy portfolio typically has no single dominant position unless that is deliberate strategy.',
  },
  fx_attribution_chart: {
    title: 'FX Attribution',
    definition:
      'Breaks down your portfolio return into how much came from actual price performance versus how much was driven by currency movements between GBP and the asset\'s home currency.',
    interpret:
      'If a large slice is attributed to FX, your return is sensitive to exchange rate movements — not just how well the company is doing. A large FX contribution can flatter or distort your true investment performance.',
  },
  portfolio_concentration_chart: {
    title: 'Portfolio Concentration',
    definition:
      'A treemap where each box represents one holding — the size of the box reflects its portfolio weight and the colour indicates its return on investment.',
    interpret:
      'Large green boxes are your high-value winners. Large red boxes are costly underperformers deserving attention. Small boxes have limited impact either way. Use this to spot whether your biggest positions are working for you.',
  },
  var_by_position_chart: {
    title: 'Value at Risk by Position',
    definition:
      'Ranks your holdings by their individual 1-day VaR at 95% confidence, showing which positions carry the most short-term downside risk in pound terms.',
    interpret:
      'The longest bars represent your riskiest positions in absolute terms — they could move against you by that amount on any given day. Compare these bars against position size: high VaR in a small position is less concerning than high VaR in a large one.',
  },
  position_profitability_chart: {
    title: 'Position Profitability',
    definition:
      'A simple count of how many of your current positions are in profit versus at a loss.',
    interpret:
      'If more than half your positions are in the red, your stock selection or entry timing may need review. A majority in profit does not guarantee portfolio gains — one large loss can outweigh several small wins.',
  },

  // --- Opportunities charts ---
  position_performance_map_chart: {
    title: 'Position Performance Map',
    definition:
      'Plots each holding on a chart where the x-axis is ROI %, the y-axis is portfolio weight %, and the bubble size represents the position\'s absolute value — divided into four quadrants.',
    interpret:
      'Top-right (High Value Winners) is where you want your biggest holdings. Bottom-left (Dead Weights) signals small losing positions worth reviewing. Top-left (Speculative) means significant capital in loss-making positions — a warning zone. Bottom-right (Low Value Winners) shows small profitable positions you may want to grow.',
  },

  // --- Asset-level charts ---
  asset_price_chart: {
    title: 'Price Structure',
    definition:
      "Shows the asset's daily closing price over time with the 30-day and 50-day moving averages overlaid as smooth trend lines.",
    interpret:
      "When price is above both moving averages, the asset is in an uptrend. When it crosses below either line, momentum may be weakening. The gap between MA30 and MA50 shows how strong or fading the short-term trend is relative to the medium-term.",
  },
  asset_value_chart: {
    title: 'Asset Value',
    definition:
      'Shows the total market value of your holding in this specific asset over time (shares held × price at each point).',
    interpret:
      'Growth in this line reflects both price appreciation and any additional shares purchased. A falling line means your position value is declining. Compare the shape to the price chart to understand whether changes are driven by price or by you buying or selling.',
  },
  asset_profit_range_chart: {
    title: 'Profit Range 30D',
    definition:
      "Plots the asset's daily unrealised P&L with a shaded band showing the highest and lowest P&L reached over the last 30 days.",
    interpret:
      "The band gives you context for where today's profit sits within recent history. If current P&L is near the bottom of the band, you have given back most recent gains. If near the top, the position is performing at its best recent level.",
  },
  asset_risk_chart: {
    title: 'Risk Context',
    definition:
      "Shows the asset's rolling 30-day annualised volatility over time, giving you a historical view of how risky the stock has been at different periods.",
    interpret:
      'Rising volatility means the stock is becoming more unpredictable — useful context before adding to a position. Periods of low volatility followed by sharp spikes often coincide with earnings releases or news events.',
  },
  asset_dca_bias_chart: {
    title: 'DCA Bias',
    definition:
      'Plots the DCA bias score for this asset over time, showing how the signal has shifted as your average cost and the market price have moved relative to each other.',
    interpret:
      'Periods where the score rises indicate the price was dropping below your average cost — historically the conditions under which adding shares lowers your break-even. A declining score means the price has recovered above your average cost and the averaging opportunity has reduced.',
  },
  asset_daily_return_chart: {
    title: 'Daily Return',
    definition:
      "A bar chart showing this asset's day-by-day percentage price change, giving you a session-by-session view of how the stock has been moving.",
    interpret:
      'Consistent small bars indicate a stable, low-volatility period. Large spikes — positive or negative — flag days with significant news or market events. Clustering of red bars is an early signal of a downtrend taking hold.',
  },
  asset_vs_portfolio_return_chart: {
    title: 'Asset vs Portfolio Return',
    definition:
      'An indexed comparison where both the individual asset and your overall portfolio start at 100 and are tracked forward from the same date, letting you see relative performance on the same scale.',
    interpret:
      'If the asset line rises faster than the portfolio line, it is outperforming your broader holdings. If it lags, the asset is a drag on overall returns. Crossovers between the two lines mark the point where relative performance shifted.',
  },
} as const

export type MetricKey = keyof typeof metricDefinitions
