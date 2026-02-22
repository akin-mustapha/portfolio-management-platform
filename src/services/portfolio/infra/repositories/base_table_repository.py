from typing import Dict, Iterable
from src.services.portfolio.app.interfaces import RepositoryInterface
import logging

class BaseTableRepository(RepositoryInterface):
    def __init__(self, entity_name: str, schema_name: str = None, field_map: Dict[str, str] = None):
      """
      :param entity_name: Table name in DB
      :param schema_name: Schema name (Postgres only)
      :param field_map: Mapping from domain name -> DB column name
      """
      self._field_map = field_map or {}
      self._entity_repo = EntityRepositoryFactory.get_repository(entity_name, schema_name)

    def _to_db_fields(self, data: Dict) -> Dict:
      """Map domain-friendly fields to DB column names."""
      return {self._field_map.get(k, k): v for k, v in data.items()}

    def _from_db_fields(self, data: Dict) -> Dict:
      """Map DB column names back to domain-friendly fields."""
      reverse_map = {v: k for k, v in self._field_map.items()}
      return {reverse_map.get(k, k): v for k, v in data.items()}

    def insert(self, data: Iterable[Dict]):
      if not isinstance(records, list):
        records = [records]
        
      for record in records:
        
        record = self._to_db_fields(record)
        columns = ", ".join(record.keys())
        placeholders = ", ".join(f":{k}" for k in record.keys())
        
        sql = f"INSERT INTO {self._entity_name} ({columns}) VALUES ({placeholders})"
        
        logging.debug(f"Executing query: {sql} with params: {record}")
        
        with self._client as client:
          res = client.execute(sql, record)
        logging.info(f"Inserted record into {self._entity_name}")

      return res

    def upsert(self, data: Dict, unique_key: list[str]):
      for record in records:
        record = self._to_db_fields(record)
        db_unique_key = [self._field_map.get(k, k) for k in unique_key]
        
        columns = ", ".join(record.keys())
        placeholders = ", ".join(f":{k}" for k in record.keys())
        updates = ", ".join(f"{k} = :{k}" for k in record.keys() if k not in db_unique_key)
        
        sql = f"""
          INSERT INTO {self._entity_name} ({columns})
          VALUES ({placeholders})
          ON CONFLICT({', '.join(db_unique_key)}) DO UPDATE SET {updates}
        """
        
        logging.debug(f"Executing query: {sql} with params: {record}")
        
        with self._client as client:
          res = client.execute(sql, record)
        logging.info(f"Upserted record into {self._entity_name}")
      return res

    def select(self, params: Dict):
      db_params = self._to_db_fields(params)
      result = self._entity_repo.select(db_params)
      if result:
        filters = [f"{key} = :{key}" for key in params.keys()]
        sql = f"SELECT * FROM {self._entity_name} WHERE {' AND '.join(filters)}"
        logging.info(f"Selecting record from {self._entity_name}")
        with self._client as client:
          result = client.execute(sql, params)
        logging.info(f"Count of records fetched: {result.rowcount}")
        result = result.first()
        return self._from_db_fields(dict(result))
      return None

    def select_all(self):
      sql = f"SELECT * FROM {self._entity_name}"
      logging.info(f"Selecting all records from {self._entity_name}")
      with self._client as client:
        result = client.execute(sql)
      results = result.fetchall()
      logging.info(f"Count of records fetched: {result.rowcount}")
      return [self._from_db_fields(dict(r)) for r in results]

    def update(self, params: Dict, data: Dict):
      db_params = self._to_db_fields(params)
      db_data = self._to_db_fields(data)
      set_clause = ", ".join(f"{k} = :{k}" for k in db_data.keys())
      where_clause = " AND ".join(f"{k} = :{k}" for k in db_params.keys())
      sql = f"UPDATE {self._entity_name} SET {set_clause} WHERE {where_clause}"
      combined_params = {**db_data, **db_params}
      logging.info(f"Updating record in {self._entity_name}")
      with self._client as client:
          res = client.execute(sql, combined_params)
      logging.info(f"Updated record in {self._entity_name}")
      return res

    def delete(self, params: Dict):
      db_params = self._to_db_fields(params)
      where_clause = " AND ".join(f"{k} = :{k}" for k in db_params.keys())
      sql = f"DELETE FROM {self._entity_name} WHERE {where_clause}"
      logging.info(f"Deleting record from {self._entity_name}")
      with self._client as client:
          res = client.execute(sql, db_params)
      logging.info(f"Deleted record from {self._entity_name}")
      return res