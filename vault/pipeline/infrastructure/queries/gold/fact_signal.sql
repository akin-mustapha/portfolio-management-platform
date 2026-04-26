SELECT
    TO_CHAR(am.data_timestamp, 'YYYYMMDD')::INTEGER AS date_id,
    dp.id                                           AS portfolio_id,
    da.asset_id,

    -- TODO: Compare old dca formula with new one and evaluate which is better
    -- df['dca_bias'] = (
    --     -0.5 * df['pct_drawdown']
    --     -0.4 * df['price_vs_ma_50']
    --     +0.1 * df['volatility_30d']
    -- )
    am.price / NULLIF(am.avg_price, 0)              AS dca_bias,
    am.value_ma_20d - am.value_ma_50d               AS value_ma_crossover_signal,
    (am.price > am.price_ma_20d)                    AS price_above_ma_20d,
    (am.price > am.price_ma_50d)                    AS price_above_ma_50d
FROM staging.v_asset_metrics am
JOIN analytics.dim_asset da
    ON da.ticker = am.ticker
CROSS JOIN (
    SELECT id FROM analytics.dim_portfolio WHERE portfolio_id = :portfolio_id
) dp
