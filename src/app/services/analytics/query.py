
# TODO: Refactor to use repository interface (Query Repo for Asset)
from src.infra.database.client import SQLModelClient
from dotenv import load_dotenv
import os
import pandas as pd

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
      FROM asset_snapshot
      WHERE asset_id IS NOT NULL;
    """

    with cls._client as db:
      result = db.execute(sql)

    # TODO: Convert result to data
    return result.fetchall()


