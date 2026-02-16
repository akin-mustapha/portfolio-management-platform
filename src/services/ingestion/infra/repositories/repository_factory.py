import os
import logging
from dotenv import load_dotenv
from typing import Iterable, Dict

from src.services.ingestion.infra.repositories.repository_postgres import PostgresRepository
from src.services.ingestion.infra.repositories.repository_sqlite import SQLiteRespository
from src.services.ingestion.app.interfaces.interface_repository import Repository

logging.basicConfig(
    level=logging.INFO,
    filename='logs/info.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s'
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite").lower()


class RepositoryFactory:
  registry = {
    "sqlite": SQLiteRespository,
    "postgres": PostgresRepository,
  }

  @classmethod
  def get(cls, entity_name: str, schema_name: str = None, field_mapping: list[Dict] = None) -> Repository:
    repo_class = cls.registry.get(DATABASE_TYPE)
    if not repo_class:
      raise ValueError(
        f"No repository for database type: {DATABASE_TYPE}")
    return repo_class(entity_name, schema_name, field_mapping)
