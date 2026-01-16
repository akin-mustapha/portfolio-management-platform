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
  
class AssetDataExtractionStrategy:
  from datetime import datetime, UTC
  @classmethod
  def apply_to(self, record, asset_repository, asset_data_repository):
    data_date = datetime.now(UTC)
    assets = json.loads(record.get('payload', {}))
    for asset in assets:
      instrument = asset.get('instrument', {})
      wallet_impact = asset.get('walletImpact', {})

      ticker = instrument.get('ticker', '')
      asset_id = asset_repository.select({'external_id': ticker})

      data = {
        "asset_id": "",
        "data_date": data_date,
        "share": asset.get('quantity', 0),
        "price": asset.get('currentPrice', 0),
        "avg_price": asset.get('averagePricePaid', 0),
        "value": wallet_impact.get('currentValue', 0),
        "cost": wallet_impact.get('totalCost', 0),
        "profit": wallet_impact.get('unrealizedProfitLoss', 0),
        "fx_impact": wallet_impact.get('fxImpact', 0),
        "currency": instrument.get('currency', ''),
        "local_currency": wallet_impact.get('currency', ''),
        
      }

      asset_data_repository.insert([data])

    return len(assets)
  

class Trading212APIStrategy:
  @staticmethod
  def apply_to(endpoint, api_client) -> list[dict]:
      logging.info("Making API call to fetch all positions")

      # TODO: MOVE LOGIC TO TRANSFORMATION
      data = asyncio.run(api_client.get(endpoint=endpoint))
      return data