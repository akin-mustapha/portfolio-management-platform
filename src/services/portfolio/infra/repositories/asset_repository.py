from src.services.portfolio.infra.repositories.base_table_repository import BaseTableRepository

class PostgresAssetRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain name -> DB column mapping
        field_map = {
            "id": "id",
            "ticker": "ticker",
            "name": "name",
            "description": "description",
            "broker": "broker",           # domain field = source, DB column = source_name
            "is_active": "is_active",
            "created_datetime": "from_timestamp", # domain field = created_at, DB column = created_timestamp
            "updated_timestamp": "updated_timestamp",
        }

        schema_name = "portfolio" if db_type == "postgres" else None
        super().__init__("asset", schema_name=schema_name, field_map=field_map)


class SQLiteAssetRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain name -> DB column mapping
        field_map = {
            "id": "id",
            "external_id": "external_id",
            "name": "name",
            "description": "description",
            "source_name": "source_name",           # domain field = source, DB column = source_name
            "is_active": "is_active",
            "data_timestamp": "created_datetime", # domain field = created_at, DB column = created_timestamp
            "updated_timestamp": "updated_datetime",
        }

        schema_name = "portfolio" if db_type == "postgres" else None
        super().__init__("asset", schema_name=schema_name, field_map=field_map)
