import pytest
from ..protocols.destination import Destination




@pytest.fixture
def fix_destination_interface():
  return Destination