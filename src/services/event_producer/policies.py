from datetime import datetime, UTC
from abc import ABC, abstractmethod
from typing import Protocol, Any

from src.services.ingestion.model.data import Data

class EventProducer(ABC):
  @abstractmethod
  def run(self) -> None:
    pass

class Source(ABC):
  _origin_name : str
  @abstractmethod
  def fetch(self) -> Data:
    pass

class Destination(ABC):
  _destination_name: str
  @abstractmethod
  def save(self, data: list[Any]) -> None:
    pass
  