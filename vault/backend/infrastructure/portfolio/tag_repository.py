from shared.repositories.base_table_repository import BaseTableRepository


class PostgresTagRepository(BaseTableRepository):
    def __init__(self):
        field_map = {
            "id": "id",
            "name": "name",
            "description": "description",
            "tag_type_id": "category_id",  # domain: tag_type_id, DB: category_id
            "created_timestamp": "created_timestamp",
        }
        super().__init__("tag", schema_name="portfolio", field_map=field_map)


class SQLiteTagRepository(BaseTableRepository):
    def __init__(self):
        field_map = {
            "id": "id",
            "name": "name",
            "description": "description",
            "category_id": "category_id",
            "is_active": "is_active",
            "created_timestamp": "created_datetime",
        }
        super().__init__("tag", schema_name=None, field_map=field_map)
