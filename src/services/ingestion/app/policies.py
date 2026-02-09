from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


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
