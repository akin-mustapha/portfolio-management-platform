from repositories.asset_repository import AssetRepository
from repositories.asset_snapshot_repository import AssetSnapshotRepository
from repositories.portfolio_snapshot_repository import PortfolioSnapshotRepository
from repositories.query_repository import ItemSQLQueryRepository
from repositories.raw_data_repository import RawDataRepository
from repositories.base_repository import BaseRepository
from repositories.entity_repository import EntityRepository

repositories = [
  AssetRepository,
  AssetSnapshotRepository,
  PortfolioSnapshotRepository,
  ItemSQLQueryRepository,
  RawDataRepository,
  BaseRepository,
  EntityRepository,
]