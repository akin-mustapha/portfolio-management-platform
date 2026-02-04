from typing import List, Dict
from src.infra.repositories.entity_repository import EntityRepositoryFactory
from src.app.interfaces.ingestion import Destination

class Trading212AssetDestination(Destination):
  def __init__(self):
    self._destination_repo = EntityRepositoryFactory.get_repository("asset", schema_name="portfolio")
  def save(self, records: List[Dict]) -> None:
    self._destination_repo.upsert(records=records, unique_key='external_id')

class Trading212AssetSnapshotDestination(Destination):
  def __init__(self):
    self._destination_repo = EntityRepositoryFactory.get_repository("asset_snapshot", schema_name="portfolio")
  def save(self, records: List[Dict]) -> None:
    self._destination_repo.insert(records=records)

class Trading212PortfolioSnapshotDestination(Destination):
  def __init__(self):
    self._destination_repo = EntityRepositoryFactory.get_repository("portfolio_snapshot", schema_name="portfolio")
  def save(self, records: List[Dict]) -> None:
    self._destination_repo.insert(records=records)