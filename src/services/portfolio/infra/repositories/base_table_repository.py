from typing import Dict, Iterable
from src.services.portfolio.infra.repositories.entity_repository import EntityRepositoryFactory
from src.services.portfolio.app.interfaces import BaseRepositoryInterface
import logging

class BaseTableRepository(BaseRepositoryInterface):
    def __init__(self, entity_name: str, schema_name: str = None, field_map: Dict[str, str] = None):
        """
        :param entity_name: Table name in DB
        :param schema_name: Schema name (Postgres only)
        :param field_map: Mapping from domain name -> DB column name
        """
        self._field_map = field_map or {}
        self._entity_repo = EntityRepositoryFactory.get_repository(entity_name, schema_name)

    def _to_db_fields(self, data: Dict) -> Dict:
        """Map domain-friendly fields to DB column names."""
        return {self._field_map.get(k, k): v for k, v in data.items()}

    def _from_db_fields(self, data: Dict) -> Dict:
        """Map DB column names back to domain-friendly fields."""
        reverse_map = {v: k for k, v in self._field_map.items()}
        return {reverse_map.get(k, k): v for k, v in data.items()}

    def insert(self, data: Dict):
        for record in data:
            logging.info(f"Inserting data into {self._entity_repo._entity_name}: {record}")
            db_data = self._to_db_fields(record)
            self._entity_repo.insert(db_data)

    def upsert(self, data: Dict, unique_key: str):
        for record in data:
            db_data = self._to_db_fields(record)
            db_unique_key = self._field_map.get(unique_key, unique_key)
            self._entity_repo.upsert([db_data], unique_key=db_unique_key)


    def select(self, params: Dict):
        db_params = self._to_db_fields(params)
        result = self._entity_repo.select(db_params)
        if result:
            return self._from_db_fields(dict(result))
        return None

    def select_all(self):
        results = self._entity_repo.select_all()
        return [self._from_db_fields(dict(r)) for r in results]

    def update(self, params: Dict, data: Dict):
        db_params = self._to_db_fields(params)
        db_data = self._to_db_fields(data)
        return self._entity_repo.update(db_params, db_data)

    def delete(self, params: Dict):
        db_params = self._to_db_fields(params)
        return self._entity_repo.delete(db_params)