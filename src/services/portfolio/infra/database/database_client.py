import os
import logging
from functools import wraps
from dotenv import load_dotenv
from typing import Iterable, Dict
from abc import ABC, abstractmethod
from services.portfolio.app.interfaces import Repostiory

from shared.database.client import SQLModelClient
logging.basicConfig(
    level=logging.INFO,
    filename='logs/info.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s'
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite").lower()



def schema(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):

        if not getattr(self, "_field_mapping", None):
            return method(self, *args, **kwargs)

        def map_dict(data: dict):
            return {
                self._field_mapping.get(k, k): v
                for k, v in data.items()
            }

        # Map records (list or dict)
        if "records" in kwargs and kwargs["records"] is not None:
            records = kwargs["records"]
            if isinstance(records, list):
                kwargs["records"] = [map_dict(r) for r in records]
            elif isinstance(records, dict):
                kwargs["records"] = map_dict(records)

        # Map params
        if "params" in kwargs and kwargs["params"] is not None:
            kwargs["params"] = map_dict(kwargs["params"])

        # Map unique_key
        if "unique_key" in kwargs and kwargs["unique_key"] is not None:
            kwargs["unique_key"] = [
                self._field_mapping.get(k, k)
                for k in kwargs["unique_key"]
            ]

        return method(self, *args, **kwargs)

    return wrapper

class SQLiteRespository(Repository):
  _client = SQLModelClient(DATABASE_URL)
  
  @schema
  def select(self, params: Dict):
    filters = [f"{key} = :{key}" for key in params.keys()]
    sql = f"""
      SELECT *
      FROM {self._entity_name}
      WHERE {' AND '.join(filters)}
    """
    logging.info(f"Selecting record from {self._entity_name}")
    with self._client as client:
      result = client.execute(sql, params)
    logging.info(f"Count of records fetched: {result.rowcount}")
    return result.first()

  @schema
  def select_all(self):
    sql = f"""
      SELECT *
      FROM {self._entity_name}
    """
    logging.info(f"Selecting all records from {self._entity_name}")
    with self._client as client:
      result = client.execute(sql)
    logging.info(f"Count of records fetched: {result.rowcount}")
    return result.fetchall()

  @schema
  def insert(self, records: Iterable[Dict]):
    """
      Insert
    """
    if not isinstance(records, list):
      records = [records]
    
    result = []
    for record in records:
      columns = ", ".join(record.keys())
      placeholders = ", ".join(f":{k}" for k in record.keys())
      sql = f"""
        INSERT INTO {self._entity_name} ({columns})
        VALUES ({placeholders})
      """
      logging.debug(f"Executing query: {sql} with params: {record}")
      with self._client as client:
        res = client.execute(sql, record)
        result.append(res)
      logging.info(f"Inserted record into {self._entity_name}")
    return result

  @schema
  def upsert(self, records: Iterable[Dict], unique_key: list[str]):
    result = []
    for record in records:
      columns = ", ".join(record.keys())
      placeholders = ", ".join(f":{k}" for k in record.keys())
      updates = ", ".join(
        f"{k} = :{k}" for k in record.keys() if k not in unique_key)
      sql = f"""
        INSERT INTO {self._entity_name} ({columns})
        VALUES ({placeholders})
        ON CONFLICT({', '.join(unique_key)}) DO UPDATE SET {updates}
      """
      logging.debug(f"Executing query: {sql} with params: {record}")
      with self._client as client:
        res = client.execute(sql, record)
        result.append(res)
      logging.info(f"Upserted record into {self._entity_name}")
    return result

  @schema
  def update(self, records: Dict, params: Dict):
    set_clause = ", ".join(f"{k} = :{k}" for k in records.keys())
    where_clause = " AND ".join(f"{k} = :{k}" for k in params.keys())
    sql = f"""
      UPDATE {self._entity_name}
        SET {set_clause}
        WHERE {where_clause}
    """
    combined_params = {**records, **params}
    logging.info(f"Updating record in {self._entity_name}")
    with self._client as client:
      res = client.execute(sql, combined_params)
    logging.info(f"Updated record in {self._entity_name}")
    return res

  @schema
  def delete(self, params: Dict):
    where_clause = " AND ".join(f"{k} = :{k}" for k in params.keys())
    sql = f"""
        DELETE t1
        FROM {self._entity_name} t1
        WHERE {where_clause}
      """
    logging.info(f"Deleting record from {self._entity_name}")
    with self._client as client:
      res = client.execute(sql, params)
    logging.info(f"Deleted record from {self._entity_name}")
    return res


class PostgresRepository(Repository):
  _client = SQLModelClient(DATABASE_URL)

  @schema
  def select(self, params: Dict):
    where_clause = " AND ".join(f"{k} = :{k}" for k in params.keys())
    sql = f"""
      SELECT *
      FROM {self._entity_name}
      WHERE {where_clause}
    """
    logging.info(f"Selecting record from {self._entity_name}")

    with self._client as client:
      result = client.execute(sql, params)
      row = result.first()
      logging.info(f"Count of records fetched: {result.rowcount}")
      
      if not row:
        return None
      return dict(row._mapping)
  
  @schema
  def select_all(self):
    sql = f"""
      SELECT *
      FROM {self._entity_name}
    """
    logging.info(f"Selecting all records from {self._entity_name}")
    with self._client as client:
      result = client.execute(sql)
    logging.info(f"Count of records fetched: {result.rowcount}")
    return result.fetchall()

  @schema
  def insert(self, records: Iterable[Dict]):
    if not isinstance(records, list):
      records = [records]
    result = []
    for record in records:
      columns = ", ".join(record.keys())
      placeholders = ", ".join(f":{k}" for k in record.keys())
      sql = f"""
        INSERT INTO {self._entity_name} ({columns})
        VALUES ({placeholders})
      """
      logging.debug(f"Executing query: {sql} with params: {record}")
      with self._client as client:
        res = client.execute(sql, record)
        result.append(res)
      logging.info(f"Inserted record into {self._entity_name}")
    return result

  @schema
  def upsert(self, records: Iterable[Dict], unique_key: list[str]):
    result = []
    for record in records:
      columns = ", ".join(record.keys())
      placeholders = ", ".join(f":{k}" for k in record.keys())
      updates = ", ".join(
        f"{k} = :{k}"
        for k in record.keys()
        if k not in unique_key
      )
      sql = f"""
        INSERT INTO {self._entity_name} ({columns})
        VALUES ({placeholders})
        ON CONFLICT({', '.join(unique_key)}) DO UPDATE SET {updates}
      """
      logging.debug(f"Executing query: {sql} with params: {record}")
      with self._client as client:
        res = client.execute(sql, record)
        result.append(res)
      logging.info(f"Upserted record into {self._entity_name}")
      return result

  @schema
  def update(self, records: Dict, params: Dict):
    set_clause = ", ".join(
      f"{k} = :{k}" 
      for k in records.keys()
    )
    where_clause = " AND ".join(
      f"{k} = :{k}"
      for k in params.keys()
    )
    sql = f"""
      UPDATE {self._entity_name}
      SET {set_clause}
      WHERE {where_clause}
    """
    combined_params = {**records, **params}
    logging.info(f"Updating record in {self._entity_name}")
    with self._client as client:
      res = client.execute(sql, combined_params)
    logging.info(f"Updated record in {self._entity_name}")
    return res

  @schema
  def delete(self, params: Dict):
    where_clause = " AND ".join(
      f"{k} = :{k}"
      for k in params.keys()
    )
    sql = f"""
      DELETE FROM {self._entity_name}
      WHERE {where_clause}
      """
    logging.info(f"Deleting record from {self._entity_name}")
    with self._client as client:
      res = client.execute(sql, params)
    logging.info(f"Deleted record from {self._entity_name}")
    return res


class DatabaseRepositoryFactory:
  registry = {
    "sqlite": SQLiteRespository,
    "postgres": PostgresRepository,
  }

  @classmethod
  def get_repository(cls, entity_name: str, schema_name: str = None) -> Repository:
    repo_class = cls.registry.get(DATABASE_TYPE)
    if not repo_class:
      raise ValueError(
        f"No repository for database type: {DATABASE_TYPE}")
    return repo_class(entity_name, schema_name)
