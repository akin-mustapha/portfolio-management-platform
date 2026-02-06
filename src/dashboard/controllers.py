
from src.services.portfolio.tagging_service_builder import build_portfolio_service
from src.dashboard.services.asset_service import AssetService
from src.dashboard.services.portfolio_service import PortfolioService
from src.dashboard.services.local_portfolio_service import LocalPortfolioService
from src.dashboard.services.local_asset_service import LocalAssetService


from .presenters import PortfolioPresenter

class PortfolioController:
    def __init__(self):
        # self._dashboard_service = build_portfolio_service()
        # self._dashboard_service = AssetService.get_asset_data()
        self._dashboard_service = LocalAssetService
        self._dashboard_service_2 = LocalPortfolioService
        self._presenter = PortfolioPresenter()

    def get_data(self):
        # Fetch data from the service layer
        asset_data = self._dashboard_service.get_asset_data()
        portfolio_value = self._dashboard_service_2().get_unrealized_profit()
        data = {
          "assets": asset_data.to_dict(orient="records"),
          "portfolio_value": portfolio_value
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