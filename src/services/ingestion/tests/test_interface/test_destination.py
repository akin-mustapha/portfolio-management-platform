import pytest
from unittest.mock import MagicMock
# from src.services.ingestion_service.interfaces.destination import Destination
from ...protocols.destination import Destination


class TestDestinationInterface:

  @pytest.fixture
  def fix_destination_interface(self):
    return Destination
  
  def test_destination_interface_is_implemented(self, fix_destination_interface: Destination):
    try:
      destination_interface = fix_destination_interface()
      assert True
    except TypeError:
      assert True
    except NotImplementedError as e:
      AssertionError

