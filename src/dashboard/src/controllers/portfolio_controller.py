import os
import pandas as pd
from dashboard.infra.repositories.repository_factory import RepositoryFactory
from ..presenters.portfolio_presenter import PortfolioPresenter

class PortfolioController:
    def __init__(self):
        self._presenter = PortfolioPresenter()
        self._query_factory = RepositoryFactory()

    def get_data(self):
        # Fetch data from the service layer
        asset_data = self._query_factory.get("asset_query").get_most_recent_asset_data()
        portfolio_history = self._query_factory.get("snapshot_query").get_unrealized_profit()
        
        df_asset_data = pd.DataFrame([dict(r._mapping) for r in asset_data])
        df_portfolio_history = pd.DataFrame([dict(r._mapping) for r in portfolio_history])
        
        portfolio_snapshot = df_portfolio_history.sort_values(by='data_date', ascending=False).head(1).to_dict("records")
        
        data = {
            "assets": df_asset_data.to_dict(orient="records"),
            "portfolio_history": df_portfolio_history.to_dict(orient="records"),
            "portfolio_current_snapshot": portfolio_snapshot[0]
        }
        view_model = self._presenter.present(data)
        
        return view_model