import os
import json
import logging
from datetime import timedelta
from prefect import flow, task
from dotenv import load_dotenv
from datetime import datetime, UTC
from prefect.cache_policies import NO_CACHE

from api.client import APIClient
from database.client import SQLModelClient
from repository.entity_repository import EntityRepository
from repository.raw_data_repository import RawDataRepository
from ingestion_service.application.service import Trading212IngestionService
from ingestion_service.strategy.strategies import AssetTLStrategy, Trading212APIStrategy

os.path.exists('logs') or os.makedirs('logs')
log_dir_name = 'logs'

logging.basicConfig(level=logging.INFO, filename=f'{log_dir_name}/info.log', filemode='w', format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

load_dotenv()

URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")

@task(retry_delay_seconds=30, retries=2, cache_policy=NO_CACHE)
def ingest_asset(ingestion_service, raw_data_repo, asset_repo, extraction_strategy, transformation_strategy):

    ingestion_service.asset(
        raw_data_repo,
        asset_repo,
        extraction_strategy,
        transformation_strategy)

    
@flow
def trading_212_asset():
    logging.info("Starting the flow to fetch account cash")
    logging.info("Starting data ingestion process")

    api_client = APIClient(url=URL, api_token=API_TOKEN, secret_token=SECRET_TOKEN)

    database_client = SQLModelClient(database_url="sqlite:///./data/trading212.db")

    asset_repo = EntityRepository("asset", client=database_client)

    raw_data_repo = RawDataRepository(client=database_client)

    extraction_strategy = Trading212APIStrategy
    transformation_strategy = AssetTLStrategy()
    ingestion_service = Trading212IngestionService(api_client)
   
    ingest_asset(
        ingestion_service,
        raw_data_repo,
        asset_repo,
        extraction_strategy,
        transformation_strategy)


    
cron="1 * * * *"
if __name__ == "__main__":
    trading_212_asset.serve(
        name="trading_212_asset", interval=timedelta(seconds=3600))  # 60min