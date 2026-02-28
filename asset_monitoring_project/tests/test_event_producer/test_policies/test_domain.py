

import pytest
from datetime import datetime, UTC

from event_producer.app.domain import Event

class TestEventDomain:
  @pytest.fixture
  def fixture_event(self):
    return Event(metadata={"name": "test_event"}, payload={"key": "value"}, timestamp='2026-02-09')
  
  def test_event_is_created_correctly(self, fixture_event: Event):
    assert fixture_event.metadata.get("name") == "test_event"
    assert fixture_event.payload == {"key": "value"}
    assert fixture_event.timestamp == "2026-02-09"
    
  def test_event_is_iterable(self, fixture_event: Event):
    event_dict = dict(fixture_event)
    assert event_dict["metadata"].get("name") == "test_event"
    assert event_dict["payload"] == {"key": "value"}
    assert event_dict["timestamp"] == "2026-02-09"