from .base_table_repository import BaseTableRepository

class PostgresTagRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain field -> DB column mapping
        field_map = {
            "id": "id",
            "name": "name",
            "description": "description",
            "tag_type_id": "category_id",  # domain: tag_type_id, DB: category_id
            "created_timestamp": "created_timestamp",
        }

        schema_name = "portfolio" if db_type == "postgres" else None
        super().__init__("tag", schema_name=schema_name, field_map=field_map)


class SQLiteTagRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain field -> DB column mapping
        field_map = {
            "id": "id",
            "name": "name",
            "description": "description",
            "category_id": "category_id",
            "is_active": "is_active",
            "created_timestamp": "created_datetime",  # TODO: verify DB column name against portfolio schema
        }

        schema_name = "portfolio" if db_type == "postgres" else None
        super().__init__("tag", schema_name=schema_name, field_map=field_map)
