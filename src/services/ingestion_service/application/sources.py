import os
import asyncio
from dotenv import load_dotenv

from src.services.ingestion_service.application.interfaces import Source
from src.services.ingestion_service.api.trading212_api_client import Trading212APIClient

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
    self._api_client = Trading212APIClient(self._url, self._api_token, self._secret_token)
  def fetch(self):
    data = asyncio.run(self._api_client.get(endpoint=self._endpoint))
    data = self._to_data(data)
    return data
  
class Trading212AssetSnapshotSource(Source):
  def __init__(self):
    self._url = URL
    self._endpoint = "equity/positions"
    self._api_token = API_TOKEN
    self._secret_token = SECRET_TOKEN
    self._api_client = Trading212APIClient(self._url, self._api_token, self._secret_token)
  def fetch(self):
    data = asyncio.run(self._api_client.get(endpoint=self._endpoint))
    data = self._to_data(data)
    return data
  
class Trading212PortfolioSnapshotSource(Source):
  def __init__(self):
    self._url = URL
    self._endpoint = "equity/account/summary"
    self._api_token = API_TOKEN
    self._secret_token = SECRET_TOKEN
    self._api_client = Trading212APIClient(self._url, self._api_token, self._secret_token)
  def fetch(self):
    data = asyncio.run(self._api_client.get(endpoint=self._endpoint))
    data = self._to_data(data)
    return data