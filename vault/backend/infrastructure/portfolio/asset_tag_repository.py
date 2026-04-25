from shared.repositories.base_table_repository import BaseTableRepository


class PostgresAssetTagRepository(BaseTableRepository):
    def __init__(self):
        field_map = {
            "id": "id",
            "tag_id": "tag_id",
            "asset_id": "asset_id",
            "is_active": "is_active",
            "created_datetime": "created_timestamp",
            "processed_timestamp": "updated_timestamp",
        }
        super().__init__("asset_tag", schema_name="portfolio", field_map=field_map)


class SQLiteAssetTagRepository(BaseTableRepository):
    def __init__(self):
        field_map = {
            "id": "id",
            "tag_id": "tag_id",
            "asset_id": "asset_id",
            "is_active": "is_active",
            "data_timestamp": "created_datetime",
            "processed_timestamp": "updated_datetime",
        }
        super().__init__("asset_tag", schema_name=None, field_map=field_map)
