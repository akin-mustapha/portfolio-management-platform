import os
import logging
from dotenv import load_dotenv
from typing import Dict, Iterable
from ..database.client import SQLModelClient
from .interface import RepositoryInterface

logging.basicConfig(
    level=logging.INFO,
    filename="logs/info.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


class BaseTableRepository(RepositoryInterface):
    def __init__(
        self,
        entity_name: str,
        schema_name: str = None,
        field_map: Dict[str, str] = None,
    ):
        """
        :param entity_name: Table name in DB
        :param schema_name: Schema name (Postgres only; omit for SQLite)
        :param field_map: Mapping from domain name -> DB column name
        """
        self._entity_name = entity_name
        self._schema_name = schema_name
        self._client = SQLModelClient(DATABASE_URL)
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

    def _to_db_fields(self, data: Dict) -> Dict:
        """Map domain-friendly fields to DB column names. Passthrough when no field_map."""
        if not self._field_map:
            return data
        return {self._field_map.get(k, k): v for k, v in data.items()}

    def _from_db_fields(self, data: Dict) -> Dict:
        """Map DB column names back to domain-friendly fields. Passthrough when no field_map."""
        if not self._field_map:
            return data
        reverse_map = {v: k for k, v in self._field_map.items()}
        return {reverse_map.get(k, k): v for k, v in data.items()}

    def insert(self, records: Iterable[Dict]):
        if not isinstance(records, list):
            records = [records]

        res = None
        for record in records:
            record = self._to_db_fields(record)
            columns = ", ".join(record.keys())
            placeholders = ", ".join(f":{k}" for k in record.keys())
            sql = f"INSERT INTO {self._table} ({columns}) VALUES ({placeholders})"
            logging.debug(f"Executing query: {sql} with params: {record}")
            with self._client as client:
                res = client.execute(sql, record)
                logging.info(f"Inserted record into {self._table}")
        return res

    def upsert(self, records: Iterable[Dict], unique_key: list[str]):
        res = None
        for record in records:
            record = self._to_db_fields(record)
            db_unique_key = [self._field_map.get(k, k) for k in unique_key]
            columns = ", ".join(record.keys())
            placeholders = ", ".join(f":{k}" for k in record.keys())
            updates = ", ".join(
                f"{k} = :{k}" for k in record.keys() if k not in db_unique_key
            )
            sql = f"""
              INSERT INTO {self._table} ({columns})
              VALUES ({placeholders})
              ON CONFLICT({', '.join(db_unique_key)}) DO UPDATE SET {updates}
            """
            logging.debug(f"Executing query: {sql} with params: {record}")
            with self._client as client:
                res = client.execute(sql, record)
                logging.info(f"Upserted record into {self._table}")
        return res

    def select(self, params: Dict):
        db_params = self._to_db_fields(params)
        filters = [f"{key} = :{key}" for key in db_params.keys()]
        sql = f"SELECT * FROM {self._table} WHERE {' AND '.join(filters)}"
        logging.info(f"Selecting record from {self._table}")
        with self._client as client:
            result = client.execute(sql, db_params)
        logging.info(f"Count of records fetched: {result.rowcount}")
        row = result.first()
        if row is None:
            return None
        return self._from_db_fields(dict(row._mapping))

    def select_all(self):
        sql = f"SELECT * FROM {self._table}"
        logging.info(f"Selecting all records from {self._table}")
        with self._client as client:
            result = client.execute(sql)
        results = result.fetchall()
        logging.info(f"Count of records fetched: {result.rowcount}")
        return [self._from_db_fields(dict(r._mapping)) for r in results]

    def select_all_by(self, params: Dict):
        db_params = self._to_db_fields(params)
        filters = [f"{key} = :{key}" for key in db_params.keys()]
        sql = f"SELECT * FROM {self._table} WHERE {' AND '.join(filters)}"
        logging.info(f"Selecting records from {self._table}")
        with self._client as client:
            result = client.execute(sql, db_params)
        results = result.fetchall()
        logging.info(f"Count of records fetched: {result.rowcount}")
        return [self._from_db_fields(dict(r._mapping)) for r in results]

    def update(self, params: Dict, data: Dict):
        db_params = self._to_db_fields(params)
        db_data = self._to_db_fields(data)
        set_clause = ", ".join(f"{k} = :{k}" for k in db_data.keys())
        where_clause = " AND ".join(f"{k} = :{k}" for k in db_params.keys())
        sql = f"UPDATE {self._table} SET {set_clause} WHERE {where_clause}"
        combined_params = {**db_data, **db_params}
        logging.info(f"Updating record in {self._table}")
        with self._client as client:
            res = client.execute(sql, combined_params)
        logging.info(f"Updated record in {self._table}")
        return res

    def delete(self, params: Dict):
        db_params = self._to_db_fields(params)
        where_clause = " AND ".join(f"{k} = :{k}" for k in db_params.keys())
        sql = f"DELETE FROM {self._table} WHERE {where_clause}"
        logging.info(f"Deleting record from {self._table}")
        with self._client as client:
            res = client.execute(sql, db_params)
        logging.info(f"Deleted record from {self._table}")
        return res
