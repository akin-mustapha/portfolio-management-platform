from src.services.ingestion.infra.repositories.base_table_repository import BaseTableRepository

class PostgresBronzeAssetRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain name -> DB column mapping
        field_map = {
          "ticker": "ticker",
          "instrument_name": "instrument_name",
          "isin": "isin",
          "instrument_currency": "instrument_currency",
          "created_at": "created_at",
          "quantity": "quantity",
          "quantity_available": "quantity_available",
          "quantity_in_pies": "quantity_in_pies",
          "current_price": "current_price",
          "average_price_paid": "average_price_paid",
          "wallet_currency": "wallet_currency",
          "total_cost": "total_cost",
          "current_value": "current_value",
          "unrealized_pnl": "unrealized_pnl",
          "fx_impact": "fx_impact",
          "ingested_date": "ingested_date",
          "ingested_timestamp": "ingested_timestamp"
        }

        schema_name = "raw" if db_type == "postgres" else None
        super().__init__("v_bronze_asset", schema_name=schema_name, field_map=field_map)
