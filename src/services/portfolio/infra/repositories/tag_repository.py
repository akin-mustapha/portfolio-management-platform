from services.portfolio.infra.repositories.base_table_repository import BaseTableRepository

class PostgresTagRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain name -> DB column mapping
        field_map = {
            "name": "name",
            "description": "description",
            "tag_type_id": "category_id",
            "created_timestamp": "created_timestamp",
        }

        schema_name = "portfolio" if db_type == "postgres" else None
        super().__init__("tag", schema_name=schema_name, field_map=field_map)


class SQLiteTagRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain name -> DB column mapping
        field_map = {
            "id": "id",
            "name": "name",
            "description": "description",
            "category_id": "category_id",
            "is_active": "is_active",
            "data_timestamp": "created_datetime",
            "processed_timestamp": "updated_datetime",
        }

        schema_name = "portfolio" if db_type == "postgres" else None
        super().__init__("tag", schema_name=schema_name, field_map=field_map)