"""
Bronze Pipeline for FRED (Federal Reserve Economic Data)

Fetches DTB3 (3-Month T-Bill rate) and SP500 from the FRED API and stores
raw observations in raw.fred_observations (JSONB, date-partitioned).
"""

import os
import logging
from datetime import date, timedelta
from typing import Any
from dotenv import load_dotenv
from pydantic import ValidationError

from ...application.protocols import Source, Destination
from ...application.policies import Pipeline
from .loaders.loader_bronze_fred import FullLoaderPostgresFred
from ...infrastructure.api.api_client_fred import FredAPIClient
from ...domain.schemas.bronze.fred_api import FredObservationsResponse

from shared.database.client import SQLModelClient

logging.basicConfig(
    level=logging.INFO,
    filename="logs/info.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
)

load_dotenv()

FRED_API_KEY = os.getenv("FREED_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

_SERIES = ["DTB3", "SP500"]
_DEFAULT_LOOKBACK_DAYS = 30


# ─────────────────────────────────────────────
# Source
# ─────────────────────────────────────────────


class FredBronzeSource(Source):
    def __init__(self):
        self._api_client = FredAPIClient(FRED_API_KEY)
        self._db_client = SQLModelClient(DATABASE_URL)

    def extract(self) -> list[dict]:
        results = []
        for series_id in _SERIES:
            observation_start = self._get_observation_start(series_id)
            response = self._api_client.get_observations(
                series_id=series_id,
                observation_start=observation_start,
            )
            self._validate_structure(series_id, response)
            results.append({
                "series_id": series_id,
                "observations": response["observations"],
                "observation_start": observation_start,
            })
        return results

    def _get_observation_start(self, series_id: str) -> str:
        sql = """
            SELECT MAX(observation_date) AS max_date
            FROM staging.fred_observation
            WHERE series_id = :series_id
        """
        with self._db_client as client:
            result = client.execute(sql, params={"series_id": series_id})
            row = result.fetchone()

        if row and row.max_date:
            start = row.max_date - timedelta(days=1)
        else:
            start = date.today() - timedelta(days=_DEFAULT_LOOKBACK_DAYS)

        return start.strftime("%Y-%m-%d")

    def _validate_structure(self, series_id: str, response: dict) -> None:
        try:
            FredObservationsResponse(**response)
        except ValidationError as e:
            raise ValueError(
                f"FRED API response for {series_id} failed structural validation: {e}"
            )


# ─────────────────────────────────────────────
# Destination
# ─────────────────────────────────────────────


class FredBronzeDestination(Destination):
    def load(self, data: Any) -> None:
        FullLoaderPostgresFred("raw.fred_observations").load(data)


# ─────────────────────────────────────────────
# Pipeline
# ─────────────────────────────────────────────


class PipelineFredBronze(Pipeline):
    def __init__(self):
        self._source = FredBronzeSource()
        self._destination = FredBronzeDestination()

    def run(self):
        try:
            data = self._source.extract()
            self._destination.load(data)
        except Exception as e:
            raise e


if __name__ == "__main__":
    PipelineFredBronze().run()
