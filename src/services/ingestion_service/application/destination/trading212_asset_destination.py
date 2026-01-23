from dotenv import load_dotenv
import os
import asyncio
import json
from datetime import datetime, UTC
from typing import Iterable, Any, List, Dict
load_dotenv()


from src.services.ingestion_service.application.interfaces.protocols.destination import Destination

from src.shared.repositories.entity_repository import EntityRepository
from src.shared.database.client import SQLModelClient

# TODO: MOVE TO SQLMODEL CLIENT
DATABASE_URL = os.getenv("DATABASE_URL")


class Trading212AssetDestination(Destination):
  def __init__(self):
    self._database_client = SQLModelClient(database_url=DATABASE_URL)
    self._repository = EntityRepository("asset", client=self._database_client)
  def save(self, records: List[Dict]):
    self._repository.upsert(records=records, unique_key='external_id')