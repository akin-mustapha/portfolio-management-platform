from src.infra.repositories.base_table_repository import BaseTableRepository
class AssetRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain name -> DB column mapping
        field_map = {
            "id": "id",
            "external_id": "external_id",
            "name": "name",
            "description": "description",
            "source": "source_name",           # domain field = source, DB column = source_name
            "is_active": "is_active",
            "created_at": "created_timestamp", # domain field = created_at, DB column = created_timestamp
            "updated_at": "updated_timestamp",
        }

        schema_name = "portfolio" if db_type == "postgres" else None
        super().__init__("asset", schema_name=schema_name, field_map=field_map)