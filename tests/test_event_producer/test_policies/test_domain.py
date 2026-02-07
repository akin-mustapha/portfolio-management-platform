

import pytest
from datetime import date

from src.services.event_producer.domain import Event

class TestEventDomain:
  @pytest.fixture
  def fixture_event(self):
    return Event(metadata={"name": "test_event"}, payload={"key": "value"}, timestamp=date.today())
  
  def test_event_is_created_correctly(self, fixture_event: Event):
    assert fixture_event.metadata.get("name") == "test_event"
    assert fixture_event.payload == {"key": "value"}
    assert fixture_event.timestamp == date.today()
    
  def test_event_is_iterable(self, fixture_event: Event):
    event_dict = dict(fixture_event)
    assert event_dict["metadata"].get("name") == "test_event"
    assert event_dict["payload"] == {"key": "value"}
    assert event_dict["timestamp"] == date.today()
