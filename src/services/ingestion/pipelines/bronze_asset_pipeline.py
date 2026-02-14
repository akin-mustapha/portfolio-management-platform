import os
import asyncio
from dotenv import load_dotenv
import logging
from typing import List, Dict
from dataclasses import asdict, Any
import json
from dataclasses import replace
from datetime import datetime, UTC
from src.services.ingestion.app.interfaces import Source
from src.services.ingestion.app.interfaces import Destination
from src.services.ingestion.app.interfaces import Transformation
from src.services.ingestion.app.policies import Pipeline

from src.services.ingestion.infra.api.trading212_api_client import Trading212APIClient
from sandbox.full_loader.main import PostgresAssetFullLoader

logging.basicConfig(level="INFO")

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
    

class Trading212AssetDestination(Destination):
  def __init__(self, repo):
    pass
  def save(self, data: List[Dict]) -> None:
    data = asdict(data)
    for record in data.get("payload", []):
      PostgresAssetFullLoader("raw.asset").load(json.dumps(record))


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

  def apply_to(self, data: Data) -> list[Dict]:
    """
      apply_to: 
    """
    record = self._get_raw_data(data)
    transformed_data = []
    field_map = self._FIELD_MAP
    source_name = self._SOURCE_NAME
    created_datetime = datetime.now(UTC)
    for asset in record:
      instrument = asset.get("instrument", {})
      data = {target: instrument.get(source) for target, source in field_map.items()}
      data["source_name"] = source_name
      data["is_active"] = True
      data["created_datetime"] = created_datetime
      transformed_data.append(data)
    return transformed_data
  
  
class BronzeAssetIngestionPipeline(Pipeline):
  def __init__(self):
    self._source = Trading212AssetSource()
    self._transformation = Trading212AssetTransformation()
    self._destination = Trading212AssetDestination()

  def run(self):
    # Fetch raw data from source
    data = self._source.fetch()
    # Copy to prevent mutating object
    try:
      # Apply Transformation Logic
      transformed_data: List[Any] = self._transformation.apply_to(data)
      
      # Save to Destination Table
      self._destination.save(transformed_data)
      return None
    
    except Exception as e:
      # Update raw data
      data = replace(data, is_processed=False)
      
      # TODO REPLACE WITH ERROR MANAGEMENT 
      # Persist raw data
      # self._sink.save(data)

      raise e