
# TODO: Refactor to use repository interface (Query Repo for Asset)
from src.shared.database.client import SQLModelClient
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime, timedelta

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class AssetMetricQuery:
  _client = SQLModelClient(DATABASE_URL)
  @classmethod
  def get(cls):
    sql = """
      SELECT
        asset_id,
        data_date,
        price,
        MAX(price) OVER (
          PARTITION BY asset_id
          ORDER BY data_date
          ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS recent_high_30d,
        MIN(price) OVER (
          PARTITION BY asset_id
          ORDER BY data_date
          ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS recent_low_30d,
        AVG(price) OVER (
          PARTITION BY asset_id
          ORDER BY data_date
          ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS ma_30,
        AVG(price) OVER (
          PARTITION BY asset_id
          ORDER BY data_date
          ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
        ) AS ma_50
      FROM portfolio.asset_snapshot
      WHERE asset_id IS NOT NULL;
    """

    with cls._client as db:
      result = db.execute(sql)

    # TODO: Convert result to data
    return result.fetchall()



class AssetSilverQueryRepo:
  """
    Query Window. Incremental Loader
  """
  _client = SQLModelClient(DATABASE_URL)
  
  _window_in_hrs = 1

  @classmethod
  def get_bronze_asset(cls):
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
          FROM portfolio.asset_v2 x1
          WHERE t1.business_key = x1.business_key
        )
    LIMIT 1000;
    """
    with cls._client as db:
      result = db.execute(sql)
    return result.fetchall()
      
      
  @classmethod
  def get_asset_computed(cls):
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
            FROM portfolio.asset_v2 b
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
                AVG(value) OVER (PARTITION BY ticker ORDER BY created_timestamp ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS ma_20,
                AVG(value) OVER (PARTITION BY ticker ORDER BY created_timestamp ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS ma_30,
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
            daily_return                        AS return,
            cumulative_return,

            -- DCA bias: current value vs average cost
            (value - cost) / NULLIF(cost, 0)    AS dca_bias,

            -- drawdown from recent high
            (value - recent_high_30d) / NULLIF(recent_high_30d, 0) AS pct_drawdown,

            recent_high_30d,
            recent_low_30d,
            high,
            low,
            ma_20,
            ma_30,
            ma_50d,
            volatility_20d,
            volatility_30d,
            volatility_50d
        FROM stats s
    """
    with cls._client as db:
      result = db.execute(sql)
    return result.fetchall()
      