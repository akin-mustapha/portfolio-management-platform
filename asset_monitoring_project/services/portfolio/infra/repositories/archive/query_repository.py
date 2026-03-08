from dotenv import load_dotenv
from src.shared.database.client import SQLModelClient
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# ===== Postgres Repos =====
class PostgresAssetQueryRepository:
  def __init__(self):
    self.client = SQLModelClient(database_url=DATABASE_URL)

  def select_all_asset(self):
    sql = """
    SELECT a.id as asset_id, a.name as asset_name
    FROM portfolio.asset a
    WHERE a.is_active = TRUE
    """
    with self.client as client:
      res = client.execute(sql)
    return res.fetchall()

  def select_all_tag(self):
    sql = """
    SELECT t.id as tag_id, t.name as tag_name
    FROM portfolio.tag t
    WHERE t.is_active = TRUE
    """
    with self.client as client:
      res = client.execute(sql)
    return res.fetchall()
  
  def select_all_tag_item(self):
    sql = """
    SELECT at.asset_id, a.name as asset_name,
           at.tag_id, t.name as tag_name
    FROM portfolio.asset a
    INNER JOIN portfolio.asset_tag at ON a.id = at.asset_id
    INNER JOIN portfolio.tag t ON at.tag_id = t.id
    """
    with self.client as client:
      res = client.execute(sql)
    return res.fetchall()

  def select_item_by_tag(self, tag_id):
    sql = """
    SELECT at.asset_id, a.name as asset_name,
           at.tag_id, t.name as tag_name
    FROM portfolio.asset a
    INNER JOIN portfolio.asset_tag at ON a.id = at.asset_id
    INNER JOIN portfolio.tag t ON at.tag_id = t.id
    WHERE t.id = :tag_id
    """
    with self.client as client:
      res = client.execute(sql, {"tag_id": tag_id})
    return res.fetchall()

  def select_tag_by_item(self, item_id):
    sql = """
    SELECT at.asset_id, a.name as asset_name,
           at.tag_id, t.name as tag_name
    FROM portfolio.asset a
    INNER JOIN portfolio.asset_tag at ON a.id = at.asset_id
    INNER JOIN portfolio.tag t ON at.tag_id = t.id
    WHERE a.id = :item_id
    """
    with self.client as client:
      res = client.execute(sql, {"item_id": item_id})
    return res.fetchall()


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

  def select_portfolio_unrealized_return(self):
    sql = """
    SELECT data_date,
           current_value AS portfolio_value,
           unrealized_profit AS unrealized_return
    FROM portfolio.portfolio_snapshot
    WHERE external_id IS NOT NULL
    GROUP BY data_date
    ORDER BY data_date
    """
    with self.client as client:
      res = client.execute(sql)
    return res.fetchall()


# ===== SQLite Repos =====
class SQLiteAssetQueryRepository(PostgresAssetQueryRepository):
  def select_all_asset(self):
    sql = """
    SELECT a.id as asset_id, a.name as asset_name
    FROM asset a
    WHERE a.is_active = 1
    """
    with self.client as client:
      res = client.execute(sql)
    return res.fetchall()

  def select_all_tag(self):
    sql = """
    SELECT t.id as tag_id, t.name as tag_name
    FROM tag t
    WHERE t.is_active = 1
    """
    with self.client as client:
      res = client.execute(sql)
    return res.fetchall()

  def select_all_tag_item(self):
    sql = """
    SELECT at.asset_id, a.name as asset_name,
           at.tag_id, t.name as tag_name
    FROM asset a
    INNER JOIN asset_tag at ON a.id = at.asset_id
    INNER JOIN tag t ON at.tag_id = t.id
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