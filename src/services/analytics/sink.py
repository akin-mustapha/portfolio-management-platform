from src.shared.database.client import SQLModelClient
from src.services.ingestion_service.infrastructure.repositories.entity_repository import EntityRepository
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class SinkAssetMetric:
  _client = SQLModelClient(DATABASE_URL)
  _repository = EntityRepository("asset_metric", _client)
  @classmethod
  def save(cls, df: pd.DataFrame):
    records = df.to_dict(orient="records")

    cls._repository.insert(records)