from typing import List, Dict
from src.shared.repositories.entity_repository import EntityRepository
from src.services.ingestion.app.interfaces import Destination

class Trading212AssetDestination(Destination):
  def __init__(self):
    self._destination_repo = EntityRepository("asset")
  def save(self, records: List[Dict]) -> None:
    self._destination_repo.upsert(records=records, unique_key='external_id')

class Trading212AssetSnapshotDestination(Destination):
  def __init__(self):
    self._destination_repo = EntityRepository("asset_snapshot")
  def save(self, records: List[Dict]) -> None:
    self._destination_repo.insert(records=records)

class Trading212PortfolioSnapshotDestination(Destination):
  def __init__(self):
    self._destination_repo = EntityRepository("portfolio_snapshot")
  def save(self, records: List[Dict]) -> None:
    self._destination_repo.insert(records=records)