import pandas as pd


# load_dotenv()

BASE_URL = "shared/data/csv"

class LocalAssetService:
    # def __init__(self):
    # _client = SQLModelClient(database_url=DATABASE_URL)
    @classmethod
    def get_all_asset(cls):
        df = pd.read_csv(f"{BASE_URL}/assets.csv")
        return df
    @classmethod
    def get_all_tag(cls):
        df = pd.read_csv(f"{BASE_URL}/tags.csv")
        return df
    @classmethod
    def get_asset_data(cls):
        df = pd.read_csv(f"{BASE_URL}/asset_data.csv")
        return df
    @classmethod
    def get_asset_snapshot(cls, start_date, end_date):
        df = pd.read_csv(f"{BASE_URL}/asset_snapshot.csv")
        return df