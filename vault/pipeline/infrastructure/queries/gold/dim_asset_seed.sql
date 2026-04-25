INSERT INTO analytics.dim_asset (asset_id, ticker, name, asset_type, currency)
SELECT DISTINCT ON (ticker)
    id          AS asset_id,
    ticker,
    name,
    'STOCK'     AS asset_type,
    currency
FROM staging.asset
ORDER BY ticker, data_timestamp DESC
ON CONFLICT (ticker) DO NOTHING
