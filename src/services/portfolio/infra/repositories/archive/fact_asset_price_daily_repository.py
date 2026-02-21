from src.services.ingestion.infra.repositories.base_table_repository import BaseTableRepository

class PostgresFactAssetPriceDailyRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain name -> DB column mapping
        field_map = {
            "id": "id",
            "asset_id": "asset_id",
            "date_id": "date_id",
            "average_price": "average_price",
            "opening_price": "opening_price",
            "closing_price": "closing_price",
            "high": "high",
            "low": "low",
            "updated_timestamp": "updated_timestamp",
        }

        schema_name = "analytics" if db_type == "postgres" else None
        super().__init__("fact_asset_price_daily", schema_name=schema_name, field_map=field_map)

class SQLiteFactAssetPriceDailyRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain name -> DB column mapping
        field_map = {
            "id": "id",
            "asset_id": "asset_id",
            "date_id": "date_id",
            "average_price": "average_price",
            "opening_price": "opening_price",
            "closing_price": "closing_price",
            "high": "high",
            "low": "low",
            "updated_timestamp": "updated_timestamp",
        }

        schema_name = "analytics" if db_type == "postgres" else None
        super().__init__("fact_asset_price_daily", schema_name=schema_name, field_map=field_map)