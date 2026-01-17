import pytest
from unittest.mock import MagicMock
from repository.repository_factory import RepositoryFactory

class TestRepositoryFactory:

  @pytest.fixture
  def repository_factory(self):
    return RepositoryFactory()