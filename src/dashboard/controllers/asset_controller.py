import os
import pandas as pd
from dotenv import load_dotenv
from ..presenters.asset_presenter import AssetPresenter

from ..infrastructure.repositories.repository_factory import RepositoryFactory
from backend.services.portfolio.infrastructure.repositories.repository_factory import RepositoryFactory as PortfolioRepositoryFactory

load_dotenv()

class AssetController:
    def __init__(self):
        self._presenter = AssetPresenter()
        self._query_factory = RepositoryFactory()
        self._portfolio_factory = PortfolioRepositoryFactory()

    def get_data(self):
        asset_repo = self._portfolio_factory.get("asset")
        all_asset_data = asset_repo.select_all()

        df_all_asset_data = pd.DataFrame(all_asset_data)

        analytics_repo = self._query_factory.get("asset_analytics")
        asset_data = analytics_repo.get_most_recent_asset_data()
        df_asset_data = pd.DataFrame([dict(r._mapping) for r in asset_data])

        data = {
            "all_asset_data": df_all_asset_data.to_dict("records"),
            "asset_data": df_asset_data.to_dict("records"),
        }

        view_model = self._presenter.present(data)

        return view_model

    def get_asset_snapshot(self, ticker, start_date, end_date):
        repo = RepositoryFactory.get("snapshot_query")
        asset_snapshot = repo.get_asset_snapshot(ticker, start_date, end_date)

        df_asset_snapshot = pd.DataFrame([dict(r._mapping) for r in asset_snapshot])

        data = {
            "asset_history": df_asset_snapshot.to_dict(orient="records")
        }

        view_model = self._presenter.present_asset_history(data)
        return view_model
