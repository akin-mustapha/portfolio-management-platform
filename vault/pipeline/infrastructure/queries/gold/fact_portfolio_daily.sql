SELECT
    TO_CHAR(acc.data_timestamp, 'YYYYMMDD')::INTEGER AS date_id,
    dp.id                                            AS portfolio_id,

    acc.total_value,
    acc.investments_total_cost                       AS total_cost,
    acc.investments_unrealized_pnl                   AS unrealized_pnl,
    acc.investments_unrealized_pnl
        / NULLIF(acc.investments_total_cost, 0) * 100 AS unrealized_pnl_pct,
    acc.investments_realized_pnl                     AS realized_pnl,

    (acc.investments_total_cost + acc.investments_unrealized_pnl)
        - COALESCE(
            acc.prev_invested_value,
            acc.investments_total_cost + acc.investments_unrealized_pnl
        )                                            AS daily_value_change_abs,
    ((acc.investments_total_cost + acc.investments_unrealized_pnl)
        - COALESCE(
            acc.prev_invested_value,
            acc.investments_total_cost + acc.investments_unrealized_pnl
        ))
        / NULLIF(acc.prev_invested_value, 0) * 100   AS daily_value_change_pct,

    acc.cash_available_to_trade                      AS cash_available,
    acc.cash_reserved_for_orders                     AS cash_reserved,
    acc.cash_in_pies,
    (acc.total_value - acc.cash_available_to_trade)
        / NULLIF(acc.total_value, 0) * 100           AS cash_deployment_ratio,

    acc.fx_impact_total,
    acc.portfolio_volatility_weighted,
    acc.portfolio_beta_weighted,

    acc.sharpe_ratio_30d,
    acc.benchmark_return_daily,
    acc.portfolio_vs_benchmark_30d
FROM staging.v_account_metrics acc
CROSS JOIN (
    SELECT id FROM analytics.dim_portfolio WHERE portfolio_id = :portfolio_id
) dp
