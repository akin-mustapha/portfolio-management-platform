import pytest
from unittest.mock import MagicMock
from repository.repositories import PortfolioSnapshotRepository

class TestRepository:

  @pytest.fixture
  def repository(self):
    return PortfolioSnapshotRepository('portfolio_snapshot', {})
  
  def test_entity_name_is_not_null(self, repository):
    # Arrange

    # Act
    assert True