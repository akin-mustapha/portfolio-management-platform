import os
import logging
from dotenv import load_dotenv
from typing import Iterable, Dict

from shared.database.client import SQLModelClient

logging.basicConfig(
    level=logging.INFO,
    filename="logs/info.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite").lower()


class SQLiteDatabaseClient:
    def __init__(self, entity_name):
        self._client = SQLModelClient(DATABASE_URL)
        self._entity_name = entity_name

    def select(self, params: Dict):
        filters = [f"{key} = :{key}" for key in params.keys()]
        sql = f"SELECT * FROM {self._entity_name} WHERE {' AND '.join(filters)}"
        logging.info(f"Selecting record from {self._entity_name}")
        with self._client as client:
            result = client.execute(sql, params)
        logging.info(f"Count of records fetched: {result.rowcount}")
        return result.first()

    def select_all(self):
        sql = f"SELECT * FROM {self._entity_name}"
        logging.info(f"Selecting all records from {self._entity_name}")
        with self._client as client:
            result = client.execute(sql)
        logging.info(f"Count of records fetched: {result.rowcount}")
        return result.fetchall()

    def insert(self, records: Iterable[Dict]):
        if not isinstance(records, list):
            records = [records]
        for record in records:
            columns = ", ".join(record.keys())
            placeholders = ", ".join(f":{k}" for k in record.keys())
            sql = f"INSERT INTO {self._entity_name} ({columns}) VALUES ({placeholders})"
            logging.debug(f"Executing query: {sql} with params: {record}")
            with self._client as client:
                res = client.execute(sql, record)
            logging.info(f"Inserted record into {self._entity_name}")
        return res

    def upsert(self, records: Iterable[Dict], unique_key: list[str]):
        for record in records:
            columns = ", ".join(record.keys())
            placeholders = ", ".join(f":{k}" for k in record.keys())
            updates = ", ".join(
                f"{k} = :{k}" for k in record.keys() if k not in unique_key
            )
            sql = f"""
                INSERT INTO {self._entity_name} ({columns})
                VALUES ({placeholders})
                ON CONFLICT({', '.join(unique_key)}) DO UPDATE SET {updates}
            """
            logging.debug(f"Executing query: {sql} with params: {record}")
            with self._client as client:
                res = client.execute(sql, record)
            logging.info(f"Upserted record into {self._entity_name}")
        return res

    def update(self, params: Dict, data: Dict):
        set_clause = ", ".join(f"{k} = :{k}" for k in data.keys())
        where_clause = " AND ".join(f"{k} = :{k}" for k in params.keys())
        sql = f"UPDATE {self._entity_name} SET {set_clause} WHERE {where_clause}"
        combined_params = {**data, **params}
        logging.info(f"Updating record in {self._entity_name}")
        with self._client as client:
            res = client.execute(sql, combined_params)
        logging.info(f"Updated record in {self._entity_name}")
        return res

    def delete(self, params: Dict):
        where_clause = " AND ".join(f"{k} = :{k}" for k in params.keys())
        sql = f"DELETE FROM {self._entity_name} WHERE {where_clause}"
        logging.info(f"Deleting record from {self._entity_name}")
        with self._client as client:
            res = client.execute(sql, params)
        logging.info(f"Deleted record from {self._entity_name}")
        return res


class PostgresDatabaseClient:
    def __init__(self, entity_name, schema_name: str):
        self._client = SQLModelClient(DATABASE_URL)
        self._entity_name = (
            f"{schema_name}.{entity_name}" if schema_name else entity_name
        )

    def select(self, params: Dict):
        where_clause = " AND ".join(f"{k} = :{k}" for k in params.keys())
        sql = f"SELECT * FROM {self._entity_name} WHERE {where_clause}"
        logging.info(f"Selecting record from {self._entity_name}")

        with self._client as client:
            result = client.execute(sql, params)
            row = result.first()

            logging.info(f"Count of records fetched: {result.rowcount}")
            if not row:
                return None
            return dict(row._mapping)

    def select_all(self):
        sql = f"SELECT * FROM {self._entity_name}"
        logging.info(f"Selecting all records from {self._entity_name}")
        with self._client as client:
            result = client.execute(sql)
        logging.info(f"Count of records fetched: {result.rowcount}")
        return result.fetchall()

    def insert(self, records: Iterable[Dict]):
        if not isinstance(records, list):
            records = [records]
        for record in records:
            columns = ", ".join(record.keys())
            placeholders = ", ".join(f":{k}" for k in record.keys())
            sql = f"INSERT INTO {self._entity_name} ({columns}) VALUES ({placeholders})"
            logging.debug(f"Executing query: {sql} with params: {record}")
            with self._client as client:
                res = client.execute(sql, record)
            logging.info(f"Inserted record into {self._entity_name}")
        return res

    def upsert(self, records: Iterable[Dict], unique_key: list[str]):
        for record in records:
            columns = ", ".join(record.keys())
            placeholders = ", ".join(f":{k}" for k in record.keys())
            updates = ", ".join(
                f"{k} = :{k}" for k in record.keys() if k not in unique_key
            )
            sql = f"""
                INSERT INTO {self._entity_name} ({columns})
                VALUES ({placeholders})
                ON CONFLICT({', '.join(unique_key)}) DO UPDATE SET {updates}
            """
            logging.debug(f"Executing query: {sql} with params: {record}")
            with self._client as client:
                res = client.execute(sql, record)
            logging.info(f"Upserted record into {self._entity_name}")
        return res

    def update(self, params: Dict, data: Dict):
        set_clause = ", ".join(f"{k} = :{k}" for k in data.keys())
        where_clause = " AND ".join(f"{k} = :{k}" for k in params.keys())
        sql = f"UPDATE {self._entity_name} SET {set_clause} WHERE {where_clause}"
        combined_params = {**data, **params}
        logging.info(f"Updating record in {self._entity_name}")
        with self._client as client:
            res = client.execute(sql, combined_params)
        logging.info(f"Updated record in {self._entity_name}")
        return res

    def delete(self, params: Dict):
        where_clause = " AND ".join(f"{k} = :{k}" for k in params.keys())
        sql = f"DELETE FROM {self._entity_name} WHERE {where_clause}"
        logging.info(f"Deleting record from {self._entity_name}")
        with self._client as client:
            res = client.execute(sql, params)
        logging.info(f"Deleted record from {self._entity_name}")
        return res


class DestinationFactory:
    registry = {
        "sqlite": SQLiteDatabaseClient,
        "postgres": PostgresDatabaseClient,
    }

    @classmethod
    def get(cls, entity_name: str, schema_name: str = None):
        repo_class = cls.registry.get(DATABASE_TYPE)
        if not repo_class:
            raise ValueError(f"No repository for database type: {DATABASE_TYPE}")
        return repo_class(entity_name, schema_name)
