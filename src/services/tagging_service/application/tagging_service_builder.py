

import logging
import os
from dotenv import load_dotenv
from random import randint
from datetime import UTC, datetime

from src.shared.database.client import SQLModelClient
from src.services.tagging_service.domain.models.models import Item, Item_tag, Tag
from src.services.tagging_service.infrastructure.repositories.interface import BaseRepository
from src.services.ingestion_service.infrastructure.repositories.entity_repository import EntityRepository
from src.services.tagging_service.infrastructure.repositories.repositories import DomainRepositoryFactory
from src.shared.repositories.query_repository import ItemSQLQueryRepository
from src.shared.utils.custom_logger import customer_logger
from src.services.tagging_service.application.service import TaggingService

logging = customer_logger("Tagging Service")
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")



def build_trading212_pipeline():
  database_client = SQLModelClient(database_url=DATABASE_URL)
  item_repo = DomainRepositoryFactory.get_repository("item", EntityRepository("asset", client=database_client))
  tag_repo = DomainRepositoryFactory.get_repository("tag", EntityRepository("tag", client=database_client))
  item_tag_repo = DomainRepositoryFactory.get_repository("item_tag", EntityRepository("asset_tag", client=database_client))
  item_query_repo = ItemSQLQueryRepository(database_client)
  return TaggingService(item_repo, tag_repo, item_tag_repo, item_query_repo)