import logging
from typing import Iterable, Dict

from repository.base_repository import BaseRepository
from database.client import DatabaseClient


logging.basicConfig(level=logging.INFO, filename='logs/info.log', filemode='a', format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

# Data access Repository
class EntityRepository(BaseRepository):
    def __init__(self, entity_name, client: DatabaseClient):
        self.client = client
        self.entity_name = entity_name

    def select(self, params: Dict):
        filters = [f'{key} = :{key}' for key in params.keys()]
        filters_str = ' AND '.join(filters)

        sql = f"SELECT * FROM {self.entity_name} WHERE {filters_str}"

        logging.info(f"Selecting record from {self.entity_name}")

        with self.client as client:
            result = client.execute(sql, params)

        logging.info(f"Count of records fetched: {result.rowcount}")
        return result.first()

    def select_all(self):
        sql = f"SELECT * FROM {self.entity_name}"

        logging.info(f"Selecting all records from {self.entity_name}")
        with self.client as client:
            result = client.execute(sql)
        
        logging.info(f"Count of records fetched: {result.rowcount}")
        return result.fetchall()
    
    def insert(self, records: Iterable[Dict]):
        for record in records:
            logging.debug(f"Preparing to insert record into {self.entity_name}")

            column_names = ", ".join(record.keys())
            placeholders = ", ".join(f":{key}" for key in record.keys())

            sql = f"INSERT INTO {self.entity_name} ({column_names}) VALUES ({placeholders})"

            logging.debug(f"Executing query: {sql} with params: {record}")
            with self.client as client:
                res = client.execute(sql, record)

            logging.info(f"Inserted record into {self.entity_name}")
            return res

    def upsert(self, records: Iterable[Dict], unique_key: str) -> None:
        for record in records:
            logging.debug(f"Preparing to upsert record into {self.entity_name}")

            column_names = ", ".join(record.keys())
            placeholders = ", ".join(f":{key}" for key in record.keys())
            update_placeholders = ", ".join(f"{key} = :{key}" for key in record.keys() if key != unique_key)

            sql = f"""
                INSERT INTO {self.entity_name} ({column_names}) 
                VALUES ({placeholders})
                ON CONFLICT({unique_key}) 
                DO UPDATE SET {update_placeholders}
            """

            logging.debug(f"Executing query: {sql} with params: {record}")
            with self.client as client:
                res = client.execute(sql, record)

            logging.info(f"Upserted record into {self.entity_name}")
            return res

    def update(self, params: Dict, data: Dict):
        filters = [f'{key} = :{key}' for key in params.keys()]
        filters_str = ' AND '.join(filters)

        columns = [f'{key} = {val}' for key, val in data.items()]
        column_names = ", ".join(columns)
        placeholders = ", ".join(f":{key}" for key in data.keys())
        sql = f"UPDATE {self.entity_name} SET {column_names} WHERE {filters_str}"

        logging.info(f"Updating record in {self.entity_name}")
        with self.client as client:
            res = client.execute(sql, params)

        logging.info(f"Updated record in {self.entity_name}")
        return res

    def delete(self, params: Dict):
        filters = [f'{key} = :{key}' for key in params.keys()]
        filters_str = ' AND '.join(filters)

        sql = f"DELETE FROM {self.entity_name} WHERE {filters_str}"

        logging.info(f"Deleting record from {self.entity_name}")
        with self.client as client:
            res = client.execute(sql, params)

        logging.info(f"Deleted record from {self.entity_name}")
        return res