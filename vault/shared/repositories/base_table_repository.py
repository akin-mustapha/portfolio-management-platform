import logging
import os
from collections.abc import Iterable

from dotenv import load_dotenv

from ..database.client import SQLModelClient
from .interface import RepositoryInterface

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


class BaseTableRepository(RepositoryInterface):
    def __init__(
        self,
        entity_name: str,
        schema_name: str | None = None,
        field_map: dict[str, str] | None = None,
    ):
        self._entity_name = entity_name
        self._schema_name = schema_name
        self._client = SQLModelClient(DATABASE_URL or "")
        self._field_map = field_map or {}

    @property
    def entity_name(self):
        return self._entity_name

    @property
    def schema_name(self):
        return self._schema_name

    @property
    def _table(self) -> str:
        if self._schema_name:
            return f"{self._schema_name}.{self._entity_name}"
        return self._entity_name

    def _to_db_fields(self, data: dict) -> dict:
        if not self._field_map:
            return data
        return {self._field_map.get(k, k): v for k, v in data.items()}

    def _from_db_fields(self, data: dict) -> dict:
        if not self._field_map:
            return data
        reverse_map = {v: k for k, v in self._field_map.items()}
        return {reverse_map.get(k, k): v for k, v in data.items()}

    def insert(self, records: Iterable[dict]):
        if not isinstance(records, list):
            records = list(records)

        for record in records:
            record = self._to_db_fields(record)
            columns = ", ".join(record.keys())
            placeholders = ", ".join(f":{k}" for k in record.keys())
            sql = f"INSERT INTO {self._table} ({columns}) VALUES ({placeholders})"
            self._client.execute(sql, record)
            logging.info(f"Inserted record into {self._table}")

    def upsert(self, records: Iterable[dict], unique_key: list[str]):
        for record in records:
            record = self._to_db_fields(record)
            db_unique_key = [self._field_map.get(k, k) for k in unique_key]
            columns = ", ".join(record.keys())
            placeholders = ", ".join(f":{k}" for k in record.keys())
            updates = ", ".join(f"{k} = :{k}" for k in record.keys() if k not in db_unique_key)
            sql = f"""
              INSERT INTO {self._table} ({columns})
              VALUES ({placeholders})
              ON CONFLICT({", ".join(db_unique_key)}) DO UPDATE SET {updates}
            """
            self._client.execute(sql, record)
            logging.info(f"Upserted record into {self._table}")

    def select(self, params: dict):
        db_params = self._to_db_fields(params)
        filters = [f"{key} = :{key}" for key in db_params.keys()]
        sql = f"SELECT * FROM {self._table} WHERE {' AND '.join(filters)}"
        rows = self._client.execute(sql, db_params)
        if not rows:
            return None
        return self._from_db_fields(dict(rows[0]._mapping))

    def select_all(self):
        sql = f"SELECT * FROM {self._table}"
        rows = self._client.execute(sql)
        return [self._from_db_fields(dict(r._mapping)) for r in rows]

    def select_all_by(self, params: dict):
        db_params = self._to_db_fields(params)
        filters = [f"{key} = :{key}" for key in db_params.keys()]
        sql = f"SELECT * FROM {self._table} WHERE {' AND '.join(filters)}"
        rows = self._client.execute(sql, db_params)
        return [self._from_db_fields(dict(r._mapping)) for r in rows]

    def update(self, params: dict, data: dict):
        db_params = self._to_db_fields(params)
        db_data = self._to_db_fields(data)
        set_clause = ", ".join(f"{k} = :{k}" for k in db_data.keys())
        where_clause = " AND ".join(f"{k} = :{k}" for k in db_params.keys())
        sql = f"UPDATE {self._table} SET {set_clause} WHERE {where_clause}"
        combined_params = {**db_data, **db_params}
        self._client.execute(sql, combined_params)
        logging.info(f"Updated record in {self._table}")

    def delete(self, params: dict):
        db_params = self._to_db_fields(params)
        where_clause = " AND ".join(f"{k} = :{k}" for k in db_params.keys())
        sql = f"DELETE FROM {self._table} WHERE {where_clause}"
        self._client.execute(sql, db_params)
        logging.info(f"Deleted record from {self._table}")
