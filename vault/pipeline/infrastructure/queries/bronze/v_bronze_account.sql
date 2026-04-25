CREATE VIEW raw.v_bronze_account AS
WITH cte AS (
    SELECT
        account_data->>'id'                                    AS external_id,
        account_data->'cash'->>'inPies'                        AS cash_in_pies,
        account_data->'cash'->>'availableToTrade'              AS cash_available_to_trade,
        account_data->'cash'->>'reservedForOrders'             AS cash_reserved_for_orders,
        account_data->>'currency'                              AS currency,
        (account_data->>'totalValue')::NUMERIC                 AS total_value,
        account_data->'investments'->>'totalCost'              AS investments_total_cost,
        account_data->'investments'->>'realizedProfitLoss'     AS investments_realized_pnl,
        account_data->'investments'->>'unrealizedProfitLoss'   AS investments_unrealized_pnl,
        ingested_date,
        ingested_timestamp
    FROM {table_name}
)
SELECT
    *,
    external_id || '_' || currency || '_' || ingested_timestamp AS business_key
FROM cte
