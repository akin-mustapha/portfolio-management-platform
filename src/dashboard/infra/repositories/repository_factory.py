import os
from .query_repository import PostgresAssetQueryRepository, SQLiteAssetQueryRepository
from .query_repository import PostgresSnapshotQueryRepository, SQLiteSnapshotQueryRepository

class RepositoryFactory:
    # Registry: table_name -> {db_type -> repository class}
    registry = {
        "asset_query": {
            "postgres": PostgresAssetQueryRepository,
            "sqlite": SQLiteAssetQueryRepository,
        },
        "snapshot_query": {
            "postgres": PostgresSnapshotQueryRepository,
            "sqlite": SQLiteSnapshotQueryRepository,
        }
    }

    @classmethod
    def get(cls, table_name: str, db_type: str = None):
        db_type = db_type or os.getenv("DATABASE_TYPE", "sqlite").lower()
        table_entry = cls.registry.get(table_name)
        if not table_entry:
            raise ValueError(f"No repository registered for table: {table_name}")
        repo_class = table_entry.get(db_type)
        if not repo_class:
            raise ValueError(f"No repository for table '{table_name}' and DB type '{db_type}'")
        return repo_class()