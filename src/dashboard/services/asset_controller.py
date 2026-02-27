import os
import pandas as pd
from dotenv import load_dotenv 
from src.shared.database.client import SQLModelClient

from src.dashboard.infra.repositories.repository_factory import RepositoryFactory

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
database_client = SQLModelClient(database_url=DATABASE_URL)

class AssetController:
    # def __init__(self):
    _client = SQLModelClient(database_url=DATABASE_URL)
    
    @classmethod
    def get_all_asset(cls):
        repo = RepositoryFactory.get("asset_query")
        rows = repo.select_all_asset()
        df = pd.DataFrame([dict(r._mapping) for r in rows])
        return df
    
    @classmethod
    def get_all_tag(cls):
        repo = RepositoryFactory.get("asset_query")
        rows = repo.select_all_tag()
        df = pd.DataFrame([dict(r._mapping) for r in rows])
        return df
    
    @classmethod
    def get_asset_data(cls):
        sql = """
            ;WITH most_recent_asset AS
            (
            SELECT
                ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY data_timestamp DESC) as rn
                , id
            FROM staging.asset
            )
            SELECT
                a.name,
                a.description AS asset_description,
                -- STRING_AGG(t.name, ',') AS tag_list,
                a.value,
                a.profit,
                a.price,
                a.cost,
                ac.recent_profit_high_30d,
                ac.recent_profit_low_30d,
                ac.pct_drawdown,
                ac.volatility_30d,
                ac.volatility_50d,
                ac.ma_30d,
                ac.ma_50d,
                ac.dca_bias,
                CASE WHEN ac.ma_30d > ac.ma_50d THEN 'Bullish' ELSE 'Bearish' END AS trend,
                a.created_timestamp as data_date
            FROM staging.asset a
            INNER JOIN most_recent_asset lm
                ON a.id = lm.id
                AND lm.rn = 1               -- only take latest metric per asset
            LEFT JOIN staging.asset_computed ac
                ON a.id = ac.asset_id
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
           SELECT
                a.name,
                a.description as asset_description,
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
            AND ac.asset_id IS NOT NULL
        """
        with cls._client as client:
            res = client.execute(
                sql
            )
            res = res.fetchall()
        return pd.DataFrame([dict(r._mapping) for r in res]) 