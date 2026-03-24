

import pytest
from pipelines.application.policies import EventDestination as Destination
from pipelines.domain.models import Event

class TestDestination:
  @pytest.fixture
  def fixture_destination(self):
    class TestDestinationImpl(Destination):
      def send(self, event: Event) -> None:
        pass
    destination = TestDestinationImpl(destination_name="test_destination")
    return destination

  def test_destination_is_created_correctly(self, fixture_destination: Destination):
    assert fixture_destination.destination_name == "test_destination"
