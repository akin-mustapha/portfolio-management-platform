import os
from src.services.portfolio.infra.repositories.tag_respository import PostgresTagRepository, SQLiteTagRepository
from src.services.portfolio.infra.repositories.asset_repository import PostgresAssetRepository, SQLiteAssetRepository
from src.services.portfolio.infra.repositories.asset_tag_repository import PostgresAssetTagRepository, SQLiteAssetTagRepository
from src.services.portfolio.infra.repositories.industry_repository import PostgresIndustryRepository, SQLiteIndustryRepository
from src.services.portfolio.infra.repositories.sector_repository import PostgresSectorRepository, SQLiteSectorRepository

from src.services.portfolio.infra.repositories.category_repository import PostgresCategoryRepository, SQLiteCategoryRepository

class RepositoryFactory:
    # Registry: table_name -> {db_type -> repository class}
    registry = {
        "asset": {
            "postgres": PostgresAssetRepository,
            "sqlite": SQLiteAssetRepository,
        },
        "asset_tag": {
            "postgres": PostgresAssetTagRepository,
            "sqlite": SQLiteAssetTagRepository,
        },
        "category": {
            "postgres": PostgresCategoryRepository,
            "sqlite": SQLiteCategoryRepository,
        }
        "industry": {
          "postgres": PostgresIndustryRepository, 
          "sqlite": SQLiteIndustryRepository
        },
        "sector": {
            "postgres": PostgresSectorRepository,
            "sqlite": SQLiteSectorRepository,
        },
        "tag": {
            "postgres": PostgresTagRepository,
            "sqlite": SQLiteTagRepository,
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