"""
  Concrete implementation of the storage logic for asssets
"""
import pandas as pd
# TODO: Rafactor to use repository interface
from src.app.interfaces.interface import BaseRepositoryInterface
from src.infra.repositories.entity_repository import EntityRepositoryFactory


class SinkAssetMetric:
  _repository = EntityRepositoryFactory.get_repository("asset_metric", schema_name="portfolio")
  @classmethod
  def save(cls, df: pd.DataFrame):
    records = df.to_dict(orient="records")
    cls._repository.insert(records)