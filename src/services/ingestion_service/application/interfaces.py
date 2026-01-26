from typing import Protocol, Any
from dataclasses import dataclass
from datetime import datetime, UTC
from abc import ABC, abstractmethod

class Pipeline(ABC):
  @abstractmethod
  def run(self):
    raise NotImplementedError

"""
  DOMAIN
"""
@dataclass
class Data:
  source: str
  payload: Any
  is_processed: bool
  data_timestamp: str
  processed_timestamp: str

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