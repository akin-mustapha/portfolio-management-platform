import os
import logging
from dotenv import load_dotenv
from datetime import datetime, UTC
from typing import List, Dict
from pydantic import ValidationError

import pandas as pd

from...application.policies import BaseSilverPipeline
from...application.protocols import Source
from...application.protocols import Destination
from...application.protocols import Transformation

# TODO: should depend on interface
from shared.database.client import SQLModelClient
from...infrastructure.repositories.repository_factory import RepositoryFactory
from...domain.schemas.silver.asset import AssetRecord

logging.basicConfig(
    level=logging.INFO,
    filename='logs/info.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s'
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")



class Trading212AssetSourceSilver(Source):
  def __init__(self):
    self._client = SQLModelClient(DATABASE_URL)

  def extract(self):
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
      WHERE ticker IS NOT NULL;
    """

    with self._client as db:
      result = db.execute(sql)

    # TODO: Convert result to data
    return result.fetchall()


class Trading212AssetTransformationSilver(Transformation):
  """
    Trading212AssetTransformationSilver
  """
  def transform(self, data: list[Dict]) -> list[Dict]:
    """
      transform
    """
    bronze_asset_df = pd.DataFrame(data)
    bronze_asset_df.rename({
      "ticker": "external_id"
    })

    # REMOVE NULL
    df = bronze_asset_df[bronze_asset_df["ticker"].notna()]

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
    asset_dict = asset_df.to_dict("records")
    return asset_dict

class Trading212AssetDestination(Destination):
  def __init__(self):
      # TODO: INJECT DEPENDENCY MAKES TESTING EASIER | ALLOWS TO CHANGE BEHAVIOUR
      self._repository = RepositoryFactory.get("asset", schema_name="staging")

  def load(self, data: List[Dict]) -> None:
      self._repository.upsert(records=data, unique_key=['business_key'])


class PipelineAssetSilver(BaseSilverPipeline):
  def __init__(self):
    self._source = Trading212AssetSourceSilver()
    self._transformation = Trading212AssetTransformationSilver()
    self._destination = Trading212AssetDestination()

  def _to_records(self, transformed_data: list) -> list[dict]:
    valid, invalid = [], []
    for row in transformed_data:
      try:
        valid.append(AssetRecord(**row).model_dump())
      except ValidationError as e:
        invalid.append((row.get("business_key"), e))
    if invalid:
      logging.warning(f"[AssetSilver] {len(invalid)} records failed validation: {invalid}")
    return valid



if __name__ == "__main__":
  PipelineAssetSilver().run()
