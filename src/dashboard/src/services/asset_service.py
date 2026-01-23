import pandas as pd

class AssetService:
    def __init__(self, repo):
        self.repo = repo
    def get_asset(self):
        rows = self.repo.select_top_10_profit_asset_snapshot()
        df = pd.DataFrame([dict(r._mapping) for r in rows])
        return df