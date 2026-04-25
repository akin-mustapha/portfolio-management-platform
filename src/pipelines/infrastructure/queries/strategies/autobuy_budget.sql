-- name: get_budget
-- Returns spent amount for the given month, or NULL if no row exists.
SELECT spent
FROM portfolio.autobuy_budget
WHERE month = :month;

-- name: upsert_budget
-- Insert or update the monthly spend total.
INSERT INTO portfolio.autobuy_budget (month, spent, updated_at)
VALUES (:month, :spent, now())
ON CONFLICT (month)
DO UPDATE SET
    spent      = EXCLUDED.spent,
    updated_at = now();

-- name: get_drawdown
-- Latest 14-day price drawdown for each requested ticker from the gold layer.
SELECT DISTINCT ON (da.ticker)
    da.ticker,
    ft.price_drawdown_pct_14d
FROM analytics.fact_technical ft
JOIN analytics.dim_asset da ON da.asset_id = ft.asset_id
JOIN analytics.dim_date  dd ON dd.id       = ft.date_id
WHERE da.ticker = ANY(:tickers)
ORDER BY da.ticker, dd.full_date DESC;

-- name: get_cash
-- Most recent available cash from staging.account.
SELECT cash_available_to_trade
FROM staging.account
ORDER BY data_timestamp DESC
LIMIT 1;
