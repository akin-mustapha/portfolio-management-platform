from src.services.portfolio.infra.repositories.base_table_repository import BaseTableRepository

class PostgresAssetTagRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain name -> DB column mapping
        field_map = {
            "id": "id",
            "tag_id": "tag_id",
            "asset_id": "asset_id",
            "is_active": "is_active",
            "created_datetime": "created_timestamp",
            "processed_timestamp": "updated_timestamp",
        }

        schema_name = "portfolio" if db_type == "postgres" else None
        super().__init__("asset_tag", schema_name=schema_name, field_map=field_map)


class SQLiteAssetTagRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain name -> DB column mapping
        field_map = {
            "id": "id",
            "tag_id": "tag_id",
            "asset_id": "asset_id",
            "is_active": "is_active",
            "data_timestamp": "created_datetime",
            "processed_timestamp": "updated_datetime",
        }

        schema_name = "portfolio" if db_type == "postgres" else None
        super().__init__("asset_tag", schema_name=schema_name, field_map=field_map)
