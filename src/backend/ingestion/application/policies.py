import logging
from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import date, timedelta, datetime, UTC

from .protocols import Source
from .protocols import Destination
from .protocols import Transformation
from ..domain.models import Event

class Pipeline(ABC):
  _source: Source
  _transformation: Transformation
  _destination: Destination

  @abstractmethod
  def run(self):
    raise NotImplementedError


class BaseSilverPipeline(Pipeline):
  """
  Shared run() logic for silver pipelines.
  Subclasses declare _pipeline_name and wire _validator and _dead_letter in __init__.
  """
  _pipeline_name: str

  def run(self):
    try:
      data = self._source.extract()

      if len(data) == 0:
        logging.warning("NO RECORD")
        return

      transformed_data = self._transformation.transform(data)
      result = self._validator.validate(transformed_data)

      if result.invalid:
        for r in result.invalid:
          r.pipeline_name = self._pipeline_name
        self._dead_letter.load(result.invalid)
        logging.warning(f"[{self._pipeline_name}] {len(result.invalid)} records rejected — written to dead letter")

      records = self._to_records(result.valid)
      self._destination.load(records)
      return None

    except Exception as e:
      raise e

  def _to_records(self, validated_data: list) -> list[dict]:
    """Convert validated Pydantic model instances to dicts for the destination."""
    return [record.model_dump() for record in validated_data]

class BaseGoldPipeline(Pipeline):
  """
  Shared run() logic for gold layer pipelines.

  Subclasses must declare:
    _pipeline_name: str
    _fact_destinations: list[Destination]

  And wire _source, _transformation, _validator, _dead_letter in __init__.

  Override _ensure_dimensions() to upsert any dimension rows that fact FK
  constraints depend on. This runs before extract so the source query can
  safely join dim tables.
  """
  _pipeline_name: str
  _fact_destinations: list

  def run(self):
    self._ensure_dimensions()

    data = self._source.extract()

    if not data:
      logging.warning(f"[{self._pipeline_name}] NO RECORD — skipping")
      return

    transformed_data = self._transformation.transform(data)
    result = self._validator.validate(transformed_data)

    if result.invalid:
      for r in result.invalid:
        r.pipeline_name = self._pipeline_name
      self._dead_letter.load(result.invalid)
      logging.warning(f"[{self._pipeline_name}] {len(result.invalid)} records rejected — written to dead letter")

    if not result.valid:
      logging.warning(f"[{self._pipeline_name}] no valid records after validation — nothing to load")
      return

    records = self._to_records(result.valid)

    for destination in self._fact_destinations:
      destination.load(records)

  def _ensure_dimensions(self):
    """Seed dimension tables before the source query runs. Override in subclass."""
    pass

  def _to_records(self, validated_data: list) -> list[dict]:
    return [record.model_dump() for record in validated_data]


class FullLoader(ABC):
  def __init__(self, table_name):
    self._current_datetime = datetime.now()
    self._day = self._current_datetime.strftime('%Y_%m_%d')
    self._next_day = (self._current_datetime + timedelta(days=1)).strftime('%Y_%m_%d')
    self._table_name = table_name
    self._partition_name = f"{self._table_name}_{self._day}"

  def load(self, data):
    self._create_partition()
    self._loader(data)
    self._exposition_abstraction()

  @abstractmethod
  def _create_partition(self):
    pass

  @abstractmethod
  def _loader(self):
    pass

  def _exposition_abstraction(self):
    pass


class EventProducer(ABC):
  @abstractmethod
  def run(self) -> None:
    pass

class Origin(ABC):
  def __init__(self, origin_name: str):
    self._origin_name = origin_name
    self._event: Event = None
    self._metadata = None

  @property
  def origin_name(self) -> str:
    return self._origin_name
  @property
  def event(self) -> Event:
    return self._event

  @event.setter
  def event(self, event: Event):
    self._event = event

  def fetch(self) -> Event:
    data = self._handler()
    return self._to_event(data, self._metadata)

  def _to_event(self, data, metadata=None) -> Event:
    event = Event(
          metadata=metadata,
          payload = data,
          timestamp=datetime.now(UTC).isoformat(),
     )
    return event

  @abstractmethod
  def _handler(self) -> None:
    pass

class EventDestination(ABC):
  def __init__(self, destination_name: str):
    self._destination_name = destination_name
    self._event: Event = None

  @property
  def destination_name(self) -> str:
    return self._destination_name

  @property
  def event(self) -> Event:
    return self._event

  @event.setter
  def event(self, event: Event):
    self._event = event

  @abstractmethod
  def send(self, event: Event) -> None:
    pass


class SchemeFactory(ABC):
  @abstractmethod
  def get_schema(self, table_name):
    pass

class Mapper(ABC):
  @abstractmethod
  def map(self) -> None:
    pass


class EventConsumer(ABC):
  @abstractmethod
  def run(self, event) -> None:
    pass


class Repository(ABC):
  def __init__(self, entity_name, schema_name):
    self._entity_name = entity_name
    self._schema_name = schema_name

  @property
  def entity_name(self):
    return self._entity_name

  @entity_name.setter
  def entity_name(self, entity_name):
    self._entity_name = entity_name

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
