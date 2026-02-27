import os
import pandas as pd
from src.shared.database.client import SQLModelClient
from src.dashboard.infra.repositories.repository_factory import RepositoryFactory
from dotenv import load_dotenv 

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

class PortfolioService:
    def __init__(self):
        self.database_client = SQLModelClient(database_url=DATABASE_URL)

    def get_unrealized_profit(self) -> dict:
        repo = RepositoryFactory.get("snapshot_query")
        rows = repo.select_portfolio_unrealized_return()
        data = [dict(r._mapping) for r in rows]
        return data