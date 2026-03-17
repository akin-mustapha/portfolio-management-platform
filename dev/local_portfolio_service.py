import os
import pandas as pd
# from src.shared.database.client import SQLModelClient
# from src.infra.repositories.query_repository import SnapshotSQLQueryRepository
from dotenv import load_dotenv 

load_dotenv()

BASE_URL = 'data/csv'

class LocalPortfolioService:
    def __init__(self):
        self.database_client = None

    def get_unrealized_profit(self) -> dict:
        df = pd.read_csv(f"{BASE_URL}/unrealized_return.csv")
        return df.to_dict("records")