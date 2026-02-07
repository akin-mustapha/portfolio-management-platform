

import pytest
from datetime import date

from src.services.event_producer.domain import Event

class TestEventDomain:
  @pytest.fixture
  def fixture_event(self):
    return Event(name="test_event", payload={"key": "value"}, datetime=date.today())
  
  def test_event_is_created_correctly(self, fixture_event: Event):
    assert fixture_event.name == "test_event"
    assert fixture_event.payload == {"key": "value"}
    assert fixture_event.datetime == date.today()
    
  def test_event_is_iterable(self, fixture_event: Event):
    event_dict = dict(fixture_event)
    assert event_dict["name"] == "test_event"
    assert event_dict["payload"] == {"key": "value"}
    assert event_dict["datetime"] == date.today()
