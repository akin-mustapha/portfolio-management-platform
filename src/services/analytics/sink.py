"""
  Concrete implementation of the storage logic for asssets
"""
import pandas as pd
# TODO: Rafactor to use repository interface
from src.services.analytics.app.interfaces import BaseRepositoryInterface
from src.services.analytics.infra.clients.database.database_client import DatabaseClientFactory
from src.services.analytics.infra.repositories.table_repository_factory import TableRepositoryFactory


class SinkAssetMetric:
  _repository = DatabaseClientFactory.get_repository("asset_metric", schema_name="portfolio")
  @classmethod
  def save(cls, df: pd.DataFrame):
    records = df.to_dict(orient="records")
    cls._repository.insert(records)