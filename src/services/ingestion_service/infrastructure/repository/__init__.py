from repository.asset_repository import AssetRepository
from repository.asset_snapshot_repository import AssetSnapshotRepository
from repository.portfolio_snapshot_repository import PortfolioSnapshotRepository
from repository.query_repository import ItemSQLQueryRepository
from repository.raw_data_repository import RawDataRepository
from repository.base_repository import BaseRepository
from repository.entity_repository import EntityRepository

repositories = [
  AssetRepository,
  AssetSnapshotRepository,
  PortfolioSnapshotRepository,
  ItemSQLQueryRepository,
  RawDataRepository,
  BaseRepository,
  EntityRepository,
]