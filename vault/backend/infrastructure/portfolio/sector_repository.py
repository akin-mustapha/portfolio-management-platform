from shared.repositories.base_table_repository import BaseTableRepository


class PostgresSectorRepository(BaseTableRepository):
    def __init__(self):
        field_map = {
            "id": "id",
            "name": "name",
            "description": "description",
            "industry_id": "industry_id",
            "is_active": "is_active",
            "created_timestamp": "created_timestamp",
        }
        super().__init__("sector", schema_name="portfolio", field_map=field_map)


class SQLiteSectorRepository(BaseTableRepository):
    def __init__(self):
        field_map = {
            "id": "id",
            "name": "name",
            "description": "description",
            "industry_id": "industry_id",
            "is_active": "is_active",
            "created_datetime": "created_timestamp",
            "processed_timestamp": "updated_timestamp",
        }
        super().__init__("sector", schema_name=None, field_map=field_map)
