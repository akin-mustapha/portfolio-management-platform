import os
import json
import logging
from time import sleep
from dotenv import load_dotenv
from datetime import datetime, UTC

from database.client import SQLModelClient
from api.client import APIClient
from repository.entity_repository import EntityRepository
from repository.raw_data_repository import RawDataRepository
from ingestion_service.strategy.strategies import AssetTLStrategy, Trading212APIStrategy, AssetSnapshotTLStrategy, PortfolioSnapshotTLStrategy

os.path.exists('logs') or os.makedirs('logs')
log_dir_name = 'logs'

logging.basicConfig(level=logging.INFO, filename=f'{log_dir_name}/info.log', filemode='w', format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

load_dotenv()

URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")

# Where to Dump data
# How to dump data
# Where to fetch data from
# How to fetch data
class Trading212IngestionService:
    def __init__(self, api_client, fetch=None, dump_strategy=None):
        logging.info("=" * 80)
        logging.info("Initializing Ingestion Service")
        logging.info("=" * 80)
        self.api_client = api_client
        self.dump_strategy = dump_strategy

    def ingest_raw_data(self, endpoint, extraction_strategy, repository):
        results = extraction_strategy.apply_to(endpoint, self.api_client)
        res = repository.insert(
            record={
                "source": endpoint,
                "payload": json.dumps(results),
                "is_processed": False,
                "created_datetime": datetime.now(UTC)
                }
        )
        return res
    
    def asset(self,
            raw_data_repository,
            processed_data_repository,
            extraction_strategy,
            transformation_strategy,
            ):
        endpoint = "equity/positions"
        res = self.ingest_raw_data(endpoint, extraction_strategy, raw_data_repository)
        transformation_strategy.apply_to(res, processed_data_repository)
        raw_data_repository.process_raw_data(res.get('id'))

    # This guy makes Asset Snapshot cake
    # It puts the raw ingredients on the rawDataRepo shelve 
    # It puts the freshly baked cake in the AssetSnapshotRepo
    def asset_snapshot(self,
                raw_data_repository,
                asset_repository,
                asset_snapshot_repository,
                extraction_strategy,
                transformation_strategy,
                ):
        endpoint = "equity/positions"
        res = self.ingest_raw_data(endpoint, extraction_strategy, raw_data_repository)
        transformation_strategy.apply_to(res, asset_repository, asset_snapshot_repository)
        raw_data_repository.process_raw_data(res.get('id'))

    def portfolio_snapshot(self,
                           raw_data_repository,
                           processed_data_repository,
                           extraction_strategy,
                           transformation_strategy,
                           ):
        endpoint = "equity/account/summary"
        res = self.ingest_raw_data(endpoint, extraction_strategy, raw_data_repository)
        transformation_strategy.apply_to(res, processed_data_repository)
        raw_data_repository.process_raw_data(res.get('id'))

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
        raw_data_repository=raw_data_repo,
        processed_data_repository=asset_repo,
        portfolio_snapshot_repository=asset_snapshot_repo,
        extraction_strategy=extraction_strategy,
        transformation_strategy=AssetSnapshotTLStrategy,
    )

    # transformation_strategy = PortfolioSnapshotTLStrategy()
    # ingestion_service.portfolio_snapshot(portfolio_snapshot_repo, extraction_strategy, raw_data_repo, transformation_strategy)

    # logging.info(f"Mapped {res} positions to Trading212 Asset dataclass instances")