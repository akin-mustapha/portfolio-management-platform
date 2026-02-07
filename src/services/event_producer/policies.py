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
  def __init__(self, destination_name: str):
    self._destination_name = destination_name
  
  @property
  def destination_name(self) -> str:
    return self._destination_name

  @abstractmethod
  def save(self, data: list[Any]) -> None:
    pass
  