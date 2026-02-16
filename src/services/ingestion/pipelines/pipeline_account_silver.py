
import os
import logging
from dotenv import load_dotenv
from datetime import datetime, UTC
from typing import List, Any, Dict
from dataclasses import dataclass, asdict

import pandas as pd

from src.services.ingestion.app.policies import Pipeline
from src.services.ingestion.app.protocols import Source
from src.services.ingestion.app.protocols import Destination
from src.services.ingestion.app.protocols import Transformation

# TODO: should depend on interface
from src.shared.database.client import SQLModelClient
from src.services.ingestion.infra.repositories.repositories import DatabaseRepositoryFactory

logging.basicConfig(
    level=logging.INFO,
    filename='logs/info.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s'
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


@dataclass
class Account:
  data_timestamp: datetime
  external_id: str
  cash_in_pies: float
  cash_available_to_trade: float
  cash_reserved_for_orders: float
  broker: str
  currency: str
  total_value: float
  investments_total_cost: float
  investments_realized_pnl: float
  investments_unrealized_pnl: float
  business_key: str  
  
class Trading212AccountSourceSilver(Source):
  def __init__(self):
    self._client = SQLModelClient(DATABASE_URL)
    
  def extract(self):
    sql = """
      SELECT
        external_id,
        cash_in_pies,
        cash_available_to_trade,
        cash_reserved_for_orders,
        currency,
        total_value,
        investments_total_cost,
        investments_realized_pnl,
        investments_unrealized_pnl,
        ingested_date,
        ingested_timestamp,
        business_key
      FROM raw.v_bronze_account t1
      WHERE NOT EXISTS (
            SELECT 1
            FROM staging.account x1
            WHERE t1.business_key = x1.business_key
          )
          AND external_id IS NOT NULL
      LIMIT 1000;
    """

    with self._client as db:
      result = db.execute(sql)

    # TODO: Convert result to data
    return result.fetchall()


class Trading212AccountTransformationSilver(Transformation):
  """
    Trading212AccountTransformationSilver
  """
  def transform(self, data: list[Dict]) -> list[Dict]:
    """
      transform
    """
    bronze_account_df = pd.DataFrame(data)
    # REMOVE NULL
    df = bronze_account_df[bronze_account_df["external_id"].notna()]
    
    account_df = pd.DataFrame()
    account_df["external_id"] = df["external_id"]
    account_df["cash_in_pies"] = df["cash_in_pies"]
    account_df["cash_available_to_trade"] = df["cash_available_to_trade"]
    account_df["cash_reserved_for_orders"] = df["cash_reserved_for_orders"]
    account_df["broker"] = "Trading 212"
    account_df["currency"] = df["currency"]
    account_df["total_value"] = df["total_value"]
    account_df["investments_total_cost"] = df["investments_total_cost"]
    account_df["investments_realized_pnl"] = df["investments_realized_pnl"]
    account_df["investments_unrealized_pnl"] = df["investments_unrealized_pnl"]
    account_df["business_key"] = df["business_key"]
    account_df["updated_timestamp"] = datetime.now(UTC)
    
    # Using ingested date as marker to sequential ordering of data
    account_df["data_timestamp"] = df['ingested_timestamp']
    asset_dict = account_df.to_dict("records")
    return asset_dict

class Trading212AccountDestination(Destination):
  def __init__(self):
      # TODO: INJECT DEPENDENCY MAKES TESTING EASIER | ALLOWS TO CHANGE BEHAVIOUR
      self._repository = DatabaseRepositoryFactory.get_repository("account", schema_name="staging")
  
  def load(self, data: List[Dict]) -> None:
      self._repository.upsert(records=data, unique_key=['business_key'])
      

class PipelineAccountSilver(Pipeline):
  def __init__(self):
    self._source = Trading212AccountSourceSilver()
    self._transformation = Trading212AccountTransformationSilver()
    self._destination = Trading212AccountDestination()

  def run(self):
    try:
      
      # Fetch raw data from source
      # Copy to prevent mutating object
      data = self._source.extract()

      if len(data) == 0:
        logging.warning("NO RECORD")
        return
      
      # Apply Transformation Logic
      transformed_data: List[Any] = self._transformation.transform(data)
      
      # Mapping
      data = [
        asdict(
          Account(
          data_timestamp = row.get("data_timestamp"),
          external_id = row.get("external_id"), 
          cash_in_pies = row.get("cash_in_pies"), 
          cash_available_to_trade = row.get("cash_available_to_trade"),
          cash_reserved_for_orders = row.get("cash_reserved_for_orders"), 
          broker = row.get("broker"), 
          currency = row.get("currency"), 
          total_value = row.get("total_value"), 
          investments_total_cost = row.get("investments_total_cost"),
          investments_realized_pnl = row.get("investments_realized_pnl"),
          investments_unrealized_pnl = row.get("investments_unrealized_pnl"),
          business_key = row.get("business_key"),
          )
        )
        
        for row in transformed_data
      ]
      
      # print(data)
      # Save to Destination Table
      self._destination.load(data)
      return None
    except Exception as e:
      # TODO REPLACE WITH ERROR MANAGEMENT 
      # Persist raw data
      # self._sink.save(data)

      raise e
    
    
    
if __name__ == "__main__":
  PipelineAccountSilver().run()