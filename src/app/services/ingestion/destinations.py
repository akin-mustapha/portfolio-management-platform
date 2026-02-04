from typing import List, Dict
from src.infra.repositories.entity_repository import EntityRepositoryFactory
from src.infra.repositories.table_repository_factory import TableRepositoryFactory
from src.app.interfaces.ingestion import Destination

class Trading212AssetDestination(Destination):
  def __init__(self):
    self._destination_repo = TableRepositoryFactory.get("asset")
  def save(self, data: List[Dict]) -> None:
    self._destination_repo.upsert(data=data, unique_key='external_id')

class Trading212AssetSnapshotDestination(Destination):
  def __init__(self):
    self._destination_repo = TableRepositoryFactory.get("asset_snapshot")
  def save(self, data: List[Dict]) -> None:
    self._destination_repo.insert(data=data)

class Trading212PortfolioSnapshotDestination(Destination):
  def __init__(self):
    self._destination_repo = EntityRepositoryFactory.get_repository("portfolio_snapshot", schema_name="portfolio")
  def save(self, data: List[Dict]) -> None:
    self._destination_repo.insert(records=data)