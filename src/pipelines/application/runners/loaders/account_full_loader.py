import os
import uuid
import json
from typing import Any
from datetime import datetime
from dotenv import load_dotenv
from dataclasses import dataclass

from ....application.policies import FullLoader

from shared.database.client import SQLModelClient

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Partition by date
# Create exposition abstraction - view
# Extract
# Load


@dataclass
class AccountRaw:
    payload: Any
    ingested_date: str
    ingested_timestamp: str


class PostgresAccountFullLoader(FullLoader):

    def __init__(self, table_name):
        super().__init__(table_name)
        self._client = SQLModelClient(DATABASE_URL)

    def _loader(self, data: list[dict]):

        ingested_time = datetime.now().date()
        # for record in data:
        sql = f"""
      INSERT INTO {self._table_name} (
          id
        , payload
        , ingested_date
      )
      VALUES ((:id), (:payload), (:ingested_date))
    """

        params = {
            "id": uuid.uuid4(),
            "payload": json.dumps(data),
            "ingested_date": ingested_time,
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
        drop_sql = "DROP VIEW IF EXISTS raw.v_bronze_account"
        create_sql = f"""
      CREATE VIEW raw.v_bronze_account AS
      WITH cte AS (
          SELECT
              payload->>'id' AS external_id,
              payload->'cash'->>'inPies' AS cash_in_pies,
              payload->'cash'->>'availableToTrade' AS cash_available_to_trade,
              payload->'cash'->>'reservedForOrders' AS cash_reserved_for_orders,
              payload->>'currency' AS currency,
              payload->'totalValue' AS total_value,
              payload->'investments'->>'totalCost' AS investments_total_cost,
              payload->'investments'->>'realizedProfitLoss' AS investments_realized_pnl,
              payload->'investments'->>'unrealizedProfitLoss' AS investments_unrealized_pnl,
              ingested_date,
              ingested_timestamp
          FROM {self._table_name}
      )
      SELECT
          *,
          external_id || '_' || currency || '_' || ingested_timestamp AS business_key
      FROM cte
    """
        from sqlalchemy import text

        with self._client.engine.connect() as conn:
            conn.execute(text(drop_sql))
            conn.execute(text(create_sql))
            conn.commit()
