import logging
from typing import Iterable

from repository.base_repository import BaseRepository
from database.client import DatabaseClient


logging.basicConfig(level=logging.INFO, filename='logs/info.log', filemode='a', format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

# Data access Repository
class EntityRepository(BaseRepository):
    def __init__(self, entity_name, client: DatabaseClient):
        self.client = client
        self.entity_name = entity_name

    def insert(self, records: Iterable[dict]):
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

    def upsert(self, records: Iterable[dict], unique_key: str) -> None:
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

            return res
            logging.info(f"Upserted record into {self.entity_name}")

    def select_by_id(self, id: int):
        sql = f"SELECT * FROM {self.entity_name} WHERE id = :id"
        params = {"id": id}

        logging.info(f"Selecting record from {self.entity_name} with id: {id}")
        with self.client as client:
            result = client.execute(sql, params)

        logging.info(f"Count of records fetched: {result.rowcount}")
        # help(result)
        return result.first()

    def select_all(self):
        sql = f"SELECT * FROM {self.entity_name}"

        logging.info(f"Selecting all records from {self.entity_name}")


        with self.client as client:
            result = client.execute(sql)
        
        logging.info(f"Count of records fetched: {result.rowcount}")
        return result.fetchall()

    def update(self, id: int, data: dict):
        column_names = ", ".join(data.keys())
        placeholders = ", ".join(f":{key}" for key in data.keys())
        sql = f"UPDATE {self.entity_name} SET {column_names} WHERE id = :id"
        params = {**data, "id": id}

        logging.info(f"Updating record in {self.entity_name} with id: {id}")

        with self.client as client:
            res = client.execute(sql, params)

        logging.info(f"Updated record in {self.entity_name} with id: {id}")
        return res

    def delete(self, id: int):
        sql = f"DELETE FROM {self.entity_name} WHERE id = :id"
        params = {"id": id}

        logging.info(f"Deleting record from {self.entity_name} with id: {id}")

        with self.client as client:
            res = client.execute(sql, params)

        logging.info(f"Deleted record from {self.entity_name} with id: {id}")
        return res