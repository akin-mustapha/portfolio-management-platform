from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from src.services.ingestion.app.interfaces import Source
from src.services.ingestion.app.interfaces import Destination
from src.services.ingestion.app.interfaces import Transformation

class Pipeline(ABC):
  _source: Source
  _transformation: Transformation
  _destination: Destination
    
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
