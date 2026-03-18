

import pytest
from typing import Any
from backend.ingestion.application.policies import Origin
from backend.ingestion.domain.models import Event

class TestOrigin:
  @pytest.fixture
  def fixture_origin(self):

    class TestOriginImpl(Origin):
      def _handler(self) -> Any:
        self._metadata = {"origin_name": self._origin_name}
        return {"key": "value"}
    origin = TestOriginImpl(origin_name="test_origin")
    return origin

  def test_origin_is_created_correctly(self, fixture_origin: Origin):
    assert fixture_origin.origin_name == "test_origin"
    assert fixture_origin.event is None

  def test_origin_fetches_data_and_creates_event(self, fixture_origin: Origin):
    event = fixture_origin.fetch()
    assert event.metadata.get('origin_name') == "test_origin"
    assert event.payload == {"key": "value"}
    assert event.timestamp is not None
