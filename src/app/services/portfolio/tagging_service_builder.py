

import logging
import os
from dotenv import load_dotenv
from random import randint
from datetime import UTC, datetime

from src.infra.database.client import SQLModelClient
from src.app.domain.models import Item, Item_tag, Tag
from src.app.interfaces.interface import BaseRepositoryInterface
from src.infra.repositories.entity_repository import EntityRepositoryFactory
from src.infra.repositories.repositories import DomainRepositoryFactory
from src.infra.repositories.query_repository import ItemSQLQueryRepository
from src.shared.utils.custom_logger import customer_logger
from src.app.services.portfolio import PortfolioService

logging = customer_logger("Portfolio Service")
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def build_tagging_service():
  database_client = SQLModelClient(database_url=DATABASE_URL)
  item_repo = DomainRepositoryFactory.get_repository("item", EntityRepositoryFactory.get_repository("asset", schema_name="portfolio"))
  tag_repo = DomainRepositoryFactory.get_repository("tag", EntityRepositoryFactory.get_repository("tag", schema_name="portfolio"))
  item_tag_repo = DomainRepositoryFactory.get_repository("item_tag", EntityRepositoryFactory.get_repository("asset_tag", schema_name="portfolio"))
  item_query_repo = ItemSQLQueryRepository(database_client)
  return PortfolioService(item_repo, tag_repo, item_tag_repo, item_query_repo)