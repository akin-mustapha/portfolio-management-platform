import os
import logging
from dotenv import load_dotenv
from typing import Iterable, Dict

from src.shared.database.client import SQLModelClient
from src.services.ingestion.app.interfaces.interface_repository import Repository
# TODO - USE INTERFACE + DEP INJECTION
from src.services.ingestion.app.interfaces.interace_database_client import DatabaseClient
from .schema import schema

logging.basicConfig(
    level=logging.INFO,
    filename='logs/info.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s'
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite").lower()


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