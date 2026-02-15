import os
import logging
from dotenv import load_dotenv
from typing import List, Any, Dict
from dataclasses import replace, dataclass, asdict

from src.services.ingestion.app.protocols import Source
from src.services.ingestion.app.policies import Pipeline
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
  recent_high_30d: float
  recent_low_30d: float
  high: float
  low: float
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
  # FIXME - COMPUTATION HERE
  def transform(self, data: list[Dict]) -> list[Dict]:
    """
      transform: 
    """
    transformed_data = []
    for record in data:
      record = dict(record._mapping)
      transformed_data.append(
        {
          # TODO: IS NULL REALLY ZERO? - 
          "asset_id": record.get("asset_id"),
          "cashflow": record.get("cashflow", 0),
          "daily_return": record.get("daily_return", 0),
          "cumulative_return": record.get("cumulative_return", 0),
          "dca_bias": record.get("dca_bias", 0),
          "pct_drawdown": record.get("pct_drawdown", 0),
          "recent_high_30d": record.get("recent_high_30d", 0),
          "recent_low_30d": record.get("recent_low_30d", 0),
          "high": record.get("high", 0),
          "low": record.get("low", 0),
          "ma_20d": record.get("ma_20d", 0),
          "ma_30d": record.get("ma_30d", 0),
          "ma_50d": record.get("ma_50d", 0),
          "volatility_20d": record.get("volatility_20d", 0),
          "volatility_30d": record.get("volatility_30d", 0),
          "volatility_50d": record.get("volatility_50d", 0),
        }
      )
    return transformed_data
  
class Trading212AssetComputedDestination(Destination):
  def __init__(self):
      self._repository = DatabaseRepositoryFactory.get_repository("asset_computed", schema_name="staging")
  
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
          AssetComputed(
            asset_id = row.get("asset_id"),
            cashflow = row.get("cashflow", 0),
            daily_return = row.get("daily_return", 0),
            cumulative_return = row.get("cumulative_return", 0),
            dca_bias = row.get("dca_bias", 0),
            pct_drawdown = row.get("pct_drawdown", 0),
            recent_high_30d = row.get("recent_high_30d", 0),
            recent_low_30d = row.get("recent_low_30d", 0),
            high = row.get("high", 0),
            low = row.get("low", 0),
            ma_20d = row.get("ma_20d", 0),
            ma_30d = row.get("ma_30d", 0),
            ma_50d = row.get("ma_50d", 0),
            volatility_20d = row.get("volatility_20d", 0),
            volatility_30d = row.get("volatility_30d", 0),
            volatility_50d = row.get("volatility_50d", 0),
            )
        )
        for row in transformed_data
      ]
      
      # Save to Destination Table
      self._destination.load(transformed_data)
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