
from src.services.portfolio.portfolio_service_builder import build_portfolio_service
# from src.dashboard.services.asset_service import AssetService
# from src.dashboard.services.portfolio_service import PortfolioService
from src.dashboard.services.local_portfolio_service import LocalPortfolioService
from src.dashboard.services.local_asset_service import LocalAssetService
from src.dashboard.services.asset_controller import AssetController
from src.dashboard.infra.repositories.repository_factory import RepositoryFactory
import pandas as pd

from .presenters import PortfolioPresenter

class PortfolioController:
    def __init__(self):
        # self._dashboard_service = build_portfolio_service()
        # self._dashboard_service = AssetService.get_asset_data()
        # self._dashboard_service = AssetController
        # self._dashboard_service_2 = PortfolioController
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
      
      
class AssetController:
    def __init__(self):
        self.asset_service = build_portfolio_service()
        self._presenter = PortfolioPresenter()

    def get_asset_data(self, asset_id):
        # Fetch data from the service layer
        data = self.asset_service.fetch_asset_data(asset_id)
        view_model = self._presenter.present_asset(asset_id)
        return view_model