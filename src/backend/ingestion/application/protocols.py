from datetime import datetime, UTC
from typing import Protocol, Any

from ..domain import Data

"""
  PROTOCOLS
"""
class Source(Protocol):
  def extract(self) -> Data:
    raise NotImplementedError

  # Deprecated, to be removed
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
  def transform(self, data: Data) -> list[Any]:
    raise NotImplementedError

  def _get_raw_data(self, data: Data) -> Any:
    return data.payload

class Destination(Protocol):

  def load(self, data: list[Any]) -> None:
    raise NotImplementedError
