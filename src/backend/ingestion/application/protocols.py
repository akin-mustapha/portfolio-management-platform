from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Protocol, Any

from pydantic import BaseModel

from ..domain import Data

"""
  VALIDATION
"""
@dataclass
class RejectedRecord:
    pipeline_name: str | None
    layer: str
    business_key: str | None
    raw_payload: dict
    error_type: str
    error_message: str

@dataclass
class ValidationResult:
    valid: list[BaseModel]
    invalid: list[RejectedRecord]

class Validator(Protocol):
    def validate(self, data: list[dict]) -> ValidationResult: ...


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
