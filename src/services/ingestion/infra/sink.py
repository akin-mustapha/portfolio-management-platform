import json
from dataclasses import asdict
from src.services.ingestion.app.interfaces import Data
from src.services.ingestion.app.interfaces import Sink

# TODO: Refactor to use repository interface
from src.services.ingestion.infra.repositories.table_repository_factory import TableRepositoryFactory

from sandbox.full_loader.main import PostgresAssetFullLoader


class SQLModelRawDataSchema:
  def _to_schema(self, data: Data):
    data_dict = asdict(data)
    data_dict = {
      "source": data_dict.get('source', ''),
      "payload": json.dumps(data_dict.get('payload', '')),
      "is_processed": data_dict.get('is_processed', ''),
      "created_datetime": data_dict.get('data_timestamp', ''),
      "processed_datetime": data_dict.get('processed_timestamp', ''),
    }
    return data_dict


class Trading212AssetSink(Sink, SQLModelRawDataSchema):
  def __init__(self):
    self._sink_repo = TableRepositoryFactory.get("raw_data")
  def save(self, data: Data):
    # data = self._to_schema(data)
    data = asdict(data)
    
    import json
    for record in data.get("payload", []):
      PostgresAssetFullLoader("raw.asset").load(json.dumps(record))
    # self._sink_repo.insert(record=data)

class Trading212AssetSnapshotSink(Sink, SQLModelRawDataSchema):
  def __init__(self):
    self._sink_repo = TableRepositoryFactory.get("raw_data")
  def save(self, data: Data):
    data = self._to_schema(data)
    self._sink_repo.insert(record=data)

class Trading212PortfolioSnapshotSink(Sink, SQLModelRawDataSchema):
  def __init__(self):
    self._sink_repo = TableRepositoryFactory.get("raw_data")
  def save(self, data: Data):
    data = self._to_schema(data)
    self._sink_repo.insert(record=data)


class SinkFactory:
  @staticmethod
  def create(sink_type: str) -> Sink:
    match sink_type:
      case "trading212_asset":
        return Trading212AssetSink()
      case "trading212_asset_snapshot":
        return Trading212AssetSnapshotSink()
      case "trading212_portfolio_snapshot":
        return Trading212PortfolioSnapshotSink()
      case _:
        raise ValueError(f"Unknown sink type: {sink_type}")