SELECT
    TO_CHAR(am.data_timestamp, 'YYYYMMDD')::INTEGER AS date_id,
    dp.id                                           AS portfolio_id,
    da.asset_id,

    (am.value - am.recent_value_high_30d)
        / NULLIF(am.recent_value_high_30d, 0)       AS value_drawdown_pct_30d,

    am.recent_price_high_7d,
    am.recent_price_low_7d,
    (am.price - am.recent_price_high_7d)
        / NULLIF(am.recent_price_high_7d, 0)        AS price_drawdown_pct_7d,
    am.recent_price_high_14d,
    am.recent_price_low_14d,
    (am.price - am.recent_price_high_14d)
        / NULLIF(am.recent_price_high_14d, 0)       AS price_drawdown_pct_14d,

    (am.price - am.recent_price_high_30d)
        / NULLIF(am.recent_price_high_30d, 0)       AS price_drawdown_pct_30d,
    (am.price - am.recent_price_high_90d)
        / NULLIF(am.recent_price_high_90d, 0)       AS price_drawdown_pct_90d,
    (am.price - am.recent_price_high_180d)
        / NULLIF(am.recent_price_high_180d, 0)      AS price_drawdown_pct_180d,
    (am.price - am.recent_price_high_365d)
        / NULLIF(am.recent_price_high_365d, 0)      AS price_drawdown_pct_365d,

    am.value_high_alltime,
    am.value_low_alltime,
    am.value_ma_20d,
    am.value_ma_30d,
    am.value_ma_50d,
    am.price_ma_20d,
    am.price_ma_50d,
    am.volatility_20d,
    am.volatility_30d,
    am.volatility_50d,
    COALESCE(am.volatility_30d, 0) * am.value * 1.65 AS var_95_1d,
    COALESCE(am.recent_profit_high_30d, 0)
        - COALESCE(am.recent_profit_low_30d, 0)      AS profit_range_30d,
    am.recent_profit_high_30d,
    am.recent_profit_low_30d,
    am.recent_value_high_30d,
    am.recent_value_low_30d,
    am.beta_60d,
    am.sharpe_ratio_30d
FROM staging.v_asset_metrics am
JOIN analytics.dim_asset da
    ON da.ticker = am.ticker
CROSS JOIN (
    SELECT id FROM analytics.dim_portfolio WHERE portfolio_id = :portfolio_id
) dp
