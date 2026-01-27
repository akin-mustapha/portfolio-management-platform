import os
import pandas as pd
from src.shared.database.client import SQLModelClient
from src.shared.repositories.query_repository import SnapshotSQLQueryRepository
from dotenv import load_dotenv 

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
database_client = SQLModelClient(database_url=DATABASE_URL)

class PortfolioService:
    def get_unrealized_profit(self):
        repo = SnapshotSQLQueryRepository(database_client)
        rows = repo.select_portfolio_unrealized_return()
        df = pd.DataFrame([dict(r._mapping) for r in rows])
        return df