from src.services.ingestion.infra.repositories.base_table_repository import BaseTableRepository

class PostgresAssetSnapshotRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain name -> DB column mapping
        field_map = {
            "id": "id",
            "asset_id": "asset_id",
            "data_date": "data_date",
            "currency": "currency",
            "local_currency": "local_currency",           # domain field = source, DB column = source_name
            "share": "share",
            "avg_price": "avg_price", # domain field = created_at, DB column = created_timestamp
            "value": "value",
            "cost": "cost",
            "profit": "profit",
            "fx_impact": "fx_impact",
        }

        schema_name = "portfolio" if db_type == "postgres" else None
        super().__init__("asset_snapshot", schema_name=schema_name, field_map=field_map)


class SQLiteAssetSnapshotRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain name -> DB column mapping
        field_map = {
            "id": "id",
            "asset_id": "asset_id",
            "data_date": "data_date",
            "currency": "currency",
            "local_currency": "local_currency",           # domain field = source, DB column = source_name
            "share": "share",
            "avg_price": "avg_price", # domain field = created_at, DB column = created_timestamp
            "value": "value",
            "cost": "cost",
            "profit": "profit",
            "fx_impact": "fx_impact",
        }

        schema_name = "portfolio" if db_type == "postgres" else None
        super().__init__("asset_snapshot", schema_name=schema_name, field_map=field_map)
