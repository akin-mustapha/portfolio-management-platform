from datetime import datetime, UTC
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
from trading212.client import Trading212Client
import asyncio
import logging
import json
from dataclasses import dataclass
from database.client import SQLModelClient
from repository.raw_data_repository import RawDataRepositorySQLite
from repository.asset_repository import AssetRepository
from repository.entity_repository import EntityRepository
from ingestion_service.models import raw_data, asset

os.path.exists('logs') or os.makedirs('logs')
log_dir_name = 'logs'

logging.basicConfig(level=logging.INFO, filename=f'{log_dir_name}/info.log', filemode='w', format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

load_dotenv()


if __name__ == "__main__":

    logging.info("Starting data ingestion process")
    url = os.getenv("API_URL")
    api_token = os.getenv("API_TOKEN")
    secret_token = os.getenv("SECRET_TOKEN")

    # Extract
    logging.info("Extracting data")
    trading212_client = Trading212Client(url=url, api_token=api_token, secret_token=secret_token)
    assets = trading212_client.fetch_all_positions()

    # Load
    logging.info("Loading data")

    database_client = SQLModelClient(database_url="sqlite:///./data/trading212.db")
    raw_data_repo = RawDataRepositorySQLite("raw_data", client=database_client)

    raw_data_repo.insert(records=[{"source": "trading212", "payload": json.dumps(assets), "is_processed": False, "created_datetime": datetime.now(UTC)}])

    logging.info(assets)

    # Transformation
    raw_data = raw_data_repo.select_by_id(source="trading212")
    asset_no = 0
    logging.info(f"Mapping {len(assets)} positions to Trading212Asset dataclass instances")
    
    asset_repo = EntityRepository("asset", client=database_client)

    # asset_repo.delete(id=0)  # Dummy call to ensure method exists


    for item in raw_data:
        # TODO: Map to config
        assets = json.loads(item[2])
        for asset in assets:
            instrument = asset.get("instrument", {})
            data = dict(
                # TODO: Map to config
                external_id=instrument.get("ticker"),
                name=instrument.get("ticker"),
                description=instrument.get("name"),
                source_name="trading212",
                is_active=True,
                created_datetime=datetime.now(UTC),
            )
            asset_repo.upsert(records=[data], unique_key="external_id")


        # raw_data_repo.process_raw_data(id=item[0])
        asset_no += 1

    logging.info(f"Mapped {asset_no} positions to Trading212 Asset dataclass instances")