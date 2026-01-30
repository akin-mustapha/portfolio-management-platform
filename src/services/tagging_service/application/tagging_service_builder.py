

import logging
import os
from dotenv import load_dotenv
from random import randint
from datetime import UTC, datetime

from src.shared.database.client import SQLModelClient
from src.services.tagging_service.domain.models.models import Item, Item_tag, Tag
from src.services.tagging_service.infrastructure.repositories.interface import BaseRepository
from src.shared.repositories.entity_repository import EntityRepository
from src.services.tagging_service.infrastructure.repositories.repositories import DomainRepositoryFactory
from src.shared.repositories.query_repository import ItemSQLQueryRepository
from src.shared.utils.custom_logger import customer_logger
from src.services.tagging_service.application.service import TaggingService

logging = customer_logger("Tagging Service")
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def build_tagging_service():
  database_client = SQLModelClient(database_url=DATABASE_URL)
  item_repo = DomainRepositoryFactory.get_repository("item", EntityRepository("asset"))
  tag_repo = DomainRepositoryFactory.get_repository("tag", EntityRepository("tag"))
  item_tag_repo = DomainRepositoryFactory.get_repository("item_tag", EntityRepository("asset_tag"))
  item_query_repo = ItemSQLQueryRepository(database_client)
  return TaggingService(item_repo, tag_repo, item_tag_repo, item_query_repo)