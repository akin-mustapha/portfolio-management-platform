from src.services.ingestion_service.infrastructure.repositories.asset_repository import AssetRepository
from src.services.ingestion_service.infrastructure.repositories.asset_snapshot_repository import AssetSnapshotRepository
from src.services.ingestion_service.infrastructure.repositories.portfolio_snapshot_repository import PortfolioSnapshotRepository
from src.services.ingestion_service.infrastructure.repositories.query_repository import ItemSQLQueryRepository
from src.services.ingestion_service.infrastructure.repositories.raw_data_repository import RawDataRepository
from src.services.ingestion_service.infrastructure.repositories.base_repository import BaseRepository
from src.services.ingestion_service.infrastructure.repositories.entity_repository import EntityRepository

repositories = [
  AssetRepository,
  AssetSnapshotRepository,
  PortfolioSnapshotRepository,
  ItemSQLQueryRepository,
  RawDataRepository,
  BaseRepository,
  EntityRepository,
]