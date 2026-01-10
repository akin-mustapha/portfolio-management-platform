from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
from trading212.client import Trading212Client
import asyncio
import logging
import json
from dataclasses import dataclass
from database.client import JSONClient, SQLLiteClient
from ingestion.models import raw_data, asset

os.path.exists('logs') or os.makedirs('logs')
log_dir_name = 'logs'

logging.basicConfig(level=logging.INFO, filename=f'{log_dir_name}/info.log', filemode='w', format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')
# logging.basicConfig(level=logging.DEBUG, filename=f'{dir_name}/debug.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
# logging.basicConfig(level=logging.ERROR, filename=f'{dir_name}/error.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

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

    # with open("./ingestion/position.json", "r") as f:
    #     assets = json.load(f)
    
    # Load
    logging.info("Loading data")
    database_client = JSONClient(url="./data/trading212")
    database_client = SQLLiteClient(url="sqlite:///./data/trading212.db")
    database_client.save(model=raw_data, data={"source": "trading212", "payload": json.dumps(assets)})
    logging.info(assets)

    # Transformation

    asset_no = 0
    logging.info(f"Mapping {len(assets)} positions to Trading212Asset dataclass instances")
    for item in assets:
        # TODO: Map to config
        instrument = item.get("instrument", {})
        data = dict(
            # TODO: Map to config
            external_id=instrument.get("ticker"),
            name=instrument.get("ticker"),
            description=instrument.get("name"),
            source_name="trading212"
        )
        database_client.save(
            model=asset,
            data=data
        )
        asset_no += 1

    logging.info(f"Mapped {asset_no} positions to Trading212 Asset dataclass instances")