CREATE OR REPLACE VIEW raw.v_bronze_order AS
WITH cte AS (
    SELECT
        payload->'fill'->>'id'                                              AS "id",
        payload->'fill'->>'type'                                            AS "type",
        (payload->'fill'->>'price')::NUMERIC                                AS price,
        (payload->'fill'->>'filledAt')::TIMESTAMPTZ                         AS filled_at,
        (payload->'fill'->>'quantity')::NUMERIC                             AS quantity,
        payload->'fill'->'walletImpact'->'taxes'                            AS wallet_impact_taxes,
        payload->'fill'->'walletImpact'->'taxes'->0->>'name'                AS wallet_impact_taxes_name,
        payload->'fill'->'walletImpact'->'taxes'->0->>'currency'            AS wallet_impact_taxes_currency,
        (payload->'fill'->'walletImpact'->'taxes'->0->>'quantity')::NUMERIC AS wallet_impact_taxes_quantity,
        (payload->'fill'->'walletImpact'->'taxes'->0->>'chargedAt')::TIMESTAMPTZ
                                                                            AS wallet_impact_taxes_charged_at,
        (payload->'fill'->'walletImpact'->>'fxRate')::NUMERIC               AS wallet_impact_fx_rate,
        payload->'fill'->'walletImpact'->>'currency'                        AS wallet_impact_currency,
        (payload->'fill'->'walletImpact'->>'netValue')::NUMERIC             AS wallet_impact_net_value,
        payload->'fill'->>'tradingMethod'                                   AS trading_method,
        payload->'order'->>'id'                                             AS order_id,
        payload->'order'->>'side'                                           AS order_side,
        payload->'order'->>'type'                                           AS order_type,
        (payload->'order'->>'value')::NUMERIC                               AS order_value,
        payload->'order'->>'status'                                         AS order_status,
        payload->'order'->>'ticker'                                         AS order_ticker,
        payload->'order'->>'currency'                                       AS order_currency,
        payload->'order'->>'strategy'                                       AS order_strategy,
        (payload->'order'->>'createdAt')::TIMESTAMPTZ                       AS order_created_at,
        (payload->'order'->>'filledValue')::NUMERIC                         AS order_filled_value,
        (payload->'order'->>'extendedHours')::BOOLEAN                       AS order_extended_hours,
        payload->'order'->>'initiatedFrom'                                  AS order_initiated_from,
        payload->'order'->'instrument'->>'isin'                             AS order_instrument_isin,
        payload->'order'->'instrument'->>'name'                             AS order_instrument_name,
        payload->'order'->'instrument'->>'ticker'                           AS order_instrument_ticker,
        payload->'order'->'instrument'->>'currency'                         AS order_instrument_currency,
        ingested_date,
        ingested_timestamp
    FROM {table_name}
)
SELECT
    *,
    "id" AS business_key
FROM cte
