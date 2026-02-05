import os
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict
from dotenv import load_dotenv
from datetime import datetime, timezone
from src.shared.database.client import SQLModelClient
from src.services.ingestion.app.interfaces import RawDataRepositoryInterface

logging.basicConfig(
    level=logging.INFO,
    filename='logs/info.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s'
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite").lower()

# ---------------------------
# SQLite Implementation
# ---------------------------
class SQLiteRawDataRepository(RawDataRepositoryInterface):
    def __init__(self):
        self._client = SQLModelClient(DATABASE_URL)

    def insert(self, record: Dict) -> Dict:
        columns = ", ".join(record.keys())
        placeholders = ", ".join(f":{k}" for k in record.keys())
        sql = f"INSERT INTO raw_data ({columns}) VALUES ({placeholders})"

        logging.debug(f"Executing query: {sql} with params: {record}")
        with self._client as client:
            res = client.execute(sql, record)

        logging.info(f"Inserted record into raw_data")
        return {**record, "id": res.lastrowid}

    def select(self, source: str) -> Optional[Dict]:
        sql = """
            SELECT id, payload
            FROM raw_data
            WHERE source = :source AND is_processed = :is_processed
            ORDER BY id
            LIMIT 1
        """
        logging.info(f"Fetching raw data from source: {source}")
        with self._client as client:
            result = client.execute(sql, {"source": source, "is_processed": False})
            data = result.first()
        logging.info(f"Fetched record: {data}")
        return data

    def process_raw_data(self, id: int) -> None:
        sql = """
            UPDATE raw_data
               SET is_processed = :is_processed,
                   processed_datetime = :processed_datetime
             WHERE id = :id
        """
        logging.info(f"Processing raw data with id: {id}")
        with self._client as client:
            client.execute(sql, {"is_processed": True, "processed_datetime": datetime.now(timezone.utc), "id": id})


# ---------------------------
# Postgres Implementation
# ---------------------------
class PostgresRawDataRepository(RawDataRepositoryInterface):
    def __init__(self, schema_name: str = None):
        self._client = SQLModelClient(DATABASE_URL)
        self._table_name = f"{'staging'}.raw_data"

    def insert(self, record: Dict) -> Dict:
        columns = ", ".join(record.keys())
        placeholders = ", ".join(f":{k}" for k in record.keys())
        sql = f"INSERT INTO {self._table_name} ({columns}) VALUES ({placeholders}) RETURNING id"

        logging.debug(f"Executing query: {sql} with params: {record}")
        with self._client as client:
            res = client.execute(sql, record)
            new_id = res.fetchone()[0]

        logging.info(f"Inserted record into {self._table_name}")
        return {**record, "id": new_id}

    def select(self, source: str) -> Optional[Dict]:
        sql = f"""
            SELECT id, payload
            FROM {self._table_name}
            WHERE source = :source AND is_processed = :is_processed
            ORDER BY id
            LIMIT 1
        """
        logging.info(f"Fetching raw data from source: {source}")
        with self._client as client:
            result = client.execute(sql, {"source": source, "is_processed": False})
            data = result.first()
        logging.info(f"Fetched record: {data}")
        return data

    def process_raw_data(self, id: int) -> None:
        sql = f"""
            UPDATE {self._table_name}
               SET is_processed = :is_processed,
                   processed_datetime = :processed_datetime
             WHERE id = :id
        """
        logging.info(f"Processing raw data with id: {id}")
        with self._client as client:
            client.execute(sql, {"is_processed": True, "processed_datetime": datetime.now(timezone.utc), "id": id})


# ---------------------------
# Factory
# ---------------------------
class RawDataRepositoryFactory:
    registry = {
        "sqlite": SQLiteRawDataRepository,
        "postgres": PostgresRawDataRepository
    }

    @classmethod
    def get_repository(cls, schema_name: str = None) -> RawDataRepositoryInterface:
        repo_class = cls.registry.get(DATABASE_TYPE)
        if not repo_class:
            raise ValueError(f"No raw data repository found for type: {DATABASE_TYPE}")
        if DATABASE_TYPE == "postgres":
            return repo_class(schema_name)
        return repo_class()