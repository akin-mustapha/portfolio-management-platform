CREATE OR REPLACE VIEW raw.v_bronze_dividend AS
WITH cte AS (
    SELECT
        payload->>'type'                              AS "type",
        (payload->>'amount')::NUMERIC                 AS amount,
        (payload->>'paidOn')::TIMESTAMP               AS paid_on,
        payload->>'ticker'                            AS ticker,
        payload->>'currency'                          AS currency,
        payload->>'reference'                         AS reference,
        (payload->>'quantity')::NUMERIC               AS quantity,
        (payload->>'amountInEuro')::NUMERIC           AS amountineuro,
        (payload->>'grossAmountPerShare')::NUMERIC    AS grossamountpershare,
        payload->'instrument'->>'name'                AS name,
        payload->'instrument'->>'ticker'              AS instrument_ticker,
        payload->'instrument'->>'currency'            AS instrument_currency,
        payload->'instrument'->>'isin'                AS instrument_isin,
        ingested_date,
        ingested_timestamp
    FROM {table_name}
)
SELECT
    *,
    reference AS business_key
FROM cte
