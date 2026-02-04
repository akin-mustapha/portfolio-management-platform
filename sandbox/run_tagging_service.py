
import logging
import os
from dotenv import load_dotenv
from random import randint
from datetime import UTC, datetime

from src.infra.database.client import SQLModelClient
from src.app.domain.models.models import Item, Item_tag, Tag
from src.infra.repositories.entity_repository import EntityRepositoryFactory
from src.infra.repositories.repositories import DomainRepositoryFactory
from src.infra.repositories.query_repository import ItemSQLQueryRepository
from src.shared.utils.custom_logger import customer_logger
from src.app.services.portfolio.service import PortfolioService

logging = customer_logger("Portfolio Service")
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


if __name__ == "__main__":
  # Example usage
  t_item = Item(
              id=4,
              external_id=f"instrument_{randint(1000, 9999)}",
              name="Sample Instrument",
              description="Sample Instrument Description",
              source_name="trading212",
              is_active=True,
              created_datetime=datetime.now(UTC),
              updated_datetime=None,
          )
  t_tag = Tag(
              id=1,
              name=f"Sample Tag_{randint(1000, 9999)}",
              description="Sample Tag Description",
              tag_type_id=randint(1, 5),
              is_active=True,
              created_datetime=datetime.now(UTC),
              updated_datetime=None,
          )
  database_client = SQLModelClient(database_url=DATABASE_URL)

  item_repo = EntityRepositoryFactory.get_repository("asset", schema_name="portfolio")
  tag_repo = EntityRepositoryFactory.get_repository("tag", schema_name="portfolio")
  item_tag_repo = EntityRepositoryFactory.get_repository("asset_tag", schema_name="portfolio")
  item_query_repo = ItemSQLQueryRepository(database_client)

  tag_service = PortfolioService(item_repo, tag_repo, item_tag_repo, item_query_repo)

  # res = tag_service.create_item(t_item)
  # print(res)

  res_tag = tag_service.create_tag(t_tag)
  print(res_tag)

  t_tag_item = Item_tag(
                item_id=randint(1, 20),
                tag_id=1,
                is_active=True,
                created_datetime=datetime.now(UTC),
                updated_datetime=None,
            )
  res_tag_item = tag_service.tag_item(t_tag_item)
  print(res_tag_item)

  # tag_service.remove_tag_from_item(t_tag_item)
  # tag_service.tag_item(t_tag_item)


  x = tag_service.search_item_by_tag(t_tag)
  y = tag_service.search_tag_by_item(t_item)

  print(x)
  print(y)
