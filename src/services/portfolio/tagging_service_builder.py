

import logging
import os
from dotenv import load_dotenv
from random import randint
from datetime import UTC, datetime

from src.services.portfolio.infra.repositories.table_repository_factory import TableRepositoryFactory
from src.shared.utils.custom_logger import customer_logger
from src.services.portfolio.service import PortfolioService

logging = customer_logger("Portfolio Service")
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def build_tagging_service():
  asset_repo = TableRepositoryFactory.get("asset")
  tag_repo = TableRepositoryFactory.get("tag")
  asset_tag_repo = TableRepositoryFactory.get("asset_tag")
  asset_query_repo = TableRepositoryFactory.get("asset_query")
  return PortfolioService(asset_repo, tag_repo, asset_tag_repo, asset_query_repo)