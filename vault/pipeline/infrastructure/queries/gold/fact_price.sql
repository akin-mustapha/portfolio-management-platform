SELECT
    TO_CHAR(am.data_timestamp, 'YYYYMMDD')::INTEGER AS date_id,
    dp.id                                           AS portfolio_id,
    da.asset_id,
    am.price,
    am.avg_price
FROM staging.v_asset_metrics am
JOIN analytics.dim_asset da
    ON da.ticker = am.ticker
CROSS JOIN (
    SELECT id FROM analytics.dim_portfolio WHERE portfolio_id = :portfolio_id
) dp
