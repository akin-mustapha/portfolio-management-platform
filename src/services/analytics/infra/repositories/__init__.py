from src.infra.repositories.query_repository import ItemSQLQueryRepository
from src.infra.repositories.raw_data_repository import RawDataRepositoryFactory
from src.infra.repositories.entity_repository import SQLiteEntityRepository
from src.infra.repositories.entity_repository import EntityRepositoryFactory

repositories = [
  ItemSQLQueryRepository,
  RawDataRepositoryFactory,
  SQLiteEntityRepository,
  EntityRepositoryFactory,

]