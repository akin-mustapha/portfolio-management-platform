import os

from shared.repositories.interface import RepositoryInterface

from .repository_postgres import PostgresRepository
from .repository_sqlite import SQLiteRepository

DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite").lower()


class RepositoryFactory:
    registry = {
        "sqlite": SQLiteRepository,
        "postgres": PostgresRepository,
    }

    @classmethod
    def get(
        cls, entity_name: str, schema_name: str | None = None, field_map: dict[str, str] | None = None
    ) -> RepositoryInterface:
        repo_class = cls.registry.get(DATABASE_TYPE)
        if not repo_class:
            raise ValueError(f"No repository for database type: {DATABASE_TYPE}")
        return repo_class(entity_name, schema_name, field_map)
