from datetime import datetime, UTC
from abc import ABC, abstractmethod
from typing import Dict, Optional, Protocol, Any

from src.services.ingestion.model.data import Data

"""
  PROTOCOLS
"""
class Source(Protocol):
  def fetch(self) -> Data:
    raise NotImplementedError
  
  def _to_data(self, data) -> Data:
    raw_data = Data(
          source = self._endpoint,
          payload = data,
          is_processed = False,
          data_timestamp= datetime.now(UTC),
          processed_timestamp= None,
     )
    return raw_data

class Transformation(Protocol):
  def apply_to(self, data: Data) -> list[Any]:
    raise NotImplementedError
  def _get_raw_data(self, data: Data) -> Any:
    return data.payload
  
class Destination(Protocol):
  def save(self, data: list[Any]) -> None:
    raise NotImplementedError
  
class Sink(Protocol):
  def save(self, data: Any):
    raise NotImplementedError
  
class BaseRepositoryInterface(ABC):
  def __init__(self, entity_name, schema_name):
    self._entity_name = entity_name
    self._schema_name = schema_name
  @property
  def entity_name(self):
    return self._entity_name
  @entity_name.setter
  def entity_name(self, entity_name):
    self._entity_name = entity_name
  @property
  def schema_name(self):
    return self._schema_name
  @schema_name.setter
  def schema_name(self, schema_name):
    self._schema_name = schema_name
  @abstractmethod
  def insert(self, **kwargs):
    raise NotImplementedError("Subclasses must implement this method")
  @abstractmethod
  def upsert(self, **kwargs):
    raise NotImplementedError("Subclasses must implement this method")
  @abstractmethod
  def select(self, **kwargs):
    raise NotImplementedError("Subclasses must implement this method")
  @abstractmethod
  def select_all(self, **kwargs):
    raise NotImplementedError("Subclasses must implement this method")
  @abstractmethod
  def update(self, **kwargs):
    raise NotImplementedError("Subclasses must implement this method")
  @abstractmethod
  def delete(self, **kwargs):
    raise NotImplementedError("Subclasses must implement this method")

class RawDataRepositoryInterface(ABC):
  @abstractmethod
  def insert(self, record: Dict) -> Dict:
    pass
  @abstractmethod
  def select(self, source: str) -> Optional[Dict]:
    pass
  @abstractmethod
  def process_raw_data(self, id: int) -> None:
    pass



class DatabaseClientInterface(ABC):
  def __init__(self, entity_name, schema_name):
    self._entity_name = entity_name
    self._schema_name = schema_name
  @property
  def entity_name(self):
    return self._entity_name
  @entity_name.setter
  def entity_name(self, entity_name):
    self._entity_name = entity_name
  @property
  def schema_name(self):
    return self._schema_name
  @schema_name.setter
  def schema_name(self, schema_name):
    self._schema_name = schema_name
  @abstractmethod
  def insert(self, **kwargs):
    raise NotImplementedError("Subclasses must implement this method")
  @abstractmethod
  def upsert(self, **kwargs):
    raise NotImplementedError("Subclasses must implement this method")
  @abstractmethod
  def select(self, **kwargs):
    raise NotImplementedError("Subclasses must implement this method")
  @abstractmethod
  def select_all(self, **kwargs):
    raise NotImplementedError("Subclasses must implement this method")
  @abstractmethod
  def update(self, **kwargs):
    raise NotImplementedError("Subclasses must implement this method")
  @abstractmethod
  def delete(self, **kwargs):
    raise NotImplementedError("Subclasses must implement this method")