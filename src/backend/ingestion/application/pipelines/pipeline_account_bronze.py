
"""
  Account Bronze Pipeline
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

from .loaders.account_full_loader import PostgresAccountFullLoader
from ...infrastructure.api.api_client_trading212 import Trading212APIClient
from ...domain.schemas.bronze.account_api import AccountAPIResponse

logging.basicConfig(
    level=logging.INFO,
    filename='logs/info.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s'
)

load_dotenv()

URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")

class Trading212AccountSource(Source):
  def __init__(self):
    self._url = URL
    self._endpoint = "equity/account/summary"
    self._api_token = API_TOKEN
    self._secret_token = SECRET_TOKEN
    self._api_client = Trading212APIClient(self._url, self._api_token, self._secret_token)

  def extract(self):
    data = asyncio.run(self._api_client.get(endpoint=self._endpoint))
    return data


class Trading212AccountDestination(Destination):
  def load(self, data: Any) -> None:
    PostgresAccountFullLoader("raw.account").load(data)


class PipelineAccountBronze(Pipeline):
  def __init__(self):
    self._source = Trading212AccountSource()
    self._destination = Trading212AccountDestination()

  def run(self):
    try:
      data: Dict = self._source.extract()
      self._validate_structure(data)
      self._destination.load(data)
      return None

    except Exception as e:
      raise e

  def _validate_structure(self, data: dict) -> None:
    try:
      AccountAPIResponse(**data)
    except ValidationError as e:
      raise ValueError(f"[AccountBronze] API response failed structural validation: {e}")


if __name__ == "__main__":
  PipelineAccountBronze().run()
