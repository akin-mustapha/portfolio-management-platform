from src.services.ingestion.infra.repositories.base_table_repository import BaseTableRepository

class PostgresAssetMetricRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain name -> DB column mapping
        field_map = {
            "id": "id",
            "asset_id": "asset_id",
            "data_date": "data_date",
            "pct_drawdown": "pct_drawdown",
            "recent_hight_30d": "recent_hight_30d",
            "recent_low_30d": "recent_low_30d",
            "ma_30d": "ma_30d",
            "ma_50d": "ma_50d",
            "norm_price_30d": "norm_price_30d",
            "price_vs_ma_50d": "price_vs_ma_50d",
            "volatility_30d": "volatility_30d",
            "dca_bias": "dca_bias",
        }

        schema_name = "portfolio" if db_type == "postgres" else None
        super().__init__("asset_metric", schema_name=schema_name, field_map=field_map)

class SQLiteAssetMetricRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain name -> DB column mapping
        field_map = {
            "id": "id",
            "asset_id": "asset_id",
            "name": "name",
            "description": "description",
            "source_name": "source_name",           # domain field = source, DB column = source_name
            "is_active": "is_active",
            "data_timestamp": "created_datetime", # domain field = created_at, DB column = created_timestamp
            "processed_timestamp": "updated_datetime",
        }

        schema_name = "portfolio" if db_type == "postgres" else None
        super().__init__("asset", schema_name=schema_name, field_map=field_map)
