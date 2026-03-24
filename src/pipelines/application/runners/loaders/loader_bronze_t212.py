import os
import uuid
import json
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import text

from ....application.policies import FullLoader

from shared.database.client import SQLModelClient

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Partition by date
# Create exposition abstraction - view
# Extract
# Load


class FullLoaderPostgresT212(FullLoader):

    def __init__(self, table_name):
        super().__init__(table_name)
        self._client = SQLModelClient(DATABASE_URL)

    def _loader(self, data: list[dict]):
        ingested_time = datetime.now().date()
        # for record in data:
        sql = f"""
      INSERT INTO {self._table_name} (
          id
        , ingested_date
        , account_data
        , position_data
      )
      VALUES ((:id), (:ingested_date), (:account_data), (:position_data))
    """

        params = {
            "id": str(uuid.uuid4()),
            "ingested_date": ingested_time,
            "account_data": json.dumps(data.get("account_data", {})),
            "position_data": json.dumps(data.get("position_data", [])),
        }

        with self._client as client:
            client.execute(sql, params=params)

    def _create_partition(self):
        sql = f"""
      CREATE TABLE IF NOT EXISTS {self._partition_name}
      PARTITION OF {self._table_name}
      FOR VALUES FROM (:day) TO (:next_day);
    """

        with self._client as client:
            client.execute(sql, {"day": self._day, "next_day": self._next_day})

        return None

    def _exposition_abstraction(self):
        drop_account = "DROP VIEW IF EXISTS raw.v_bronze_account"
        create_account = f"""
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
          FROM {self._table_name}
      )
      SELECT
          *,
          external_id || '_' || currency || '_' || ingested_timestamp AS business_key
      FROM cte
    """

        drop_position = "DROP VIEW IF EXISTS raw.v_bronze_position"
        create_position = f"""
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
          FROM {self._table_name} t,
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
    """
        with self._client.engine.connect() as conn:
            conn.execute(text(drop_account))
            conn.execute(text(create_account))
            conn.execute(text(drop_position))
            conn.execute(text(create_position))
            conn.commit()
