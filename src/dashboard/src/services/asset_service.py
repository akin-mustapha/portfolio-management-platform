import pandas as pd
from src.shared.repositories.entity_repository import EntityRepository
from src.shared.database.client import SQLModelClient
from src.shared.repositories.query_repository import SnapshotSQLQueryRepository
from dotenv import load_dotenv 
import os


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
database_client = SQLModelClient(database_url=DATABASE_URL)

class AssetService:
    # def __init__(self):
    _client = SQLModelClient(database_url=DATABASE_URL)
    @classmethod
    def get_asset(cls):
        repo = SnapshotSQLQueryRepository(cls._client)
        rows = repo.select_top_10_profit_asset_snapshot()
        df = pd.DataFrame([dict(r._mapping) for r in rows])
        return df
    @classmethod
    def get_asset_metric(cls):
        sql = """
            SELECT
                    a.name
                ,   a.description
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
                INNER JOIN asset_snapshot as [as]
                    ON a.id = [as].asset_id
                    AND am.data_date = [as].data_date
            GROUP BY a.id
            HAVING am.data_date = MAX(am.data_date)
        """

        with cls._client as client:
            res = client.execute(
                sql
            )

            res = res.fetchall()
        return pd.DataFrame(res)