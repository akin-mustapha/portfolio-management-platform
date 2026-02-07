from datetime import datetime, UTC
from abc import ABC, abstractmethod
from typing import Protocol, Any

from .domain import Event

class EventProducer(ABC):
  @abstractmethod
  def run(self) -> None:
    pass

class Origin(ABC):
  def __init__(self, origin_name: str):
    self._origin_name = origin_name
    self._evnet: Event = None
    self._metadata = None

  @property
  def origin_name(self) -> str:
    return self._origin_name
  @property
  def event(self) -> Event:
    return self._evnet

  @event.setter
  def event(self, event: Event):
    self._evnet = event
    
  def fetch(self) -> Event:
    data = self._handler()
    return self._to_event(data, self._metadata)
  
  def _to_event(self, data, metadata=None) -> Event:
    event = Event(
          metadata=metadata,
          payload = data,
          timestamp= datetime.now(UTC),
     )
    return event

  @abstractmethod
  def _handler(self) -> None:
    pass
  
class Destination(ABC):
  def __init__(self, destination_name: str):
    self._destination_name = destination_name
  
  @property
  def destination_name(self) -> str:
    return self._destination_name
  
  @property
  def event(self) -> Event:
    return self._evnet

  @event.setter
  def event(self, event: Event):
    self._evnet = event
    
  @abstractmethod
  def send(self, event: Event) -> None:
    pass
