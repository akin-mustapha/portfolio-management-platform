import os
from dotenv import load_dotenv

from src.services.ingestion_service.api.client import APIClient
from src.shared.database.client import SQLModelClient
from src.services.ingestion_service.infrastructure.repositories.entity_repository import EntityRepository
from src.services.ingestion_service.infrastructure.repositories.raw_data_repository import RawDataRepository
from src.services.ingestion_service.application.strategy.strategies import Trading212APIStrategy, AssetSnapshotTLStrategy
from src.shared.utils.custom_logger import customer_logger
from src.services.ingestion_service.application.service import Trading212IngestionService

logging = customer_logger("ingestion_service")
load_dotenv()

URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")

if __name__ == "__main__":
    logging.info("Starting data ingestion process")

    api_client = APIClient(url=URL, api_token=API_TOKEN, secret_token=SECRET_TOKEN)
    database_client = SQLModelClient(database_url="sqlite:///./data/trading212.db")

    asset_repo = EntityRepository("asset", client=database_client)
    asset_snapshot_repo = EntityRepository("asset_snapshot", client=database_client)
    portfolio_snapshot_repo = EntityRepository("portfolio_snapshot", client=database_client)

    raw_data_repo = RawDataRepository(client=database_client)
    
    extraction_strategy=Trading212APIStrategy
    ingestion_service = Trading212IngestionService(api_client)

    # transformation_strategy = AssetTLStrategy()
    # ingestion_service.asset(
    #     raw_data_repo,
    #     asset_repo,
    #     extraction_strategy,
    #     transformation_strategy)

    # sleep(5)
    res = ingestion_service.asset_snapshot(
        raw_data_repo,
        asset_repo,
        asset_snapshot_repo,
        extraction_strategy=extraction_strategy,
        transformation_strategy=AssetSnapshotTLStrategy,
    )

    # transformation_strategy = PortfolioSnapshotTLStrategy()
    # ingestion_service.portfolio_snapshot(portfolio_snapshot_repo, extraction_strategy, raw_data_repo, transformation_strategy)

    # logging.info(f"Mapped {res} positions to Trading212 Asset dataclass instances")