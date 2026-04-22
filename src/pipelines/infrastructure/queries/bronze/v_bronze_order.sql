# TODO: DATA TYPE CONVERSION, FIX TAXES (LIST)
CREATE OR REPLACE VIEW raw.v_bronze_order AS
WITH cte AS (
    SELECT
        payload->'fill'->>'id' as "id",
        payload->'fill'->>'type' as "type",
        payload->'fill'->>'trade' as "trade",
        payload->'fill'->>'price' as "price",
        payload->'fill'->>'at' as "file_at",
        payload->'fill'->>'quantity' as "quantity",
        payload->'fill'->'walletImpact'->'taxes' as "wallet_impact_taxes",
        payload->'fill'->'walletImpact'->'taxes'->>'name' as "wallet_impact_taxes_name",
        payload->'fill'->'walletImpact'->'taxes'->>'currency' as "wallet_impact_taxes_currency",
        payload->'fill'->'walletImpact'->'taxes'->>'quantity' as "wallet_impact_taxes_quantity",
        payload->'fill'->'walletImpact'->'taxes'->>'chargedAt' as "wallet_impact_taxes_charged_at",
        payload->'fill'->'walletImpact'->>'fxRate' as "wallet_impact_fx_rate",
        payload->'fill'->'walletImpact'->>'currency' as "wallet_impact_currency",
        payload->'fill'->'walletImpact'->>'netValue' as "wallet_impact_net_value",
        payload->'fill'->>'tradingMethod' as "trading_method",
        payload->>'order'                        AS order,
        payload->'order'->>'id'                        AS order_id,
        payload->'order'->>'side'                        AS order_side,
        payload->'order'->>'type'                        AS order_type,
        payload->'order'->>'value'                        AS order_value,
        payload->'order'->>'status'                        AS order_status,
        payload->'order'->>'ticker'                        AS order_ticker,
        payload->'order'->>'currency'                        AS order_currency,
        payload->'order'->>'strategy'                        AS order_strategy,
        payload->'order'->>'createdAt'                        AS order_created_at,
        payload->'order'->>'filledValue'                        AS order_filled_value,
        payload->'order'->>'extendedHours'                        AS order_extended_hours,
        payload->'order'->>'initiatedFrom'                        AS order_initiated_from,
        payload->'order'->>'instrument'                        AS order_instrument,
        payload->'order'->'instrument'->>'isin'                        AS order_instrument_isin,
        payload->'order'->'instrument'->>'name'                        AS name,
        payload->'order'->'instrument'->>'ticker'                        AS order_instrument_ticker,
        payload->'order'->'instrument'->>'currency'                        AS order_instrument_currency,
        ingested_date,
        ingested_timestamp
    FROM {table_name}
)
SELECT
    *,
    order_id || '_' || order_ticker || '_' || order_created_at AS business_key
FROM cte
