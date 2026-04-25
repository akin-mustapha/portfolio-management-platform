CREATE OR REPLACE VIEW raw.v_bronze_position AS
WITH cte AS (
    SELECT
        t.id                                                           AS snapshot_id,
        t.ingested_date,
        t.ingested_timestamp,
        pos->'instrument'->>'ticker'                                   AS ticker,
        pos->'instrument'->>'name'                                     AS instrument_name,
        pos->'instrument'->>'isin'                                     AS isin,
        pos->'instrument'->>'currency'                                 AS instrument_currency,
        (pos->>'createdAt')::TIMESTAMP                                 AS created_at,
        (pos->>'quantity')::NUMERIC                                    AS quantity,
        (pos->>'quantityAvailableForTrading')::NUMERIC                 AS quantity_available,
        (pos->>'quantityInPies')::NUMERIC                              AS quantity_in_pies,
        (pos->>'currentPrice')::NUMERIC                                AS current_price,
        (pos->>'averagePricePaid')::NUMERIC                            AS average_price_paid,
        pos->'walletImpact'->>'currency'                               AS wallet_currency,
        (pos->'walletImpact'->>'totalCost')::NUMERIC                   AS total_cost,
        (pos->'walletImpact'->>'currentValue')::NUMERIC                AS current_value,
        (pos->'walletImpact'->>'unrealizedProfitLoss')::NUMERIC        AS unrealized_pnl,
        (pos->'walletImpact'->>'fxImpact')::NUMERIC                    AS fx_impact
    FROM {table_name} t,
         jsonb_array_elements(
             CASE WHEN jsonb_typeof(t.position_data) = 'array'
                  THEN t.position_data
                  ELSE '[]'::jsonb
             END
         ) AS pos
)
SELECT
    *,
    snapshot_id || '_' || ticker || '_' || ingested_timestamp AS business_key
FROM cte
