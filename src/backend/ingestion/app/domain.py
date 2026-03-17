"""
  DOMAIN
"""
from dataclasses import dataclass
from typing import Any


@dataclass
class Data:
  source: str
  payload: Any
  is_processed: bool
  data_timestamp: str
  processed_timestamp: str
