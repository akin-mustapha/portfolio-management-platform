from src.services.portfolio.infra.repositories.base_table_repository import BaseTableRepository

class PostgresIndustryRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain name -> DB column mapping
        industry_dto = {
            "id": "id",
            "name": "name",
            "description": "description",
            "is_active": "is_active",
            "created_timestamp": "created_timestamp",
            "updated_timestamp": "updated_timestamp",
        }

        schema_name = "portfolio" if db_type == "postgres" else None
        super().__init__("industry", schema_name=schema_name, field_map=industry_dto)


class SQLiteIndustryRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain name -> DB column mapping
        industry_dto = {
            "id": "id",
            "name": "name",
            "description": "description",
            "is_active": "is_active",
            "created_timestamp": "created_timestamp",
            "updated_timestamp": "updated_timestamp",
        }

        schema_name = "portfolio" if db_type == "postgres" else None
        super().__init__("industry", schema_name=schema_name, field_map=industry_dto)