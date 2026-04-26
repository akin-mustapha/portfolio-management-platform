import json
import os
import uuid
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from shared.database.client import SQLModelClient
from shared.database.query_loader import load_query

from pipeline.etl.policies import FullLoader

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

_QUERIES_DIR = Path(__file__).parent.parent.parent / "infrastructure" / "queries"


class FullLoaderPostgresFred(FullLoader):
    def __init__(self, table_name):
        super().__init__(table_name)
        self._client = SQLModelClient(DATABASE_URL)

    def _create_partition(self):
        sql = load_query(_QUERIES_DIR / "bronze" / "create_partition.sql").format(
            partition_name=self._partition_name,
            table_name=self._table_name,
        )
        with self._client as client:
            client.execute(sql, {"day": self._day, "next_day": self._next_day})

    def _loader(self, data: list[dict]):
        """
        data: list of dicts with keys: series_id, observations, observation_start
        Inserts one row per series per run.
        """
        ingested_date = datetime.now().date()
        sql = load_query(_QUERIES_DIR / "bronze" / "fred_observations_insert.sql").format(table_name=self._table_name)
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
