from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
from trading212.client import Trading212Client
import asyncio
import logging
import json
from dataclasses import dataclass

os.path.exists('logs') or os.makedirs('logs')
log_dir_name = 'logs'

logging.basicConfig(level=logging.INFO, filename=f'{log_dir_name}/info.log', filemode='w', format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')
# logging.basicConfig(level=logging.DEBUG, filename=f'{dir_name}/debug.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
# logging.basicConfig(level=logging.ERROR, filename=f'{dir_name}/error.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

if __name__ == "__main__":
    url = os.getenv("API_URL")
    api_token = os.getenv("API_TOKEN")
    secret_token = os.getenv("SECRET_TOKEN")

    trading212_client = Trading212Client(url=url, api_token=api_token, secret_token=secret_token)

    # with open("./ingestion/position.json", "r") as f:
    #     data = json.load(f)
    
    assets = trading212_client.fetch_all_positions()
    logging.info(assets)