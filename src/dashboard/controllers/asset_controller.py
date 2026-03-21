import pandas as pd
from dotenv import load_dotenv
from ..presenters.asset_presenter import AssetPresenter
from ..infrastructure.repositories.repository_factory import RepositoryFactory

load_dotenv()

class AssetController:
    def __init__(self):
        self._presenter = AssetPresenter()

    def get_asset_snapshot(self, ticker, start_date, end_date):
        repo = RepositoryFactory.get("snapshot_query")
        asset_snapshot = repo.get_asset_snapshot(ticker, start_date, end_date)

        df_asset_snapshot = pd.DataFrame([dict(r._mapping) for r in asset_snapshot])

        data = {
            "asset_history": df_asset_snapshot.to_dict(orient="records")
        }

        view_model = self._presenter.present_asset_history(data)
        return view_model
