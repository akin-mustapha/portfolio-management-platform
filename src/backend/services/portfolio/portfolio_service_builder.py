import os
from dotenv import load_dotenv

from shared.utils.custom_logger import customer_logger
from backend.services.portfolio.service import PortfolioService

logging = customer_logger("Portfolio Service")
load_dotenv()


def build_portfolio_service():
    return PortfolioService()
