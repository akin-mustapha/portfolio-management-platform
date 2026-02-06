import os
from src.services.portfolio.infra.repositories.asset_repository import PostgresAssetRepository, SQLiteAssetRepository
from src.services.portfolio.infra.repositories.asset_snapshot_repository import PostgresAssetSnapshotRepository, SQLiteAssetSnapshotRepository

class TableRepositoryFactory:
    # Registry: table_name -> {db_type -> repository class}
    registry = {
        "asset": {
            "postgres": PostgresAssetRepository,
            "sqlite": SQLiteAssetRepository,
        },
        "asset_snapshot": {
          "postgres": PostgresAssetSnapshotRepository, 
          "sqlite": SQLiteAssetSnapshotRepository
        },
        # "portfolio_snapshot": {
        #   "postgres": PostgresPortfolioSnapshotRepository, 
        #   "sqlite": SQLitePortfolioSnapshotRepository
        # },
        # Add more tables here
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