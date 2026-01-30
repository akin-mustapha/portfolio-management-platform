from src.shared.repositories.asset_repository import AssetRepository
from src.shared.repositories.asset_snapshot_repository import AssetSnapshotRepository
from src.shared.repositories.portfolio_snapshot_repository import PortfolioSnapshotRepository
from src.shared.repositories.query_repository import ItemSQLQueryRepository
from src.shared.repositories.raw_data_repository import RawDataRepository
from src.shared.repositories.base_repository import BaseRepository
from src.shared.repositories.entity_repository import EntityRepository

repositories = [
  AssetRepository,
  AssetSnapshotRepository,
  PortfolioSnapshotRepository,
  ItemSQLQueryRepository,
  RawDataRepository,
  BaseRepository,
  EntityRepository,
]