import os
import asyncio
from dotenv import load_dotenv

from src.backend.ingestion.app.interfaces.interfaces import Source

from ..app.policies import Origin

# TODO: should depend on interface
from src.backend.ingestion.infra.api.api_client_trading212 import Trading212APIClient

load_dotenv()

URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")

class Trading212AssetAPIOrigin(Origin):
  def __init__(self, origin_name: str):
    super().__init__(origin_name)
    self._url = URL
    self._endpoint = "equity/positions"
    self._api_token = API_TOKEN
    self._secret_token = SECRET_TOKEN
    self._api_client = Trading212APIClient(self._url, self._api_token, self._secret_token)
    
  def _handler(self):
    data = asyncio.run(self._api_client.get(endpoint=self._endpoint))
    self._metadata = {
      "url": self._url,
      "endpoint": self._endpoint,
      "origin": self.origin_name
    }
    return data