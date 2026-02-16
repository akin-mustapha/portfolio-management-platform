"""
  Asset Bronze Pipeline
"""
import os
import logging
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv

from src.services.ingestion.app.protocols import Source
from src.services.ingestion.app.policies import Pipeline
from src.services.ingestion.app.protocols import Destination
from src.services.ingestion.app.protocols import Transformation

from src.services.ingestion.full_loader.asset_full_loader import PostgresAssetFullLoader
from src.services.ingestion.infra.api.api_client_trading212 import Trading212APIClient

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

class Trading212AssetSource(Source):
  def __init__(self):
    self._url = URL
    self._endpoint = "equity/positions"
    self._api_token = API_TOKEN
    self._secret_token = SECRET_TOKEN
    self._api_client = Trading212APIClient(self._url, self._api_token, self._secret_token)
    
  def extract(self):
    data = asyncio.run(self._api_client.get(endpoint=self._endpoint))
    return data
    

class Trading212AssetDestination(Destination):
  def load(self, data: Any) -> None:
    PostgresAssetFullLoader("raw.asset").load(data)


class Trading212AssetTransformation(Transformation):
  """
    Trading212AssetTransformation:
  """
  _FIELD_MAP = {
    "external_id": "ticker",
    "name": "ticker",
    "description": "name",
  }
  _SOURCE_NAME = "trading212"

  def transform(self, data: list[Dict]) -> list[Dict]:
    """
      transform: 
    """
    pass
  
  
class PipelineAssetBronze(Pipeline):
  def __init__(self):
    self._source = Trading212AssetSource()
    self._transformation = Trading212AssetTransformation()
    self._destination = Trading212AssetDestination()

  def run(self):
    
    try:
      # Extract raw data from source
      data: list[Dict] = self._source.extract()
      
      # Load to Destination Table
      self._destination.load(data)
      return None
    
    except Exception as e:
      # Update raw data
      
      # TODO REPLACE WITH ERROR MANAGEMENT 
      # Persist raw data
      # self._sink.save(data)

      raise e
    
    
if __name__ == "__main__":
  PipelineAssetBronze().run()