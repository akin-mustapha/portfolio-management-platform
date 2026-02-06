from typing import List, Dict
from src.services.ingestion.infra.repositories.table_repository_factory import TableRepositoryFactory
from src.services.ingestion.app.interfaces import Destination

from typing import List, Dict

class Trading212AssetDestination(Destination):
  def __init__(self, repo):
      self._repo = repo
  def save(self, data: List[Dict]) -> None:
      self._repo.upsert(data=data, unique_key="external_id")

class Trading212AssetSnapshotDestination(Destination):
  def __init__(self, repo):
      self._repo = repo
  def save(self, data: List[Dict]) -> None:
      self._repo.insert(data=data)

class Trading212PortfolioSnapshotDestination(Destination):
  def __init__(self, repo):
      self._repo = repo
  def save(self, data: List[Dict]) -> None:
      self._repo.insert(data=data)

class DestinationFactory:
  @staticmethod
  def create(destination_type: str):
    match destination_type:
      case "trading212_asset":
        repo = TableRepositoryFactory.get("asset")
        return Trading212AssetDestination(repo)
      case "trading212_asset_snapshot":
        repo = TableRepositoryFactory.get("asset_snapshot")
        return Trading212AssetSnapshotDestination(repo)
      case "trading212_portfolio_snapshot":
        repo = TableRepositoryFactory.get("portfolio_snapshot")
        return Trading212PortfolioSnapshotDestination(repo)
      case _:
        raise ValueError(f"Unknown destination type: {destination_type}")