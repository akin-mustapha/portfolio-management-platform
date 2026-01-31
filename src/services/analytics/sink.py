"""
  Concrete implementation of the storage logic for asssets
"""
import pandas as pd
from src.shared.repositories.entity_repository import EntityRepository


class SinkAssetMetric:
  _repository = EntityRepository("asset_metric")
  @classmethod
  def save(cls, df: pd.DataFrame):
    records = df.to_dict(orient="records")
    cls._repository.insert(records)