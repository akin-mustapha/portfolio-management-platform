INSERT INTO analytics.dim_portfolio (portfolio_id, name, base_currency)
SELECT DISTINCT ON (external_id)
    external_id AS portfolio_id,
    broker      AS name,
    currency    AS base_currency
FROM staging.account
ORDER BY external_id, data_timestamp DESC
ON CONFLICT (portfolio_id) DO NOTHING
