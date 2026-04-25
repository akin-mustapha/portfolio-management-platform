SELECT
    TO_CHAR(am.data_timestamp, 'YYYYMMDD')::INTEGER AS date_id,
    dp.id                                           AS portfolio_id,
    da.asset_id,
    ds.id                                           AS sector_id,
    am.value,
    am.cost                                         AS cost_basis,
    am.profit                                       AS unrealized_pnl,
    am.profit / NULLIF(am.cost, 0) * 100            AS unrealized_pnl_pct,
    NULL::FLOAT                                     AS realized_pnl,
    am.value
        / NULLIF(
            acc.investments_total_cost + acc.investments_unrealized_pnl,
            0
        ) * 100                                     AS position_weight_pct,
    am.fx_impact
FROM staging.v_asset_metrics am
JOIN staging.v_account_metrics acc
    ON acc.snapshot_id = am.snapshot_id
JOIN analytics.dim_asset da
    ON da.ticker = am.ticker
LEFT JOIN (
    SELECT DISTINCT ON (ticker) ticker, sector_id
    FROM staging.asset
    WHERE sector_id IS NOT NULL
    ORDER BY ticker, data_timestamp DESC
) sa ON LOWER(sa.ticker) = LOWER(am.ticker)
LEFT JOIN analytics.dim_sector ds
    ON ds.id = sa.sector_id
CROSS JOIN (
    SELECT id FROM analytics.dim_portfolio WHERE portfolio_id = :portfolio_id
) dp
