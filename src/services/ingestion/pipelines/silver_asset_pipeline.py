import os
import asyncio
from dotenv import load_dotenv
import logging
from typing import List, Any, Dict
from dataclasses import replace
from datetime import datetime, UTC
from src.services.ingestion.app.policies import Pipeline, Data
from src.services.ingestion.app.interfaces import Source
from src.services.ingestion.app.interfaces import Destination
from src.services.ingestion.app.interfaces import Transformation

# TODO: should depend on interface
from src.shared.database.client import SQLModelClient
from src.services.ingestion.infra.database.database_client import EntityRepositoryFactory


logging.basicConfig(level="INFO")

DATABASE_URL = os.getenv("DATABASE_URL")

class Trading212AssetSourceSilver(Source):
  def __init__(self):
    self._client = SQLModelClient(DATABASE_URL)
    
  def fetch(self):
    sql = """
      SELECT
        ticker,
        instrument_name,
        isin,
        instrument_currency,
        created_at,
        quantity,
        quantity_available,
        quantity_in_pies,
        current_price,
        average_price_paid,
        wallet_currency,
        total_cost,
        current_value,
        unrealized_pnl,
        fx_impact,
        ingested_date,
        ingested_timestamp,
        business_key
      FROM raw.v_bronze_asset t1
      WHERE NOT EXISTS (
            SELECT 1
            FROM staging.asset_v2 x1
            WHERE t1.business_key = x1.business_key
          )
      LIMIT 1000;
    """

    with self._client as db:
      result = db.execute(sql)

    # TODO: Convert result to data
    return result.fetchall()


class Trading212AssetTransformationSilver(Transformation):
  """
    Trading212AssetTransformationSilver
  """
  def transform(self, data: Data) -> list[Dict]:
    """
      transform
    """
    bronze_asset_df = pd.DataFrame(data)
    df.rename({
      "ticker": "external_id"
    })
    df = df
    df = df[df["ticker"].notna()]
    
    asset_df = pd.DataFrame()
    asset_df["external_id"] = df["ticker"]
    asset_df["ticker"] = df["ticker"].apply(lambda x: x.split("_")[0])
    asset_df["name"] = df["instrument_name"]
    asset_df["description"] = df["instrument_name"]
    asset_df["broker"] = "Trading 212"
    asset_df["currency"] = df["instrument_currency"]
    asset_df["local_currency"] = df["wallet_currency"]
    asset_df["share"] = df["quantity"]
    asset_df["price"] = df["current_price"]
    asset_df["avg_price"] = df["average_price_paid"]
    asset_df["value"] = df["current_value"]
    asset_df["cost"] = df["total_cost"]
    asset_df["profit"] = df["unrealized_pnl"]
    asset_df["fx_impact"] = df["fx_impact"]
    asset_df["business_key"] = df["business_key"]
    asset_df["updated_timestamp"] = datetime.now(UTC)
    
    # Using ingested date as marker to sequential ordering of data
    asset_df["data_timestamp"] = df['ingested_timestamp']
    
    
    return asset_df

class Trading212AssetDestination(Destination):
  def __init__(self, repo):
      self._repository = EntityRepositoryFactory.get_repository("asset", schema_name="staging")
  
  def save(self, data: List[Dict]) -> None:
      self._repository.upsert(data=data, unique_key='asset_id')
      

class SilverAssetPipeline(Pipeline):
  def __init__(self):
    self._source = Trading212AssetSourceSilver()
    self._transformation = Trading212AssetTransformationSilver()
    self._destination = Trading212AssetDestination()

  def run(self):
    # Fetch raw data from source
    data = self._source.fetch()
    # Copy to prevent mutating object
    try:
      # Apply Transformation Logic
      transformed_data: List[Any] = self._transformation.apply_to(data)
      
      # Save to Destination Table
      self._destination.save(transformed_data)
      return None
    
    except Exception as e:
      # Update raw data
      data = replace(data, is_processed=False)
      
      # TODO REPLACE WITH ERROR MANAGEMENT 
      # Persist raw data
      # self._sink.save(data)

      raise e