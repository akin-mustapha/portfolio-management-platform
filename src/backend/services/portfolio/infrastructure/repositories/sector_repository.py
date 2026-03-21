from shared.repositories.base_table_repository import BaseTableRepository

class PostgresSectorRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain field -> DB column mapping
        field_map = {
            "id": "id",
            "name": "name",
            "description": "description",
            "industry_id": "industry_id",
            "is_active": "is_active",
            "created_timestamp": "created_timestamp",  # TODO: verify DB column name against portfolio schema
        }

        schema_name = "portfolio" if db_type == "postgres" else None
        super().__init__("sector", schema_name=schema_name, field_map=field_map)


class SQLiteSectorRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain field -> DB column mapping
        field_map = {
            "id": "id",
            "name": "name",
            "description": "description",
            "industry_id": "industry_id",
            "is_active": "is_active",
            "created_datetime": "created_timestamp",
            "processed_timestamp": "updated_timestamp",
        }

        schema_name = "portfolio" if db_type == "postgres" else None
        super().__init__("sector", schema_name=schema_name, field_map=field_map)
