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



load_dotenv()

URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")



class Trading212AssetComputedSourceSilver(Source):
  def __init__(self):
    self._client = SQLModelClient(DATABASE_URL)
    
  def fetch(self):
    
    # TODO - MOVE AGGREGATION TO PYTHON
    sql = """
            WITH base AS (
            SELECT
                b.id as asset_id,
                b.ticker,
                b.value,
                b.cost,
                b.profit,
                b.fx_impact,
                (b.value - LAG(b.value) OVER (
                    PARTITION BY b.ticker
                    ORDER BY b.created_timestamp
                )) 
                / NULLIF(LAG(b.value) OVER (
                    PARTITION BY b.ticker
                    ORDER BY b.created_timestamp
                ), 0) AS daily_return,
                b.created_timestamp
            FROM staging.asset_v2 b
        ),

        stats AS (
            SELECT
                asset_id,
                value,
                cost,
                profit,
                fx_impact,
                daily_return,

                -- cumulative return
                EXP(SUM(LN(1 + daily_return)) OVER (
                    PARTITION BY ticker
                    ORDER BY created_timestamp
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                )) - 1 AS cumulative_return,

                -- moving averages
                AVG(value) OVER (PARTITION BY ticker ORDER BY created_timestamp ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS ma_20d,
                AVG(value) OVER (PARTITION BY ticker ORDER BY created_timestamp ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS ma_30d,
                AVG(value) OVER (PARTITION BY ticker ORDER BY created_timestamp ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) AS ma_50d,

                -- volatility
                STDDEV(daily_return) OVER (PARTITION BY ticker ORDER BY created_timestamp ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS volatility_20d,
                STDDEV(daily_return) OVER (PARTITION BY ticker ORDER BY created_timestamp ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS volatility_30d,
                STDDEV(daily_return) OVER (PARTITION BY ticker ORDER BY created_timestamp ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) AS volatility_50d,

                -- rolling highs & lows
                MAX(value) OVER (PARTITION BY ticker ORDER BY created_timestamp ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS recent_high_30d,
                MIN(value) OVER (PARTITION BY ticker ORDER BY created_timestamp ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS recent_low_30d,

                -- all-time high / low
                MAX(value) OVER (PARTITION BY ticker) AS high,
                MIN(value) OVER (PARTITION BY ticker) AS low
            FROM base
        )
        SELECT
            s.asset_id,
            cost                                AS cashflow,
            daily_return,
            cumulative_return,

            -- DCA bias: current value vs average cost
            (value - cost) / NULLIF(cost, 0)    AS dca_bias,

            -- drawdown from recent high
            (value - recent_high_30d) / NULLIF(recent_high_30d, 0) AS pct_drawdown,

            recent_high_30d,
            recent_low_30d,
            high,
            low,
            ma_20d,
            ma_30d,
            ma_50d,
            volatility_20d,
            volatility_30d,
            volatility_50d
        FROM stats s
    """
    with self._client as db:
      result = db.execute(sql)
    return result.fetchall()


class Trading212AssetComputedTransformation(Transformation):
  """
    Trading212AssetComputedTransformation:
  """
  _portfolio_snapshot_repository = EntityRepositoryFactory.get_repository("portfolio_snapshot", schema_name="portfolio")
  # FIXME - NEED TO MAP TO DATA CONTRACT
  def transform(self, data: Data) -> list[Dict]:
    """
      transform: 
    """
    record = self._get_raw_data(data)
    data_date = datetime.now(UTC)
    investment = record.get('investments', {})
    transformed_data = {
      "external_id": record.get('id', None),
      "data_date": data_date,
      "currency": record.get('currency', ''),
      "current_value": investment.get('currentValue', 0),
      "total_value": record.get('totalValue', 0),
      "total_cost": record.get('totalCost', 0),
      "unrealized_profit": investment.get('unrealizedProfitLoss', 0),
      "realized_profit": investment.get('realizedProfitLoss', 0),
    }
    return [transformed_data]
  
class Trading212AssetComputedDestination(Destination):
  def __init__(self, repo):
      self._repository = EntityRepositoryFactory.get_repository("asset_computed", schema_name="staging")
  
  def save(self, data: List[Dict]) -> None:
      self._repository.upsert(data=data, unique_key='asset_id')
      
      
class SilverAssetComputedPipeline(Pipeline):
  def __init__(self):
    self._source = Trading212AssetComputedSourceSilver()
    self._transformation = Trading212AssetComputedTransformation()
    self._destination = Trading212AssetComputedDestination()

  def run(self):
    # Fetch raw data from source
    data = self._source.fetch()
    # Copy to prevent mutating object
    try:
      # Apply Transformation Logic
      # FIXME - RENAME apply_to - to transform
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