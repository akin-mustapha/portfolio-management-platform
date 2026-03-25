WITH asset_daily AS (
    SELECT
        id,
        ticker,
        snapshot_id,
        data_timestamp,
        value,
        cost,
        profit,
        price,
        avg_price,
        fx_impact,
        ROW_NUMBER() OVER (
            PARTITION BY ticker, data_timestamp::DATE
            ORDER BY data_timestamp DESC
        )                                                       AS rn
    FROM staging.asset
),

asset_base AS (
    SELECT
        id,
        ticker,
        snapshot_id,
        data_timestamp,
        value,
        cost,
        profit,
        price,
        avg_price,
        fx_impact,
        (value - LAG(value) OVER (PARTITION BY ticker ORDER BY data_timestamp))
        / NULLIF(
            LAG(value) OVER (PARTITION BY ticker ORDER BY data_timestamp),
            0
        )                                                       AS daily_return
    FROM asset_daily
    WHERE rn = 1
),

asset_stats AS (
    SELECT
        *,

        EXP(SUM(LN(1 + COALESCE(daily_return, 0))) OVER (
            PARTITION BY ticker
            ORDER BY data_timestamp
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        )) - 1                                                  AS cumulative_return,

        AVG(value) OVER (
            PARTITION BY ticker ORDER BY data_timestamp
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        )                                                       AS value_ma_20d,
        AVG(value) OVER (
            PARTITION BY ticker ORDER BY data_timestamp
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        )                                                       AS value_ma_30d,
        AVG(value) OVER (
            PARTITION BY ticker ORDER BY data_timestamp
            ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
        )                                                       AS value_ma_50d,

        AVG(price) OVER (
            PARTITION BY ticker ORDER BY data_timestamp
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        )                                                       AS price_ma_20d,
        AVG(price) OVER (
            PARTITION BY ticker ORDER BY data_timestamp
            ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
        )                                                       AS price_ma_50d,

        STDDEV(daily_return) OVER (
            PARTITION BY ticker ORDER BY data_timestamp
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        )                                                       AS volatility_20d,
        STDDEV(daily_return) OVER (
            PARTITION BY ticker ORDER BY data_timestamp
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        )                                                       AS volatility_30d,
        STDDEV(daily_return) OVER (
            PARTITION BY ticker ORDER BY data_timestamp
            ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
        )                                                       AS volatility_50d,

        MAX(value) OVER (
            PARTITION BY ticker ORDER BY data_timestamp
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        )                                                       AS recent_value_high_30d,
        MIN(value) OVER (
            PARTITION BY ticker ORDER BY data_timestamp
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        )                                                       AS recent_value_low_30d,
        MAX(profit) OVER (
            PARTITION BY ticker ORDER BY data_timestamp
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        )                                                       AS recent_profit_high_30d,
        MIN(profit) OVER (
            PARTITION BY ticker ORDER BY data_timestamp
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        )                                                       AS recent_profit_low_30d,

        MAX(value) OVER (PARTITION BY ticker)                   AS value_high_alltime,
        MIN(value) OVER (PARTITION BY ticker)                   AS value_low_alltime
    FROM asset_base
),

asset_latest AS (
    SELECT
        1                                                       AS rn,
        *
    FROM asset_stats
),

account_ranked AS (
    SELECT
        *,
        LAG(total_value) OVER (
            ORDER BY data_timestamp
        )                                                       AS prev_total_value
    FROM staging.account
),

portfolio_agg AS (
    SELECT
        al.snapshot_id,
        SUM(al.fx_impact)                                       AS fx_impact_total,
        SUM(
            al.value / NULLIF(acc.total_value, 0)
            * COALESCE(al.volatility_30d, 0)
        )                                                       AS portfolio_volatility_weighted
    FROM asset_latest al
    JOIN account_ranked acc ON acc.snapshot_id = al.snapshot_id
    WHERE al.rn = 1
    GROUP BY al.snapshot_id
)

SELECT
    TO_CHAR(a.data_timestamp, 'YYYYMMDD')::INTEGER              AS date_id,
    dp.id                                                        AS portfolio_id,
    da.asset_id,

    -- fact_price
    a.price,
    a.avg_price,

    -- fact_valuation
    a.value,
    a.cost                                                       AS cost_basis,
    a.profit                                                     AS unrealized_pnl,
    a.profit / NULLIF(a.cost, 0) * 100                          AS unrealized_pnl_pct,
    NULL::FLOAT                                                  AS realized_pnl,
    a.value / NULLIF(acc.total_value, 0) * 100                  AS position_weight_pct,
    a.fx_impact,

    -- fact_return
    COALESCE(a.daily_return, 0)                                 AS daily_value_return,
    COALESCE(a.cumulative_return, 0)                            AS cumulative_value_return,

    -- fact_technical
    (a.value - a.recent_value_high_30d)
        / NULLIF(a.recent_value_high_30d, 0)                    AS value_drawdown_pct_30d,
    a.value_high_alltime,
    a.value_low_alltime,
    a.value_ma_20d,
    a.value_ma_30d,
    a.value_ma_50d,
    a.price_ma_20d,
    a.price_ma_50d,
    a.volatility_20d,
    a.volatility_30d,
    a.volatility_50d,
    COALESCE(a.volatility_30d, 0) * a.value * 1.65              AS var_95_1d,
    COALESCE(a.recent_profit_high_30d, 0)
        - COALESCE(a.recent_profit_low_30d, 0)                  AS profit_range_30d,
    a.recent_profit_high_30d,
    a.recent_profit_low_30d,
    a.recent_value_high_30d,
    a.recent_value_low_30d,

    -- fact_signal
    a.price / NULLIF(a.avg_price, 0)                            AS dca_bias,
    a.value_ma_20d - a.value_ma_50d                             AS value_ma_crossover_signal,
    (a.price > a.price_ma_20d)                                  AS price_above_ma_20d,
    (a.price > a.price_ma_50d)                                  AS price_above_ma_50d,

    -- fact_portfolio_daily (prefixed to avoid conflict with asset columns above)
    acc.total_value                                              AS acct_total_value,
    acc.investments_total_cost                                   AS acct_total_cost,
    acc.investments_unrealized_pnl                               AS acct_unrealized_pnl,
    acc.investments_unrealized_pnl
        / NULLIF(acc.investments_total_cost, 0) * 100           AS acct_unrealized_pnl_pct,
    acc.investments_realized_pnl                                 AS acct_realized_pnl,
    acc.total_value
        - COALESCE(acc.prev_total_value, acc.total_value)       AS daily_value_change_abs,
    (acc.total_value - COALESCE(acc.prev_total_value, acc.total_value))
        / NULLIF(acc.prev_total_value, 0) * 100                 AS daily_value_change_pct,
    acc.cash_available_to_trade                                  AS cash_available,
    acc.cash_reserved_for_orders                                 AS cash_reserved,
    acc.cash_in_pies,
    (acc.total_value - acc.cash_available_to_trade)
        / NULLIF(acc.total_value, 0) * 100                      AS cash_deployment_ratio,
    pa.fx_impact_total,
    pa.portfolio_volatility_weighted

FROM asset_latest a
JOIN account_ranked acc ON acc.snapshot_id = a.snapshot_id
JOIN analytics.dim_asset da
    ON da.ticker = a.ticker
CROSS JOIN (
    SELECT id
    FROM analytics.dim_portfolio
    WHERE portfolio_id = :portfolio_id
) dp
LEFT JOIN portfolio_agg pa ON pa.snapshot_id = a.snapshot_id
WHERE a.rn = 1
