from src.services.portfolio.infra.repositories.query_repository import PostgresAssetQueryRepository, SQLiteAssetQueryRepository, SQLiteSnapshotQueryRepository, PostgresSnapshotQueryRepository
from src.services.portfolio.infra.repositories.entity_repository import SQLiteEntityRepository
from src.services.portfolio.infra.repositories.entity_repository import EntityRepositoryFactory

repositories = [
  PostgresAssetQueryRepository,
  SQLiteAssetQueryRepository,
  SQLiteSnapshotQueryRepository,
  PostgresSnapshotQueryRepository,
  SQLiteEntityRepository,
  EntityRepositoryFactory,

]