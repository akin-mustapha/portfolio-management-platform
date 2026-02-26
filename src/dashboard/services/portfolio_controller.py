import os
import pandas as pd
from src.shared.database.client import SQLModelClient
from src.services.portfolio.infra.repositories.table_repository_factory import TableRepositoryFactory

from dotenv import load_dotenv 

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

class PortfolioService:
    def __init__(self):
        self.database_client = SQLModelClient(database_url=DATABASE_URL)

    def get_unrealized_profit(self) -> dict:
        repo = TableRepositoryFactory.get("snapshot_query")
        rows = repo.select_portfolio_unrealized_return()
        data = [dict(r._mapping) for r in rows]
        return data