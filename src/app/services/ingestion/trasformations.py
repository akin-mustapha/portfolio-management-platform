from typing import Dict
from datetime import datetime, UTC
from src.app.interfaces.ingestion import Data
from src.infra.repositories.entity_repository import EntityRepositoryFactory
from src.app.interfaces.ingestion import Transformation


class Trading212AssetTransformation(Transformation):
  """
    Trading212AssetTransformation:
  """
  def apply_to(self, data: Data) -> list[Dict]:
    """
      apply_to: 
    """
    record = self._get_raw_data(data)
    transformed_data = []
    for asset in record:
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
      transformed_data.append(data)
    return transformed_data
  
class Trading212AssetSnapshotTransformation(Transformation):
  """
    Trading212AssetSnapshotTransformation:
  """
  _asset_repository = EntityRepositoryFactory.get_repository("asset", schema_name="portfolio")
  def apply_to(self, data: Data) -> list[Dict]:
    """
      apply_to: 
    """
    record = self._get_raw_data(data)
    data_date = datetime.now(UTC)
    transformed_data = []
    for asset in record:
      instrument = asset.get('instrument', {})
      ticker = instrument.get('ticker', '')
      wallet_impact = asset.get('walletImpact', {})
      record = self._asset_repository.select({'external_id': ticker})
      asset_id = record[0]
      data = {
        "asset_id": asset_id,
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
      transformed_data.append(data)
    return transformed_data
  
class Trading212PortfolioSnapshotTransformation(Transformation):
  """
    Trading212PortfolioSnapshotTransformation:
  """
  _portfolio_snapshot_repository = EntityRepositoryFactory.get_repository("portfolio_snapshot", schema_name="portfolio")
  def apply_to(self, data: Data) -> list[Dict]:
    """
      apply_to: 
    """
    record = self._get_raw_data(data)
    data_date = datetime.now(UTC)
    investment = record.get('investments', {})
    transformed_data = {
      "external_id": record.get('id', None),
      "data_date": data_date,
      "currency": record.get('currency', ''),
      "current_value": investment.get('currentValue', 0),
      "total_value": record.get('totalValue', 0),
      "total_cost": record.get('totalCost', 0),
      "unrealized_profit": investment.get('unrealizedProfitLoss', 0),
      "realized_profit": investment.get('realizedProfitLoss', 0),
    }
    return [transformed_data]