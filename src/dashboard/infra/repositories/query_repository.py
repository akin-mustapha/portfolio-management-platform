from dotenv import load_dotenv
from src.shared.database.client import SQLModelClient
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# ===== Postgres Repos =====
class PostgresAssetQueryRepository:
  def __init__(self):
    self.client = SQLModelClient(database_url=DATABASE_URL)

  def get_most_recent_asset_data(self):
    sql = """
      WITH most_recent_asset AS
      (
          SELECT
              ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY data_timestamp DESC) AS rn,
              id
          FROM staging.asset
      ),
      portfolio_value AS
      (
          SELECT total_value
          FROM staging.account
          ORDER BY created_timestamp DESC
          LIMIT 1
      )

      SELECT
          a.ticker,
          a.name,
          CASE WHEN ac.ma_30d > ac.ma_50d THEN 'Bullish' ELSE 'Bearish' END AS trend,
          a.description AS asset_description,
          -- STRING_AGG(t.name, ',') AS tag_list,
          a.value,
          a.profit,
          a.price,
          a.cost,

          a.value / pv.total_value * 100 AS weight_pct,

          ac.recent_profit_high_30d,
          ac.recent_profit_low_30d,
          ac.pct_drawdown,
          ac.volatility_30d,
          ac.volatility_50d,
          ac.ma_30d,
          ac.ma_50d,
          ac.dca_bias,
          ac.cumulative_return,
          a.created_timestamp AS data_date

      FROM staging.asset a
      INNER JOIN most_recent_asset lm
          ON a.id = lm.id
          AND lm.rn = 1

      LEFT JOIN staging.asset_computed ac
          ON a.id = ac.asset_id

      CROSS JOIN portfolio_value pv
    """
    with self.client as client:
      res = client.execute(
          sql
      )
      res = res.fetchall()
    return res

  def get_portfolio_price_history(self, tickers: list):
    if not tickers:
      return []
    ticker_list = "', '".join(tickers)
    sql = f"""
      SELECT ticker, price, created_timestamp as data_date
      FROM staging.asset
      WHERE created_timestamp >= CURRENT_TIMESTAMP - INTERVAL '30 days'
        AND ticker IN ('{ticker_list}')
      ORDER BY ticker, created_timestamp ASC
    """
    with self.client as client:
      res = client.execute(sql)
    return res.fetchall()
  
  def get_asset_history(self):
    try:
    
      sql = f"""
          ;WITH cte AS (
          SELECT  *
                , CAST(created_timestamp AS date) AS created_date
                , ROW_NUMBER()OVER(PARTITION BY ticker, CAST(created_timestamp AS date) ORDER BY created_timestamp DESC) AS rn
            FROM staging.asset
            WHERE created_timestamp >= CURRENT_TIMESTAMP - INTERVAL '30 days'
            ORDER BY ticker, created_timestamp ASC
        )
        SELECT
          *
         , CASE WHEN profit > 0 THEN 1 ELSE 0 END AS is_profitable
          
        FROM cte
        WHERE rn = 1
      """
      with self.client as client:
        res = client.execute(sql)
      return res.fetchall()
    except Exception as e:
      raise e

class PostgresSnapshotQueryRepository:
  def __init__(self):
    self.client = SQLModelClient(database_url=DATABASE_URL)

  def select_asset_snapshot(self, params=None):
    sql = """
    SELECT a.name, at.*
    FROM portfolio.asset a
    INNER JOIN portfolio.asset_snapshot at ON a.id = at.asset_id
    """
    with self.client as client:
      res = client.execute(sql, params or {})
    return res.fetchall()

  def select_top_10_profit_asset_snapshot(self):
    sql = """
    SELECT a.name, a.description,
           avg(at.profit) as profit,
           avg(at.price) as price,
           avg(at.value) as value
    FROM portfolio.asset a
    INNER JOIN portfolio.asset_snapshot at ON a.id = at.asset_id
    GROUP BY a.id
    ORDER BY profit DESC
    LIMIT 10
    """
    with self.client as client:
      res = client.execute(sql)
    return res.fetchall()

  def get_unrealized_profit(self):
    sql = """
    SELECT created_timestamp as data_date,
           total_value,
           investments_total_cost,
           investments_realized_pnl,
           investments_unrealized_pnl,
           currency
    FROM staging.account
    WHERE external_id IS NOT NULL
    ORDER BY data_date
    """
    with self.client as client:
      res = client.execute(sql)
    return res.fetchall()
  
  def get_asset_snapshot(self, ticker, start_date, end_date):
    
    ticker = ticker.lower()
    sql = f"""
        SELECT
            a.ticker,
            a.name as asset_description,
            ac.recent_value_high_30d,
            ac.recent_value_low_30d,
            ac.ma_30d,
            ac.ma_50d,
            ac.dca_bias,
            a.value,
            a.avg_price,
            a.price,
            a.profit,
            ac.volatility_30d,
            ac.pct_drawdown,
            a.created_timestamp as data_date
        FROM staging.asset a
        INNER JOIN staging.asset_computed as ac
            on a.id = ac.asset_id
        WHERE date(a.created_timestamp) BETWEEN '{start_date}' AND '{end_date}'
          AND lower(a.ticker) = '{ticker}'
        AND ac.asset_id IS NOT NULL
      """
    with self.client as client:
      res = client.execute(
          sql
      )
    res = res.fetchall()
    
    return res


# ===== SQLite Repos =====
class SQLiteAssetQueryRepository(PostgresAssetQueryRepository):
  def get_portfolio_price_history(self, tickers: list):
    if not tickers:
      return []
    ticker_list = "', '".join(tickers)
    sql = f"""
      SELECT ticker, price, created_timestamp as data_date
      FROM asset
      WHERE created_timestamp >= datetime('now', '-30 days')
        AND ticker IN ('{ticker_list}')
      ORDER BY ticker, created_timestamp ASC
    """
    with self.client as client:
      res = client.execute(sql)
    return res.fetchall()

class SQLiteSnapshotQueryRepository(PostgresSnapshotQueryRepository):
  def select_top_10_profit_asset_snapshot(self):
    sql = """
    SELECT a.name, a.description,
           avg(at.profit) as profit,
           avg(at.price) as price,
           avg(at.value) as value
    FROM asset a
    INNER JOIN asset_snapshot at ON a.id = at.asset_id
    GROUP BY a.id
    ORDER BY profit DESC
    LIMIT 10
    """
    with self.client as client:
      res = client.execute(sql)
    return res.fetchall()