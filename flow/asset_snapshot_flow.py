import os
import json
import logging
from datetime import timedelta
from dotenv import load_dotenv
from prefect import flow, task
from datetime import datetime, UTC

from api.client import APIClient
from database.client import SQLModelClient
from repository.entity_repository import EntityRepository
from ingestion_service.models.models import raw_data, asset
from repository.raw_data_repository import RawDataRepository
from ingestion_service.service import Trading212IngestionService
from ingestion_service.strategy.strategies import AssetTLStrategy, Trading212APIStrategy, AssetSnapshotTLStrategy, PortfolioSnapshotTLStrategy

os.path.exists('logs') or os.makedirs('logs')
log_dir_name = 'logs'

logging.basicConfig(level=logging.INFO, filename=f'{log_dir_name}/info.log', filemode='w', format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

load_dotenv()

URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")

@task
def ingest_asset_snapshot(ingestion_service, raw_data_repo, processed_data_repository, asset_repo, extraction_strategy, transformation_strategy):
    ingestion_service.asset_snapshot(
        raw_data_repo,
        processed_data_repository,
        asset_repo,
        extraction_strategy,
        transformation_strategy)

@flow
def trading_212_asset_snapshot():
    logging.info("Starting the flow to fetch account cash")
    logging.info("Starting data ingestion process")

    api_client = APIClient(url=URL, api_token=API_TOKEN, secret_token=SECRET_TOKEN)

    database_client = SQLModelClient(database_url="sqlite:///./data/trading212.db")
    raw_data_repo = RawDataRepository(client=database_client)
    asset_repo = EntityRepository("asset", client=database_client)
    asset_snapshot_repo = EntityRepository("asset_snapshot", client=database_client)

    extraction_strategy = Trading212APIStrategy
    transformation_strategy = AssetSnapshotTLStrategy()
    ingestion_service = Trading212IngestionService(api_client)
   
    ingest_asset_snapshot(
        ingestion_service,
        raw_data_repo,
        asset_repo,
        asset_snapshot_repo,
        extraction_strategy,
        transformation_strategy)
    
if __name__ == "__main__":
    trading_212_asset_snapshot.serve(
        name="asset_snapshot", interval=timedelta(seconds=1800))  # Runs every 5mins
    