from src.services.ingestion.infra.database.database_client import PostgresRepository, SQLiteRespository

class PostgresAssetRepository(PostgresRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain name -> DB column mapping
        field_map = {
            "id": "id",
            "external_id": "external_id",
            "name": "name",
            "description": "description",
            "source_name": "source_name",
            "is_active": "is_active",
            "created_datetime": "created_timestamp",
            "processed_timestamp": "updated_timestamp",
        }

        schema_name = "portfolio" if db_type == "postgres" else None
        super().__init__("asset", schema_name=schema_name, field_mapping=field_map)


class SQLiteAssetRepository(SQLiteRespository):
    def __init__(self, db_type: str = "postgres"):
        # Domain name -> DB column mapping
        field_map = {
            "id": "id",
            "external_id": "external_id",
            "name": "name",
            "description": "description",
            "source_name": "source_name",
            "is_active": "is_active",
            "data_timestamp": "created_datetime",
            "processed_timestamp": "updated_datetime",
        }

        schema_name = "portfolio" if db_type == "postgres" else None
        super().__init__("asset", schema_name=schema_name, field_mapping=field_map)
