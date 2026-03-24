"""
Asset Bronze Pipeline
"""

import os
import logging
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv
from pydantic import ValidationError

from ...application.protocols import Source
from ...application.policies import Pipeline
from ...application.protocols import Destination

from .loaders.asset_full_loader import PostgresAssetFullLoader
from ...infrastructure.api.api_client_trading212 import Trading212APIClient
from ...domain.schemas.bronze.asset_api import AssetAPIRecord

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


class Trading212AssetSource(Source):
    def __init__(self):
        self._url = URL
        self._endpoint = "equity/positions"
        self._api_token = API_TOKEN
        self._secret_token = SECRET_TOKEN
        self._api_client = Trading212APIClient(
            self._url, self._api_token, self._secret_token
        )

    def extract(self):
        data = asyncio.run(self._api_client.get(endpoint=self._endpoint))
        return data


class Trading212AssetDestination(Destination):
    def load(self, data: Any) -> None:
        PostgresAssetFullLoader("raw.asset").load(data)


class PipelineAssetBronze(Pipeline):
    def __init__(self):
        self._source = Trading212AssetSource()
        self._destination = Trading212AssetDestination()

    def run(self):
        try:
            data: list[Dict] = self._source.extract()
            self._validate_structure(data)
            self._destination.load(data)
            return None

        except Exception as e:
            raise e

    def _validate_structure(self, data: list[dict]) -> None:
        errors = []
        for i, record in enumerate(data):
            try:
                AssetAPIRecord(**record)
            except ValidationError as e:
                errors.append((i, e))
        if errors:
            raise ValueError(
                f"[AssetBronze] API response failed structural validation: {errors}"
            )


if __name__ == "__main__":
    PipelineAssetBronze().run()
