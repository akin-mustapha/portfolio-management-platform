"""
Trading212 Client to interact with Trading212 API
"""
from api_service.api_client import APIClient
import asyncio
from trading212.models import Trading212Asset
import logging
import os

os.path.exists('logs') or os.makedirs('logs')
log_dir_name = 'logs'

logging.basicConfig(level=logging.INFO, filename=f'{log_dir_name}/info.log', filemode='w', format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

class Trading212Client:
    def __init__(self, url: str, api_token: str, secret_token: str):
        self.url = url
        self.api_client = APIClient(url=url, api_token=api_token, secret_token=secret_token)

    def fetch_all_positions(self) -> list[dict]:
        logging.info("Making API call to fetch all positions")

        # TODO: MOVE LOGIC TO TRANSFORMATION
        data = asyncio.run(self.api_client.get(endpoint="equity/positions"))
        # asset_list = []
        # logging.info(f"Mapping {len(data)} positions to Trading212Asset dataclass instances")
        # for item in data:
        #     # TODO: Map to config
        #     instrument = item.get("instrument", {})
        #     asset = Trading212Asset(
        #         # TODO: Map to config
        #         external_id=instrument.get("ticker"),
        #         name=instrument.get("ticker"),
        #         description=instrument.get("name"),
        #         source_name="trading212"
        #     )
        #     asset_list.append(asset)

        # logging.info(f"Mapped {len(asset_list)} positions to Trading212 Asset dataclass instances")
        return data