from shared.repositories.base_table_repository import BaseTableRepository


class PostgresAssetRepository(BaseTableRepository):
    def __init__(self):
        field_map = {
            "id": "id",
            "ticker": "ticker",
            "name": "name",
            "broker": "broker",
            "currency": "currency",
            "is_active": "is_active",
            "from_timestamp": "from_timestamp",
            "to_timestamp": "to_timestamp",
            "updated_timestamp": "updated_timestamp",
        }
        super().__init__("asset", schema_name="portfolio", field_map=field_map)


class SQLiteAssetRepository(BaseTableRepository):
    def __init__(self):
        field_map = {
            "id": "id",
            "external_id": "external_id",
            "name": "name",
            "description": "description",
            "source_name": "source_name",
            "is_active": "is_active",
            "created_timestamp": "created_datetime",
            "updated_timestamp": "updated_datetime",
        }
        super().__init__("asset", schema_name=None, field_map=field_map)
