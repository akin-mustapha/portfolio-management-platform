WITH fred_rfr AS (
    SELECT
        observation_date,
        value / 100.0 / 252.0                               AS daily_rfr
    FROM staging.fred_observation
    WHERE series_id = 'DTB3'
),

fred_sp500 AS (
    SELECT
        observation_date,
        (value - LAG(value) OVER (ORDER BY observation_date))
            / NULLIF(LAG(value) OVER (ORDER BY observation_date), 0)
                                                            AS sp500_daily_return
    FROM staging.fred_observation
    WHERE series_id = 'SP500'
),

asset_daily AS (
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
        (price - LAG(price) OVER (PARTITION BY ticker ORDER BY data_timestamp))
        / NULLIF(
            LAG(price) OVER (PARTITION BY ticker ORDER BY data_timestamp),
            0
        )                                                       AS daily_return
    FROM asset_daily
    WHERE rn = 1
),

asset_base_with_fred AS (
    SELECT
        ab.*,
        COALESCE(rfr.daily_rfr, 0)                          AS daily_rfr,
        sp.sp500_daily_return
    FROM asset_base ab
    LEFT JOIN fred_rfr rfr  ON rfr.observation_date = ab.data_timestamp::DATE
    LEFT JOIN fred_sp500 sp ON sp.observation_date  = ab.data_timestamp::DATE
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
        MIN(value) OVER (PARTITION BY ticker)                   AS value_low_alltime,

        COVAR_POP(daily_return, sp500_daily_return) OVER (
            PARTITION BY ticker ORDER BY data_timestamp
            ROWS BETWEEN 59 PRECEDING AND CURRENT ROW
        ) / NULLIF(
            VAR_POP(sp500_daily_return) OVER (
                PARTITION BY ticker ORDER BY data_timestamp
                ROWS BETWEEN 59 PRECEDING AND CURRENT ROW
            ), 0
        )                                                       AS beta_60d,

        AVG(daily_return - daily_rfr) OVER (
            PARTITION BY ticker ORDER BY data_timestamp
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) / NULLIF(
            STDDEV_POP(daily_return) OVER (
                PARTITION BY ticker ORDER BY data_timestamp
                ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
            ), 0
        ) * SQRT(252)                                           AS sharpe_ratio_30d
    FROM asset_base_with_fred
),

asset_latest AS (
    SELECT
        1                                                       AS rn,
        *
    FROM asset_stats
),

account_deduped AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY data_timestamp::DATE
            ORDER BY data_timestamp DESC
        )                                                       AS rn
    FROM staging.account
),

account_ranked AS (
    SELECT
        *,
        LAG(total_value) OVER (
            ORDER BY data_timestamp
        )                                                       AS prev_total_value,
        LAG(investments_total_cost + investments_unrealized_pnl) OVER (
            ORDER BY data_timestamp
        )                                                       AS prev_invested_value
    FROM account_deduped
    WHERE rn = 1
),

account_with_fred AS (
    SELECT
        ar.*,
        COALESCE(rfr.daily_rfr, 0)                          AS daily_rfr,
        COALESCE(sp.sp500_daily_return, 0)                  AS sp500_daily_return,
        ((ar.investments_total_cost + ar.investments_unrealized_pnl)
            - COALESCE(
                ar.prev_invested_value,
                ar.investments_total_cost + ar.investments_unrealized_pnl
            ))
            / NULLIF(ar.prev_invested_value, 0)             AS portfolio_daily_return
    FROM account_ranked ar
    LEFT JOIN fred_rfr rfr  ON rfr.observation_date = ar.data_timestamp::DATE
    LEFT JOIN fred_sp500 sp ON sp.observation_date  = ar.data_timestamp::DATE
),

portfolio_metrics AS (
    SELECT
        snapshot_id,
        sp500_daily_return                                   AS benchmark_return_daily,

        AVG(portfolio_daily_return - daily_rfr) OVER (
            ORDER BY data_timestamp
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) / NULLIF(
            STDDEV_POP(portfolio_daily_return) OVER (
                ORDER BY data_timestamp
                ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
            ), 0
        ) * SQRT(252)                                        AS sharpe_ratio_30d,

        (EXP(SUM(LN(1 + COALESCE(portfolio_daily_return, 0))) OVER (
            ORDER BY data_timestamp
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        )) - 1)
        - (EXP(SUM(LN(1 + COALESCE(sp500_daily_return, 0))) OVER (
            ORDER BY data_timestamp
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        )) - 1)                                              AS portfolio_vs_benchmark_30d
    FROM account_with_fred
),

portfolio_agg AS (
    SELECT
        al.snapshot_id,
        SUM(al.fx_impact)                                       AS fx_impact_total,
        SUM(
            al.value / NULLIF(acc.investments_total_cost + acc.investments_unrealized_pnl, 0)
            * COALESCE(al.volatility_30d, 0)
        )                                                       AS portfolio_volatility_weighted,
        SUM(
            al.value / NULLIF(acc.investments_total_cost + acc.investments_unrealized_pnl, 0)
            * COALESCE(al.beta_60d, 0)
        )                                                       AS portfolio_beta_weighted
    FROM asset_latest al
    JOIN account_with_fred acc ON acc.snapshot_id = al.snapshot_id
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
    a.value / NULLIF(acc.investments_total_cost + acc.investments_unrealized_pnl, 0) * 100
                                                                 AS position_weight_pct,
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

    -- fact_technical (FRED)
    a.beta_60d,
    a.sharpe_ratio_30d,

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
    (acc.investments_total_cost + acc.investments_unrealized_pnl)
        - COALESCE(
            acc.prev_invested_value,
            acc.investments_total_cost + acc.investments_unrealized_pnl
        )                                                       AS daily_value_change_abs,
    ((acc.investments_total_cost + acc.investments_unrealized_pnl)
        - COALESCE(
            acc.prev_invested_value,
            acc.investments_total_cost + acc.investments_unrealized_pnl
        ))
        / NULLIF(acc.prev_invested_value, 0) * 100              AS daily_value_change_pct,
    acc.cash_available_to_trade                                  AS cash_available,
    acc.cash_reserved_for_orders                                 AS cash_reserved,
    acc.cash_in_pies,
    (acc.total_value - acc.cash_available_to_trade)
        / NULLIF(acc.total_value, 0) * 100                      AS cash_deployment_ratio,
    pa.fx_impact_total,
    pa.portfolio_volatility_weighted,
    pa.portfolio_beta_weighted,

    -- fact_portfolio_daily (FRED)
    pm.sharpe_ratio_30d                                      AS acct_sharpe_ratio_30d,
    pm.benchmark_return_daily                                 AS acct_benchmark_return_daily,
    pm.portfolio_vs_benchmark_30d                             AS acct_portfolio_vs_benchmark_30d

FROM asset_latest a
JOIN account_with_fred acc ON acc.snapshot_id = a.snapshot_id
JOIN analytics.dim_asset da
    ON da.ticker = a.ticker
CROSS JOIN (
    SELECT id
    FROM analytics.dim_portfolio
    WHERE portfolio_id = :portfolio_id
) dp
LEFT JOIN portfolio_agg pa ON pa.snapshot_id = a.snapshot_id
LEFT JOIN portfolio_metrics pm ON pm.snapshot_id = a.snapshot_id
WHERE a.rn = 1
