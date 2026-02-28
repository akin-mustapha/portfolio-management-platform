from src.services.ingestion.infra.repositories.base_table_repository import BaseTableRepository

class PostgresPortfolioSnapshotRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain name -> DB column mapping
        field_map = {
            "id": "id",
            "external_id": "external_id",
            "data_date": "data_date",
            "currency": "currency",
            "current_value": "current_value",
            "total_value": "total_value",
            "total_cost": "total_cost",
            "unrealized_profit": "unrealized_profit",
            "realized_profit": "realized_profit",
        }

        schema_name = "portfolio" if db_type == "postgres" else None
        super().__init__("portfolio_snapshot", schema_name=schema_name, field_map=field_map)


class SQLitePortfolioSnapshotRepository(BaseTableRepository):
    def __init__(self, db_type: str = "postgres"):
        # Domain name -> DB column mapping
        field_map = {
            "id": "id",
            "external_id": "external_id",
            "data_date": "data_date",
            "currency": "currency",
            "current_value": "current_value",
            "total_value": "total_value",
            "total_cost": "total_cost",
            "unrealized_profit": "unrealized_profit",
            "realized_profit": "realized_profit",
        }

        schema_name = "portfolio" if db_type == "postgres" else None
        super().__init__("portfolio_snapshot", schema_name=schema_name, field_map=field_map)
