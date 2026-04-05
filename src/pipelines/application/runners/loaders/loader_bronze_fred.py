import os
import uuid
import json
from datetime import datetime
from dotenv import load_dotenv

from ....application.policies import FullLoader
from shared.database.client import SQLModelClient

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


class FullLoaderPostgresFred(FullLoader):

    def __init__(self, table_name):
        super().__init__(table_name)
        self._client = SQLModelClient(DATABASE_URL)

    def _create_partition(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS {self._partition_name}
            PARTITION OF {self._table_name}
            FOR VALUES FROM (:day) TO (:next_day);
        """
        with self._client as client:
            client.execute(sql, {"day": self._day, "next_day": self._next_day})

    def _loader(self, data: list[dict]):
        """
        data: list of dicts with keys: series_id, observations, observation_start
        Inserts one row per series per run.
        """
        ingested_date = datetime.now().date()
        sql = f"""
            INSERT INTO {self._table_name} (
                id,
                series_id,
                ingested_date,
                observation_start,
                observations
            )
            VALUES (
                :id,
                :series_id,
                :ingested_date,
                :observation_start,
                :observations
            )
        """
        with self._client as client:
            for record in data:
                params = {
                    "id": str(uuid.uuid4()),
                    "series_id": record["series_id"],
                    "ingested_date": ingested_date,
                    "observation_start": record["observation_start"],
                    "observations": json.dumps(record["observations"]),
                }
                client.execute(sql, params=params)
