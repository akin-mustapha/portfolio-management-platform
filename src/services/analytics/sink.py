"""
  Concrete implementation of the storage logic for asssets
"""
import pandas as pd
# TODO: Rafactor to use repository interface
from src.services.analytics.infra.clients.database.database_client import DatabaseClientFactory
from src.services.analytics.infra.repositories.table_repository_factory import TableRepositoryFactory


class SinkAssetMetric:
  _repository = DatabaseClientFactory.get_repository("asset_metric", schema_name="portfolio")
  @classmethod
  def save(cls, df: pd.DataFrame):
    records = df.to_dict(orient="records")
    cls._repository.insert(records)
    

class SinkSilverAsset:
  _repository = DatabaseClientFactory.get_repository("asset_v2", schema_name="portfolio")
  @classmethod
  def save(cls, df: pd.DataFrame):
    records = df.to_dict(orient="records")
    cls._repository.upsert(records, ['business_key'])
    
    
class SinkSilverAssetComputed:
  _repository = DatabaseClientFactory.get_repository("asset_computed", schema_name="portfolio")
  @classmethod
  def save(cls, df: pd.DataFrame):
    records = df.to_dict(orient="records")
    
    cls._repository.upsert(records, ['asset_id'])
    
    
    
    
class SinkRepositoryFactory:
    # Registry: table_name -> {db_type -> repository class}
    registry = {
        "asset": SinkSilverAsset,
        "asset_computed": SinkSilverAssetComputed
    }

    @classmethod
    def get(cls, sink_name: str):
        repo = cls.registry.get(sink_name)
        if not repo:
            raise ValueError(f"No repository registered for table: {sink_name}")
        if not repo:
            raise ValueError(f"No repository for table '{sink_name}'")
        return repo()