from .base_table_repository import BaseTableRepository

class PostgresAssetRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain field -> DB column mapping
        field_map = {
            "id": "id",
            "external_id": "external_id",  # TODO: verify DB column name against portfolio schema
            "name": "name",
            "description": "description",
            "source_name": "source_name",  # TODO: verify DB column name against portfolio schema
            "is_active": "is_active",
            "created_timestamp": "from_timestamp",  # TODO: verify DB column name against portfolio schema
            "updated_timestamp": "updated_timestamp",
        }

        schema_name = "portfolio" if db_type == "postgres" else None
        super().__init__("asset", schema_name=schema_name, field_map=field_map)


class SQLiteAssetRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain field -> DB column mapping
        field_map = {
            "id": "id",
            "external_id": "external_id",
            "name": "name",
            "description": "description",
            "source_name": "source_name",
            "is_active": "is_active",
            "created_timestamp": "created_datetime",  # TODO: verify DB column name against portfolio schema
            "updated_timestamp": "updated_datetime",
        }

        schema_name = "portfolio" if db_type == "postgres" else None
        super().__init__("asset", schema_name=schema_name, field_map=field_map)
