from dotenv import load_dotenv

from shared.utils.custom_logger import customer_logger
from backend.application.portfolio.service import PortfolioService
from backend.infrastructure.portfolio.repository_factory import RepositoryFactory
from backend.infrastructure.portfolio.asset_analytics_repository import (
    AssetAnalyticsRepository,
)
from backend.infrastructure.portfolio.portfolio_query_repository import (
    PortfolioQueryRepository,
)

logging = customer_logger("Portfolio Service")
load_dotenv()


def build_portfolio_service() -> PortfolioService:
    return PortfolioService(
        repo_factory=RepositoryFactory(),
        analytics_repo=AssetAnalyticsRepository(),
        portfolio_query_repo=PortfolioQueryRepository(),
    )
