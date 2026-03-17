try:
    from src.shared.repositories.base_table_repository import BaseTableRepository
except ImportError:
    from shared.repositories.base_table_repository import BaseTableRepository


class PostgresRepository(BaseTableRepository):
    def __init__(self, entity_name: str, schema_name: str = None, field_mapping=None):
        super().__init__(entity_name, schema_name, field_map=field_mapping)
