from src.shared.database.client import SQLModelClient
from src.shared.repositories.entity_repository import EntityRepository
from dotenv import load_dotenv
import pandas as pd


class SinkAssetMetric:
  _repository = EntityRepository("asset_metric")
  @classmethod
  def save(cls, df: pd.DataFrame):
    records = df.to_dict(orient="records")

    cls._repository.insert(records)