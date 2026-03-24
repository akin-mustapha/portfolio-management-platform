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
class AssetRaw:
    payload: Any
    ingested_date: str
    ingested_timestamp: str


class PostgresAssetFullLoader(FullLoader):

    def __init__(self, table_name):
        super().__init__(table_name)
        self._client = SQLModelClient(DATABASE_URL)

    def _loader(self, data: list[dict]):

        ingested_time = datetime.now().date()
        for record in data:
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
                "payload": json.dumps(record),
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
        sql = f"""
      CREATE OR REPLACE VIEW raw.v_bronze_asset AS
      WITH cte AS (
          SELECT
              payload->'instrument'->>'ticker' AS ticker,
              payload->'instrument'->>'name' AS instrument_name,
              payload->'instrument'->>'isin' AS isin,
              payload->'instrument'->>'currency' AS instrument_currency,
              (payload->>'createdAt')::TIMESTAMP AS created_at,
              (payload->>'quantity')::NUMERIC AS quantity,
              (payload->>'quantityAvailableForTrading')::NUMERIC AS quantity_available,
              (payload->>'quantityInPies')::NUMERIC AS quantity_in_pies,
              (payload->>'currentPrice')::NUMERIC AS current_price,
              (payload->>'averagePricePaid')::NUMERIC AS average_price_paid,
              (payload->'walletImpact'->>'currency') AS wallet_currency,
              (payload->'walletImpact'->>'totalCost')::NUMERIC AS total_cost,
              (payload->'walletImpact'->>'currentValue')::NUMERIC AS current_value,
              (payload->'walletImpact'->>'unrealizedProfitLoss')::NUMERIC AS unrealized_pnl,
              (payload->'walletImpact'->>'fxImpact')::NUMERIC AS fx_impact,
              id AS external_id,
              ingested_date,
              ingested_timestamp
          FROM {self._table_name}
      )
      SELECT
          *,
          external_id || '_' || ticker || '_' || ingested_timestamp AS business_key
      FROM cte;
    """
        with self._client as client:
            client.execute(sql)
