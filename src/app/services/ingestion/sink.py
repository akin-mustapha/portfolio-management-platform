import json
from dataclasses import asdict
from src.app.interfaces.ingestion import Data
from src.app.interfaces.ingestion import Sink

# TODO: Refactor to use repository interface
from src.infra.repositories.table_repository_factory import TableRepositoryFactory


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
    data = self._to_schema(data)
    self._sink_repo.insert(record=data)

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
