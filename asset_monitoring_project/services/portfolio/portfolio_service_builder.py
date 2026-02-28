

import logging
import os
from dotenv import load_dotenv
from random import randint
from datetime import UTC, datetime

from shared.utils.custom_logger import customer_logger
from services.portfolio.service import PortfolioService

logging = customer_logger("Portfolio Service")
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def build_portfolio_service():
  return PortfolioService()