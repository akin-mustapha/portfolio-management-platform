import os
import pandas as pd
from dotenv import load_dotenv
from ..presenters.portfolio_presenter import PortfolioPresenter

from src.dashboard.infra.repositories.repository_factory import RepositoryFactory

load_dotenv()

class AssetController:
    def __init__(self):
        self._presenter = PortfolioPresenter()
        self._query_factory = RepositoryFactory()
    
    def get_data(self):
        repo = self._query_factory.get("asset_query")
        all_asset_data = repo.select_all_asset()
        
        df_all_asset_data = pd.DataFrame([dict(r._mapping) for r in all_asset_data])
    
        asset_data = repo.get_asset_data()
        df_asset_data =  pd.DataFrame([dict(r._mapping) for r in asset_data])
    
    def get_asset_snapshot(self, start_date, end_date):
        repo = RepositoryFactory.get("snapshot_query")
        asset_snapshot = repo.get_asset_snapshot(start_date, end_date)
        df_asset_snapshot = pd.DataFrame([dict(r._mapping) for r in asset_snapshot])
        
        data = {
            "asset_history": df_asset_snapshot.to_dict(orient="records")
        }
        
        view_model = self._presenter.present(data)
        return view_model