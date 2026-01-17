import os
import json
import logging
from datetime import timedelta
from dotenv import load_dotenv
from prefect import flow, task
from datetime import datetime, UTC
from prefect.cache_policies import NO_CACHE

from src.shared.database.client import SQLModelClient
from src.services.ingestion_service.api.client import APIClient
from src.services.ingestion_service.infrastructure.repositories.entity_repository import EntityRepository
from src.services.ingestion_service.infrastructure.repositories.raw_data_repository import RawDataRepository
from src.services.ingestion_service.application.service import Trading212IngestionService
from src.services.ingestion_service.application.strategy.strategies import Trading212APIStrategy, AssetSnapshotTLStrategy
from src.shared.utils.custom_logger import customer_logger

logging = customer_logger("asset_snapshot_flow_run")
load_dotenv()

URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

@task(retry_delay_seconds=30, retries=2, cache_policy=NO_CACHE)
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

    database_client = SQLModelClient(database_url=DATABASE_URL)
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
    