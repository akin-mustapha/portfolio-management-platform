from abc import ABC, abstractmethod
from database.client import SQLModelClient
import logging
from datetime import datetime, UTC

from repository.entity_repository import EntityRepository

logging.basicConfig(level=logging.INFO, filename='logs/info.log', filemode='a', format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

    

class RawDataRepositorySQLite(EntityRepository):
    def __init__(self, entity_name, client):
        super().__init__(entity_name, client)
        self.client = client
        self.entity_name = entity_name

    def select_by_id(self, source: str):
        logging.info(f"Fetching raw data from source: {source}")
        with self.client as client:
            result = client.execute("""
                                    SELECT *
                                    FROM raw_data
                                    WHERE   source = :source
                                        AND is_processed = :is_processed
                                    ORDER BY id
                                    LIMIT 1""", 
                                {"source": source, "is_processed": False})
            data = result.fetchall()
        logging.info(f"Fetched {len(data)} records from source: {source}")
        return data

    # def process_raw_data(self, id: int):
    #     logging.info(f"Processing raw data with id: {id}")
    #     with self.client as client:
    #         result = client.execute(
    #             """UPDATE raw_data
    #                 SET is_processed = :is_processed
    #                   , processed_datetime = :processed_datetime
    #                 WHERE id = :id""",
    #             {"is_processed": True, "id": id, "processed_datetime": datetime.now(UTC)})

    #     logging.info(f"Raw data with id: {id} marked as processed")
        

if __name__ == "__main__":
    database_client = SQLModelClient(database_url="sqlite:///./data/trading212.db")
    raw_data_repo = RawDataRepositorySQLite(client=database_client)
    

    # Example usage
    raw_data_repo.save_raw_data(source="trading212", payload='{"example": "data"}')
    data = raw_data_repo.get_raw_data(source="trading212")

    for record in data:
        raw_data_repo.process_raw_data(id=record.id)