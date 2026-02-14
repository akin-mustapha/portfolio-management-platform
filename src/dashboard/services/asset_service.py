import os
import pandas as pd
from dotenv import load_dotenv 
from src.shared.database.client import SQLModelClient

from src.services.portfolio.infra.repositories.table_repository_factory import TableRepositoryFactory

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
database_client = SQLModelClient(database_url=DATABASE_URL)

class AssetService:
    # def __init__(self):
    _client = SQLModelClient(database_url=DATABASE_URL)
    
    @classmethod
    def get_all_asset(cls):
        repo = TableRepositoryFactory.get("asset_query")
        rows = repo.select_all_asset()
        df = pd.DataFrame([dict(r._mapping) for r in rows])
        return df
    
    @classmethod
    def get_all_tag(cls):
        repo = TableRepositoryFactory.get("asset_query")
        rows = repo.select_all_tag()
        df = pd.DataFrame([dict(r._mapping) for r in rows])
        return df
    
    @classmethod
    def get_asset_data(cls):
        sql = """
            WITH LatestMetric AS (
                SELECT *,
                    ROW_NUMBER() OVER (PARTITION BY asset_id ORDER BY data_date DESC) AS rn
                FROM asset_metric
            )
            SELECT
                a.name,
                a.description AS asset_description,
                STRING_AGG(t.name, ',') AS tag_list,
                snap.value,
                snap.profit,
                snap.price,
                lm.recent_high_30d,
                lm.recent_low_30d,
                lm.pct_drawdown,
                lm.volatility_30d,
                lm.price_vs_ma_50,
                lm.ma_30,
                lm.ma_50,
                lm.dca_bias,
                CASE WHEN lm.ma_30 > lm.ma_50 THEN 'Bullish' ELSE 'Bearish' END AS trend,
                lm.data_date
            FROM asset a
            INNER JOIN LatestMetric lm
                ON a.id = lm.asset_id
                AND lm.rn = 1               -- only take latest metric per asset
            LEFT JOIN asset_snapshot snap
                ON a.id = snap.asset_id
                AND snap.data_date = lm.data_date
            LEFT JOIN asset_tag at
                ON a.id = at.asset_id
                AND at.is_active = 1
            LEFT JOIN tag t
                ON at.tag_id = t.id
                AND t.is_active = 1
            WHERE a.is_active = 1
            GROUP BY 
                a.id, a.name, a.description, snap.value, snap.profit, snap.price,
                lm.recent_high_30d, lm.recent_low_30d, lm.pct_drawdown, lm.volatility_30d,
                lm.price_vs_ma_50, lm.ma_30, lm.ma_50, lm.dca_bias, lm.data_date
        """
        with cls._client as client:
            res = client.execute(
                sql
            )
            res = res.fetchall()
        return pd.DataFrame([dict(r._mapping) for r in res])
    
    @classmethod
    def get_asset_snapshot(cls, start_date, end_date):
        sql = f"""
           select
                a.name,
                a.description as asset_description,
                [a_snap].*,
                MAX(price) OVER (
                PARTITION BY a_snap.asset_id
                ORDER BY data_date
                ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
                ) AS recent_high_30d,
                MIN(price) OVER (
                PARTITION BY a_snap.asset_id
                ORDER BY data_date
                ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
                ) AS recent_low_30d,
                AVG(price) OVER (
                PARTITION BY a_snap.asset_id
                ORDER BY data_date
                ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
                ) AS ma_30,
                AVG(price) OVER (
                PARTITION BY a_snap.asset_id
                ORDER BY data_date
                ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
                ) AS ma_50,
                t.name as tag_name
            from asset a
            INNER JOIN asset_snapshot as [a_snap]
                on a.id = [a_snap].asset_id
            LEFT JOIN asset_tag as at
                ON a.id = at.asset_id
            INNER JOIN tag as t
                ON at.tag_id = t.id
            WHERE date(a_snap.data_date) BETWEEN '{start_date}' AND '{end_date}'
            AND a_snap.asset_id IS NOT NULL
        """
        with cls._client as client:
            res = client.execute(
                sql
            )
            res = res.fetchall()
        return pd.DataFrame([dict(r._mapping) for r in res]) 