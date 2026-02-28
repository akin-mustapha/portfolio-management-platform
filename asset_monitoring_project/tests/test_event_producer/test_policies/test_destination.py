

import pytest
from traitlets import Any
from event_producer.app.policies import Destination
from event_producer.app.domain import Event

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

# class TestEventProducer:
#   @pytest.fixture
#   def fixture_event_producer(self):
#     event_producer = EventProducer(name="test_event_producer", destination_name="test_destination")
#     return event_producer
  
#   def test_event_producer_is_created_correctly(self, fixture_event_producer: EventProducer):
#     assert fixture_event_producer.name == "test_event_producer"
#     assert fixture_event_producer.destination_name == "test_destination"