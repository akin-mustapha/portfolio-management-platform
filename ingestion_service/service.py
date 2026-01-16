import os
import json
import logging
from dotenv import load_dotenv
from datetime import datetime, UTC

from database.client import SQLModelClient
from api.client import APIClient
from ingestion_service.models import raw_data, asset
from repository.entity_repository import EntityRepository
from repository.raw_data_repository import RawDataRepository
from ingestion_service.strategies import AssetExtractionStrategy, Trading212APIStrategy, AssetDataExtractionStrategy

os.path.exists('logs') or os.makedirs('logs')
log_dir_name = 'logs'

logging.basicConfig(level=logging.INFO, filename=f'{log_dir_name}/info.log', filemode='w', format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

load_dotenv()

URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")

class Trading212IngestionService:
    def __init__(self, api_client):

        logging.info("=" * 80)
        logging.info("Initializing Ingestion Service")
        logging.info("=" * 80)
        self.api_client = api_client

    def ingest_asset(self,
                raw_data_repository,
                processed_data_repository,
                asset_data_repository,
                extraction_strategy,
                transformation_strategy,
                ):
        results = extraction_strategy.apply_to("equity/positions", self.api_client)
        res = raw_data_repository.insert(
            record={
                "source": "trading212",
                "payload": json.dumps(results),
                "is_processed": False,
                "created_datetime": datetime.now(UTC)}
            )
        
        transformation_strategy[0].apply_to(res, processed_data_repository)
        transformation_strategy[1].apply_to(res, processed_data_repository, asset_data_repository)

        raw_data_repository.process_raw_data(res.get('id'))

if __name__ == "__main__":
    logging.info("Starting data ingestion process")

    api_client = APIClient(url=URL, api_token=API_TOKEN, secret_token=SECRET_TOKEN)

    database_client = SQLModelClient(database_url="sqlite:///./data/trading212.db")

    raw_data_repo = RawDataRepository(client=database_client)

    asset_repo = EntityRepository("asset", client=database_client)
    asset_data_repo = EntityRepository("asset_data", client=database_client)

    # asset_repo.delete({'id': 1})

    ingestion_service = Trading212IngestionService(api_client)

    res = ingestion_service.ingest_asset(
        raw_data_repository=raw_data_repo,
        processed_data_repository=asset_repo,
        asset_data_repository=asset_data_repo,
        extraction_strategy=Trading212APIStrategy,
        transformation_strategy=[AssetExtractionStrategy, AssetDataExtractionStrategy],
    )

    # logging.info(f"Mapped {res} positions to Trading212 Asset dataclass instances")