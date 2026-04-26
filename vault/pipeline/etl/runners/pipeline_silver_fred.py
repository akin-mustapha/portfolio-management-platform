"""
Silver Pipeline for FRED observations

Reads unprocessed rows from raw.fred_observations, normalises each
JSONB observation to a scalar row, validates against FredObservationRecord,
and upserts to staging.fred_observation.
"""

import os
import logging
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

from pipeline.etl.policies import BaseSilverPipeline
from pipeline.etl.protocols import Source, Transformation, Destination
from pipeline.etl.validators.schema_validator import SchemaValidator
from pipeline.domain.schemas.silver.fred_observation import FredObservationRecord
from pipeline.infrastructure.repositories.repository_factory import RepositoryFactory
from pipeline.infrastructure.repositories.dead_letter_destination import (
    DeadLetterDestination,
)

from shared.database.client import SQLModelClient
from shared.database.query_loader import load_query

logging.basicConfig(
    level=logging.INFO,
    filename="logs/info.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

_QUERIES_DIR = Path(__file__).parent.parent.parent / "infrastructure" / "queries"


# ─────────────────────────────────────────────
# Source
# ─────────────────────────────────────────────


class FredSilverSource(Source):
    def __init__(self):
        self._client = SQLModelClient(DATABASE_URL)
        self._sql = load_query(_QUERIES_DIR / "silver" / "fred_silver_source.sql")

    def extract(self) -> list[Any]:
        with self._client as db:
            return db.execute(self._sql)


# ─────────────────────────────────────────────
# Transformation
# ─────────────────────────────────────────────


class FredObservationTransformation(Transformation):
    def transform(self, rows: list[Any]) -> list[dict]:
        records = []
        for row in rows:
            observation_date = date.fromisoformat(row.observation_date)
            records.append(
                {
                    "series_id": row.series_id,
                    "observation_date": observation_date,
                    "value": Decimal(row.observation_value),
                    "business_key": f"{row.series_id}_{observation_date}",
                    "ingested_date": row.ingested_date,
                }
            )
        return records


# ─────────────────────────────────────────────
# Destination
# ─────────────────────────────────────────────


class FredObservationDestination(Destination):
    def __init__(self):
        self._repository = RepositoryFactory.get(
            "fred_observation", schema_name="staging"
        )

    def load(self, data: list[dict]) -> None:
        self._repository.upsert(records=data, unique_key=["business_key"])


# ─────────────────────────────────────────────
# Pipeline
# ─────────────────────────────────────────────


class PipelineFredSilver(BaseSilverPipeline):
    _pipeline_name = "fred_silver"

    def __init__(self):
        self._source = FredSilverSource()
        self._transformation = FredObservationTransformation()
        self._validator = SchemaValidator(FredObservationRecord)
        self._destination = FredObservationDestination()
        self._dead_letter = DeadLetterDestination()

    def run(self):
        super().run()
        self._mark_processed()

    def _mark_processed(self):
        sql = """
            UPDATE raw.fred_observations
            SET processed_at = now()
            WHERE processed_at IS NULL
        """
        with SQLModelClient(DATABASE_URL) as client:
            client.execute(sql)


if __name__ == "__main__":
    PipelineFredSilver().run()
