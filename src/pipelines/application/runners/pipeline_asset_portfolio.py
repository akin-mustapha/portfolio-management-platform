"""
  Asset Portfolio Pipeline

  Sync asset list from silver asset store to OLTP portfolio asset table

  Source -> Destination (no transformation)
"""
import os
import logging
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
from shared.database.client import SQLModelClient

from ...application.protocols import Source, Destination
from ...application.policies import Pipeline

logging.basicConfig(
    level=logging.INFO,
    filename='logs/info.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s'
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


@dataclass
class Asset():
  ticker: str
  name: str
  broker: str
  currency: str


class AssetPortfolioSource(Source):
  def extract(self) -> list:
    sql = """
      SELECT ticker, name, broker, currency
      FROM (
          SELECT *,
                ROW_NUMBER() OVER (
                    PARTITION BY ticker, broker, currency
                    ORDER BY data_timestamp DESC
                ) as rn
          FROM staging.asset
      ) t
      WHERE rn = 1;
    """
    with SQLModelClient(DATABASE_URL) as client:
      res = client.execute(sql)
      return res.fetchall()


class AssetPortfolioDestination(Destination):
  def load(self, data: list[dict]) -> None:
    # INSERTION POLICY: IDEMPOTENT
    merge_value_mapping = ",".join([
        f"""(
            '{r.get('ticker')}'
          , '{r.get('name')}'
          , '{r.get('broker')}'
          , '{r.get('currency')}'
          )
        """
        for r in data
      ])

    destination_table_name = "portfolio.asset"
    asset_upsert_sql = f"""
      MERGE INTO {destination_table_name} AS tgt
      USING
        (
          VALUES
            {merge_value_mapping}
        )
      AS src (ticker, name, broker, currency)
      ON    tgt.ticker = src.ticker
        AND tgt.broker = src.broker
        AND tgt.currency = src.currency
      WHEN NOT MATCHED THEN
        INSERT (ticker, name, broker, currency)
        VALUES (src.ticker, src.name, src.broker, src.currency)
      WHEN MATCHED AND tgt.name <> src.name THEN
      UPDATE
        SET   name = src.name
            , updated_timestamp = NOW()
      WHEN NOT MATCHED BY SOURCE THEN
        UPDATE
          SET to_timestamp = NOW();
    """

    with SQLModelClient(DATABASE_URL) as client:
      client.execute(asset_upsert_sql)


class PipelineAssetPortfolio(Pipeline):
  def __init__(self):
    self._source = AssetPortfolioSource()
    self._destination = AssetPortfolioDestination()

  def run(self):
    try:
      data = self._source.extract()

      # DESTINATION Schema Contract
      # Dataclass creates a boundary between source and destination physical storage
      data = [
        asdict(Asset(
          ticker=row._mapping.get("ticker"),
          name=row._mapping.get("name"),
          broker=row._mapping.get("broker"),
          currency=row._mapping.get("currency"),
        ))
        for row in data
      ]

      self._destination.load(data)
      return None

    except Exception as e:
      raise e


if __name__ == "__main__":
  PipelineAssetPortfolio().run()
