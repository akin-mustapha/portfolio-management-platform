from shared.repositories.base_table_repository import BaseTableRepository


class PostgresCategoryRepository(BaseTableRepository):
    def __init__(self):
        field_map = {
            "name": "name",
            "description": "description",
            "is_active": "is_active",
            "created_timestamp": "created_timestamp",
            "updated_timestamp": "updated_timestamp",
        }
        super().__init__("category", schema_name="portfolio", field_map=field_map)


class SQLiteCategoryRepository(BaseTableRepository):
    def __init__(self):
        field_map = {
            "id": "id",
            "name": "name",
            "description": "description",
            "is_active": "is_active",
            "created_timestamp": "created_timestamp",
            "updated_timestamp": "updated_timestamp",
        }
        super().__init__("category", schema_name=None, field_map=field_map)
