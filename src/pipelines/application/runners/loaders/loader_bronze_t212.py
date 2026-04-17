import os
import uuid
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text

from ....application.policies import FullLoader

from shared.database.client import SQLModelClient
from shared.database.query_loader import load_query

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

_QUERIES_DIR = Path(__file__).parent.parent.parent.parent / "infrastructure" / "queries"

# Partition by date
# Create exposition abstraction - view
# Extract
# Load


class FullLoaderPostgresT212(FullLoader):

    def __init__(self, table_name):
        super().__init__(table_name)
        self._client = SQLModelClient(DATABASE_URL)

    def _loader(self, data: list[dict]):
        ingested_time = datetime.now().date()
        sql = load_query(_QUERIES_DIR / "bronze" / "t212_snapshot_insert.sql").format(
            table_name=self._table_name
        )

        params = {
            "id": str(uuid.uuid4()),
            "ingested_date": ingested_time,
            "account_data": json.dumps(data.get("account_data", {})),
            "position_data": json.dumps(data.get("position_data", [])),
        }

        with self._client as client:
            client.execute(sql, params=params)

    def _create_partition(self):
        sql = load_query(_QUERIES_DIR / "bronze" / "create_partition.sql").format(
            partition_name=self._partition_name,
            table_name=self._table_name,
        )

        with self._client as client:
            client.execute(sql, {"day": self._day, "next_day": self._next_day})

        return None

    def _exposition_abstraction(self):
        drop_account = "DROP VIEW IF EXISTS raw.v_bronze_account"
        create_account = load_query(_QUERIES_DIR / "bronze" / "v_bronze_account.sql").format(
            table_name=self._table_name
        )

        drop_position = "DROP VIEW IF EXISTS raw.v_bronze_position"
        create_position = load_query(_QUERIES_DIR / "bronze" / "v_bronze_position.sql").format(
            table_name=self._table_name
        )

        with self._client.engine.connect() as conn:
            conn.execute(text(drop_account))
            conn.execute(text(create_account))
            conn.execute(text(drop_position))
            conn.execute(text(create_position))
            conn.commit()
