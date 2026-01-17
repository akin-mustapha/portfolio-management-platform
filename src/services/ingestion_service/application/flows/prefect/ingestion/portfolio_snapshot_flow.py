import os
import json
import logging
from prefect import flow, task
from dotenv import load_dotenv
from datetime import timedelta
from datetime import datetime, UTC
from prefect.cache_policies import NO_CACHE

from src.shared.database.client import SQLModelClient
from src.services.ingestion_service.api.client import APIClient
from src.services.ingestion_service.infrastructure.repositories.entity_repository import EntityRepository
from src.services.ingestion_service.infrastructure.repositories.raw_data_repository import RawDataRepository
from src.services.ingestion_service.application.service import Trading212IngestionService
from src.services.ingestion_service.application.strategy.strategies import Trading212APIStrategy, PortfolioSnapshotTLStrategy
from src.shared.utils.custom_logger import customer_logger

logging = customer_logger("portfolio_snapshot_flow_run")
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