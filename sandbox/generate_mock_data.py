from src.dashboard.src.services.asset_service import AssetService
from src.dashboard.src.services.portfolio_service import PortfolioService
import pandas as pd

if __name__ == "__main__":
  df_asset_data = AssetService().get_asset_data()
  df_asset_snapshot = AssetService().get_asset_snapshot('2026-01-01', '2026-01-30')
  df_all_tags = AssetService().get_all_tag()
  df_all_assets = AssetService().get_all_asset()
  df_unrealized_return = pd.DataFrame(PortfolioService().get_unrealized_profit())

  df_asset_data.to_csv("data/csv/asset_data.csv", index=False)
  df_asset_snapshot.to_csv("data/csv/asset_snapshot.csv", index=False)
  df_all_tags.to_csv("data/csv/tags.csv", index=False)
  df_all_assets.to_csv("data/csv/assets.csv", index=False)
  df_unrealized_return.to_csv("data/csv/unrealized_return.csv", index=False)