import os
import pandas as pd
from src.dashboard.infra.repositories.repository_factory import RepositoryFactory
from ..presenters.portfolio_presenter import PortfolioPresenter

class PortfolioController:
    def __init__(self):
        self._presenter = PortfolioPresenter()
        self._query_factory = RepositoryFactory()

    def get_data(self):
        # Fetch data from the service layer
        asset_data = self._query_factory.get("asset_query").get_asset_data()
        portfolio_value = self._query_factory.get("snapshot_query").get_unrealized_profit()
        
        asset_data_df = pd.DataFrame([dict(r._mapping) for r in asset_data])
        portfolio_value_df = pd.DataFrame([dict(r._mapping) for r in portfolio_value])
        
        data = {
            "assets": asset_data_df.to_dict(orient="records"),
            "portfolio_value": portfolio_value_df.to_dict(orient="records")
        }
        view_model = self._presenter.present(data)
        
        return view_model