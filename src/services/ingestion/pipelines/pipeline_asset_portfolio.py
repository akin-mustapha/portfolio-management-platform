"""
  Component
  
  Sync asset list from silver asset store to OLTP portfolio asset table
  
  Extract
  Load
"""
import os
import logging
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
from src.shared.database.client import SQLModelClient

logging.basicConfig(
    level=logging.INFO,
    filename='logs/info.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s'
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite").lower()


@dataclass
class Asset():
  ticker: str
  name: str
  broker: str
  currency: str
  
  
def extract():
  sql = """
    SELECT ticker, name, broker, currency
    FROM (
        SELECT *,
              ROW_NUMBER() OVER (
                  PARTITION BY ticker, broker, currency
                  ORDER BY data_timestamp DESC
              ) as rn
        FROM staging.asset_v2
    ) t
    WHERE rn = 1;
  """
  
  # Source
  try:
    with SQLModelClient(DATABASE_URL) as client:
      res = client.execute(sql)
      data: list = res.fetchall()
  except Exception as e:
    raise e
  
  return data


def load(data):
  # INSERTION POLICY
  # IDEMPOTENT
  merge_value_mapping =  ",".join([
      f"""(
          '{r.get('ticker')}'
        , '{r.get('name')}'
        , '{r.get('broker')}'
        , '{r.get('currency')}'
        )
      """
      for r in data
    ])
  
  asset_upsert_sql = f"""
    MERGE INTO portfolio.asset_v2 AS tgt
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
  
  # Destination
  with SQLModelClient(DATABASE_URL) as client:
    client.execute(asset_upsert_sql)

class PipelineAssetPortfolio:
  @classmethod
  def run(self):  
    data = extract()
    
    # DESTINATION Schema Contract
    # Also response can be converted to a dict, this layer exist to 
    # create a boundary between the source and destination physical storage
    data = [
      asdict(Asset(
        ticker = row._mapping.get("ticker"),
        name = row._mapping.get("name"),
        broker = row._mapping.get("broker"),
        currency = row._mapping.get("currency"),
        )
      )
      
      for row in data
    ]
    
    load(data)
  
if __name__ == "__main__":
  PipelineAssetPortfolio.run()