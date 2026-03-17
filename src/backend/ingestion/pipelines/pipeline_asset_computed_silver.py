import os
import logging
from dotenv import load_dotenv
from typing import List, Any, Dict
from dataclasses import replace, dataclass, asdict

from ..app.protocols import Source
from ..app.policies import Pipeline
from ..app.protocols import Destination
from ..app.protocols import Transformation

# TODO: should depend on interface
from shared.database.client import SQLModelClient
from ..infra.repositories.repository_factory import RepositoryFactory

logging.basicConfig(
    level=logging.INFO,
    filename='logs/info.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s'
)

load_dotenv()

URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")


@dataclass
class AssetComputed:
  asset_id: str
  cashflow: float
  daily_return: float
  cumulative_return: float
  dca_bias: float
  pct_drawdown: float
  recent_value_high_30d: float
  recent_value_low_30d: float
  recent_profit_high_30d: float
  recent_profit_low_30d: float
  value_high: float
  value_low: float
  ma_20d: float
  ma_30d: float
  ma_50d: float
  volatility_20d: float
  volatility_30d: float
  volatility_50d: float


class Trading212AssetComputedSourceSilver(Source):
  def __init__(self):
    self._client = SQLModelClient(DATABASE_URL)
    
  def extract(self):
    # TODO - MOVE AGGREGATION TO PYTHON
    table_name = 'staging.asset'
    sql = f"""
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
            FROM {table_name} b
        ),

        stats AS (
            SELECT
                asset_id,
                value,
                
                -- rolling highs & lows
                MAX(value) OVER (PARTITION BY ticker ORDER BY created_timestamp ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS recent_value_high_30d,
                MIN(value) OVER (PARTITION BY ticker ORDER BY created_timestamp ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS recent_value_low_30d,
                
                cost,
                profit,
                
                -- TODO: EXPOSE
                MAX(profit) OVER (PARTITION BY ticker ORDER BY created_timestamp ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS recent_profit_high_30d,
                MIN(profit) OVER (PARTITION BY ticker ORDER BY created_timestamp ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS recent_profit_low_30d,
                
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

                -- all-time high / low
                MAX(value) OVER (PARTITION BY ticker) AS value_high,
                MIN(value) OVER (PARTITION BY ticker) AS value_low
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
            (value - recent_value_high_30d) / NULLIF(recent_value_high_30d, 0) AS pct_drawdown,
            recent_profit_high_30d,
            recent_profit_low_30d,
            value_high,
            value_low,
            recent_value_high_30d,
            recent_value_low_30d,
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
  # FIXME - COMPUTATION HERE
  def transform(self, data: list[Dict]) -> list[AssetComputed]:
    """
      transform: 
    """
    transformed_data = []
    for record in data:
      record = dict(record._mapping)
      rget = record.get
      transformed_data.append(
        AssetComputed(
          asset_id=rget("asset_id"),
          cashflow=0 if (value := rget("cashflow")) is None else value,
          daily_return=0 if (value := rget("daily_return")) is None else value,
          cumulative_return=0 if (value := rget("cumulative_return")) is None else value,
          dca_bias=0 if (value := rget("dca_bias")) is None else value,
          pct_drawdown=0 if (value := rget("pct_drawdown")) is None else value,
          recent_value_high_30d=0 if (value := rget("recent_value_high_30d")) is None else value,
          recent_value_low_30d=0 if (value := rget("recent_value_low_30d")) is None else value,
          recent_profit_high_30d=0 if (value := rget("recent_profit_high_30d")) is None else value,
          recent_profit_low_30d=0 if (value := rget("recent_profit_low_30d")) is None else value,
          value_high=0 if (value := rget("value_high")) is None else value,
          value_low=0 if (value := rget("value_low")) is None else value,
          ma_20d=0 if (value := rget("ma_20d")) is None else value,
          ma_30d=0 if (value := rget("ma_30d")) is None else value,
          ma_50d=0 if (value := rget("ma_50d")) is None else value,
          volatility_20d=0 if (value := rget("volatility_20d")) is None else value,
          volatility_30d=0 if (value := rget("volatility_30d")) is None else value,
          volatility_50d=0 if (value := rget("volatility_50d")) is None else value,
        )
      )
    return transformed_data
  
class Trading212AssetComputedDestination(Destination):
  def __init__(self):
      self._repository = RepositoryFactory.get("asset_computed", schema_name="staging")
  
  def load(self, data: List[Dict]) -> None:
      self._repository.upsert(records=data, unique_key=['asset_id'])

      
class PipelineAssetComputedSilver(Pipeline):
  def __init__(self):
    self._source = Trading212AssetComputedSourceSilver()
    self._transformation = Trading212AssetComputedTransformation()
    self._destination = Trading212AssetComputedDestination()

  def run(self):
    # Fetch raw data from source
    data = self._source.extract()
    # Copy to prevent mutating object
    
    try:
      # Apply Transformation Logic
      transformed_data: List[Any] = self._transformation.transform(data)

      # Mapping
      data = [
        asdict(
          row
        )
        for row in transformed_data
      ]
      
      # Save to Destination Table
      self._destination.load(data)
      return None
    
    except Exception as e:
      # Update raw data
      # data = replace(data, is_processed=False)
      
      # TODO REPLACE WITH ERROR MANAGEMENT 
      # Persist raw data
      # self._sink.save(data)

      raise e
    
    
if __name__ == "__main__":
  PipelineAssetComputedSilver().run()
