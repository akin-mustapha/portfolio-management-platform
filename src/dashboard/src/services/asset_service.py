import os
import pandas as pd
from dotenv import load_dotenv 
from src.shared.database.client import SQLModelClient
from src.shared.repositories.query_repository import ItemSQLQueryRepository


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
database_client = SQLModelClient(database_url=DATABASE_URL)

class AssetService:
    # def __init__(self):
    _client = SQLModelClient(database_url=DATABASE_URL)
    @classmethod
    def get_all_asset(cls):
        repo = ItemSQLQueryRepository(cls._client)
        rows = repo.select_all_asset()
        df = pd.DataFrame([dict(r._mapping) for r in rows])
        return df
    @classmethod
    def get_all_tag(cls):
        repo = ItemSQLQueryRepository(cls._client)
        rows = repo.select_all_tag()
        df = pd.DataFrame([dict(r._mapping) for r in rows])
        return df
    @classmethod
    def get_asset_metric(cls):
        sql = """
            SELECT
                    a.name
                ,   a.description
                ,	STRING_AGG(t.name, ',') as tag_list
                ,   [as].value
                ,   [as].profit
                ,   [as].price
                ,   [am].recent_high_30d
                ,   [am].recent_low_30d
                ,   am.pct_drawdown
                ,   am.volatility_30d
                ,   am.price_vs_ma_50
                ,   am.dca_bias
            FROM asset a
                INNER JOIN asset_metric am
                    ON a.id = am.asset_id
                LEFT JOIN asset_snapshot as [as]
                    ON a.id = [as].asset_id
                AND am.data_date = [as].data_date
                LEFT JOIN asset_tag at
                    ON a.id = at.asset_id
                    AND at.is_active = True
                LEFT JOIN tag t 
                    ON at.tag_id  = t.id
                AND t.is_active = True
            WHERE a.is_active = True
            GROUP BY a.id
            HAVING am.data_date = MAX(am.data_date)
        """

        with cls._client as client:
            res = client.execute(
                sql
            )
            res = res.fetchall()
        return pd.DataFrame(res)