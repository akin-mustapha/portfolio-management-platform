"""
Bronze Pipeline for Trading212
"""

import asyncio
import logging
import os
import time
from typing import Any

from dotenv import load_dotenv
from pydantic import ValidationError

from pipeline.etl.loaders.loader_bronze_t212 import FullLoaderPostgresT212
from pipeline.etl.policies import Pipeline
from pipeline.etl.protocols import Destination, Source
from pipeline.infrastructure.clients.api_client_trading212 import Trading212APIClient
from pipeline.infrastructure.factories.schema import Schema

logging.basicConfig(
    level=logging.INFO,
    filename="logs/info.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
)

load_dotenv()

URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")

# ─────────────────────────────────────────────
# Account Source
# ─────────────────────────────────────────────


class Trading212BronzeSource(Source):
    def __init__(self):
        self._url = URL
        self._endpoint = {
            "account_data": "equity/account/summary",
            "position_data": "equity/positions",
        }
        self._api_token = API_TOKEN
        self._secret_token = SECRET_TOKEN
        self._api_client = Trading212APIClient(self._url, self._api_token, self._secret_token)

    def extract(self):
        data = {}
        for key, value in self._endpoint.items():
            try:
                res = asyncio.run(self._api_client.get(endpoint=value))  # Make api call
                data.update({key: res})

                time.sleep(50)  # rate limiting
            except Exception as e:
                raise e

        return data


# ─────────────────────────────────────────────
# Account Destination
# ─────────────────────────────────────────────


class Trading212BronzeDestination(Destination):
    def load(self, data: Any) -> None:
        FullLoaderPostgresT212("raw.t212_snapshot").load(data)


class PipelineT212Bronze(Pipeline):
    def __init__(self):
        self._source = Trading212BronzeSource()
        self._destination = Trading212BronzeDestination()

    def run(self):
        try:
            data: dict = self._source.extract()
            self._validate_structure(data)
            self._destination.load(data)
            return None

        except Exception as e:
            raise e

    def _validate_structure(self, data: dict) -> None:
        try:
            Schema.get("account_data")(**data["account_data"])
        except ValidationError as e:
            raise ValueError(f"account_data API response failed structural validation: {e}")

        try:
            for record in data["position_data"]:
                Schema.get("position_data")(**record)
        except ValidationError as e:
            raise ValueError(f"position_data API response failed structural validation: {e}")


if __name__ == "__main__":
    PipelineT212Bronze().run()
