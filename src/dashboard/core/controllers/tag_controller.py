import os
import pandas as pd
from dotenv import load_dotenv
from ..presenters.portfolio_presenter import PortfolioPresenter

from dashboard.infrastructure.repositories.repository_factory import RepositoryFactory

load_dotenv()

# class TagController:
#     def __init__(self):
#         self._presenter = PortfolioPresenter()
    
#     def get_all_asset(self):
#         repo = RepositoryFactory.get("asset_query")
#         rows = repo.select_all_asset()
#         df = pd.DataFrame([dict(r._mapping) for r in rows])
#         return df
    
#     def get_all_tag(self):
#         repo = RepositoryFactory.get("asset_query")
#         rows = repo.select_all_tag()
#         df = pd.DataFrame([dict(r._mapping) for r in rows])
#         return df
    
#     def get_asset_data(self):
#         repo = RepositoryFactory.get("asset_query")
#         rows = repo.get_asset_data()
#         return pd.DataFrame([dict(r._mapping) for r in rows])
    
#     def get_asset_snapshot(self, start_date, end_date):
#         repo = RepositoryFactory.get("snapshot_query")
#         rows = repo.get_asset_snapshot(start_date, end_date)
#         return pd.DataFrame([dict(r._mapping) for r in rows])