import os
from src.services.ingestion.infra.repositories.asset_repository import PostgresAssetRepository, SQLiteAssetRepository
from src.services.ingestion.infra.repositories.raw_data_repository import SQLiteRawDataRepository, PostgresRawDataRepository
from src.services.ingestion.infra.repositories.asset_snapshot_repository import PostgresAssetSnapshotRepository, SQLiteAssetSnapshotRepository
from src.services.ingestion.infra.repositories.portfolio_snapshot_repository import PostgresPortfolioSnapshotRepository, SQLitePortfolioSnapshotRepository
from src.services.ingestion.infra.repositories.fact_asset_price_daily_repository import PostgresFactAssetPriceDailyRepository, SQLiteFactAssetPriceDailyRepository

class TableRepositoryFactory:
    # Registry: table_name -> {db_type -> repository class}
    registry = {
        "asset": {
            "postgres": PostgresAssetRepository,
            "sqlite": SQLiteAssetRepository,
        },
        "raw_data": {
            "postgres": PostgresRawDataRepository, 
            "sqlite": SQLiteRawDataRepository
        },
        "asset_snapshot": {
          "postgres": PostgresAssetSnapshotRepository, 
          "sqlite": SQLiteAssetSnapshotRepository
        },
        "portfolio_snapshot": {
          "postgres": PostgresPortfolioSnapshotRepository, 
          "sqlite": SQLitePortfolioSnapshotRepository
        },
        "fact_asset_price_daily": {
          "postgres": PostgresFactAssetPriceDailyRepository, 
          "sqlite": SQLiteFactAssetPriceDailyRepository
        },
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