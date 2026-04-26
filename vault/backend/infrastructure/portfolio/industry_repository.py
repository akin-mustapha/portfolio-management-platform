from shared.repositories.base_table_repository import BaseTableRepository


class PostgresIndustryRepository(BaseTableRepository):
    def __init__(self):
        field_map = {
            "name": "name",
            "description": "description",
            "is_active": "is_active",
            "created_timestamp": "created_timestamp",
            "updated_timestamp": "updated_timestamp",
        }
        super().__init__("industry", schema_name="portfolio", field_map=field_map)


class SQLiteIndustryRepository(BaseTableRepository):
    def __init__(self):
        field_map = {
            "id": "id",
            "name": "name",
            "description": "description",
            "is_active": "is_active",
            "created_timestamp": "created_timestamp",
            "updated_timestamp": "updated_timestamp",
        }
        super().__init__("industry", schema_name=None, field_map=field_map)
