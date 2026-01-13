import os
import json
import asyncio
import logging
from datetime import datetime, UTC

from api.client import APIClient

os.path.exists('logs') or os.makedirs('logs')
log_dir_name = 'logs'

# Ensures all logs are stored in <project_dir>/logs/info.log
logging.basicConfig(level=logging.INFO, filename=f'{log_dir_name}/info.log', filemode='w', format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')


class AssetExtractionStrategy:
  @classmethod
  def apply_to(self, record, repository):
    # TODO: Map to config
    assets = json.loads(record.get('payload', {}))
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
      repository.upsert(records=[data], unique_key="external_id")

    return len(assets)
  

class Trading212APIStrategy:
  @staticmethod
  def apply_to(endpoint, api_client) -> list[dict]:
      logging.info("Making API call to fetch all positions")

      # TODO: MOVE LOGIC TO TRANSFORMATION
      data = asyncio.run(api_client.get(endpoint=endpoint))
      return data