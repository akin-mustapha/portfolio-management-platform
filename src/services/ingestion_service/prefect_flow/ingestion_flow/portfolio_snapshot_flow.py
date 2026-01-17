import os
import json
import logging
from prefect import flow, task
from dotenv import load_dotenv
from datetime import timedelta
from datetime import datetime, UTC
from prefect.cache_policies import NO_CACHE

from api.client import APIClient
from database.client import SQLModelClient
from repository.entity_repository import EntityRepository
from repository.raw_data_repository import RawDataRepository
from ingestion_service.application.service import Trading212IngestionService
from ingestion_service.strategy.strategies import Trading212APIStrategy, PortfolioSnapshotTLStrategy

os.path.exists('logs') or os.makedirs('logs')
log_dir_name = 'logs'

logging.basicConfig(level=logging.INFO, filename=f'{log_dir_name}/info.log', filemode='w', format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

load_dotenv()

URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")

@task(retry_delay_seconds=30, retries=2, cache_policy=NO_CACHE)
def ingest_portfolio_snapshot(ingestion_service, raw_data_repo, asset_repo, extraction_strategy, transformation_strategy):
    ingestion_service.portfolio_snapshot(
        raw_data_repo,
        asset_repo,
        extraction_strategy,
        transformation_strategy)
    
@flow
def trading_212_portfolio_snapshot():
    logging.info("Starting the flow to fetch account cash")
    logging.info("Starting data ingestion process")

    api_client = APIClient(url=URL, api_token=API_TOKEN, secret_token=SECRET_TOKEN)

    database_client = SQLModelClient(database_url="sqlite:///./data/trading212.db")

    portfolio_snapshot_repo = EntityRepository("portfolio_snapshot", client=database_client)
    raw_data_repo = RawDataRepository(client=database_client)

    extraction_strategy = Trading212APIStrategy
    transformation_strategy = PortfolioSnapshotTLStrategy()
    ingestion_service = Trading212IngestionService(api_client)
   
    ingest_portfolio_snapshot(
        ingestion_service,
        raw_data_repo,
        portfolio_snapshot_repo,
        extraction_strategy,
        transformation_strategy)
    
if __name__ == "__main__": 
    trading_212_portfolio_snapshot.serve(
        name="trading_212_portfolio_snapshot", interval=timedelta(seconds=3600))  # Runs every 5mins