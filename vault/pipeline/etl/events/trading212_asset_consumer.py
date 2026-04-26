from datetime import UTC, datetime

import yaml  # type: ignore[import-untyped]

from pipeline.etl.policies import EventConsumer, Mapper
from pipeline.infrastructure.kafka.consumer_db_client import DestinationFactory

asset_schema = """
table: asset
schema: staging
fields:
  "ticker": "ticker"
  "name": "name"
  "source_name": "source_name"
  "currency": "currency"
  "quantity": "quantity"
  "quantity_available_for_trading": "quantity_available_for_trading"
  "quantity_in_pies": "quantity_in_pies"
  "current_price": "current_price"
  "average_price_paid": "average_price_paid"
  "total_cost": "total_cost"
  "current_value": "current_value"
  "unrealized_profit_loss": "unrealized_profit_loss"
  "fx_impact": "fx_impact"
  "created_timestamp": "created_timestamp"
"""


asset_snapshot_schema = """
table: asset_snapshot
schema: postgress
fields:
  "asset_id": "asset_id"
  "date_timestamp": "date_timestamp"
  "currency": "currency"
  "share": "share"
  "price": "price"
  "avg_price": "avg_price"
  "value": "value"
  "cost": "cost"
  "profit": "profit"
  "fx_impact": "fx_impact"
"""


class AssetMapper(Mapper):
    def map(self, data, schema):
        schema_dict = yaml.load(schema, Loader=yaml.SafeLoader)
        fields = schema_dict.get("fields")
        mapped_data = []
        for asset in data:
            instrument = asset.get("instrument", {})
            wallet_impact = asset.get("walletImpact", {})
            data = {
                "ticker": instrument.get("ticker"),
                "name": instrument.get("name"),
                "quantity": asset.get("quantity", 0),
                "quantity_in_pies": asset.get("quantityInPies", 0),
                "current_price": asset.get("currentPrice", 0),
                "quantity_available_for_trading": asset.get("quantityAvailableForTrading", 0),
                "average_price_paid": asset.get("averagePricePaid", 0),
                "current_value": wallet_impact.get("currentValue", 0),
                "total_cost": wallet_impact.get("totalCost", 0),
                "unrealized_profit_loss": wallet_impact.get("unrealizedProfitLoss", 0),
                "fx_impact": wallet_impact.get("fxImpact", 0),
                "currency": instrument.get("currency", ""),
                "local_currency": wallet_impact.get("currency", ""),
            }
            data = {col: data.get(source) for col, source in fields.items() if data.get(source) is not None}
            data["source_name"] = "Trading 212"
            data["created_timestamp"] = datetime.now(UTC)
            mapped_data.append(data)
        return mapped_data


class Trading212AssetConsumer(EventConsumer):
    mapper = AssetMapper()

    def run(self, data):
        result = self.mapper.map(data, asset_schema)
        destination = DestinationFactory.get("asset", "staging")

        destination.insert(result)

        # mapper = AssetSnapshotMapper()
        # result = mapper.map(data, asset_snapshot_schema)
        # destination = DestinationFactory.get("asset_snapshot", "porfolio")

        print("::consumed")
