CREATE OR REPLACE VIEW raw.v_bronze_dividend AS
WITH cte AS (
    SELECT
        payload->>'type' as "type",
        (payload->>'amount')::NUMERIC AS amount,
        (payload->>'paidOn')::TIMESTAMP              AS paid_on,
        payload->>'ticker'             AS ticker,
        payload->>'currency'       AS currency,
        payload->>'reference'       AS reference,
        (payload->>'quantity')::NUMERIC                 AS quantity,
        (payload->>'amountInEuro')::NUMERIC                 AS amountInEuro,
        (payload->>'grossAmountPerShare')::NUMERIC                 AS grossAmountPerShare,
        payload->'instrument'->>'name' AS name,
        payload->'instrument'->>'ticker' AS instrument_ticker,
        payload->'instrument'->>'currency' AS instrument_currency,
        payload->'instrument'->>'isin' AS instrument_isin,
        ingested_date,
        ingested_timestamp
    FROM {table_name}
)
SELECT
    *,
    "ticker" || '_' || currency || '_' || ingested_timestamp AS business_key
FROM cte
