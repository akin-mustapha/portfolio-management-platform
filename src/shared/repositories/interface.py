from abc import ABC, abstractmethod
from typing import Dict, Iterable


class RepositoryInterface(ABC):
    def __init__(self, entity_name: str, schema_name: str = None, field_map: Dict[str, str] = None):
        self._entity_name = entity_name
        self._schema_name = schema_name
        self._field_map = field_map or {}

    @property
    def entity_name(self):
        return self._entity_name

    @property
    def schema_name(self):
        return self._schema_name

    @abstractmethod
    def insert(self, records: Iterable[Dict]):
        raise NotImplementedError

    @abstractmethod
    def upsert(self, records: Iterable[Dict], unique_key: list[str]):
        raise NotImplementedError

    @abstractmethod
    def select(self, params: Dict):
        raise NotImplementedError

    @abstractmethod
    def select_all(self):
        raise NotImplementedError

    @abstractmethod
    def update(self, params: Dict, data: Dict):
        raise NotImplementedError

    @abstractmethod
    def delete(self, params: Dict):
        raise NotImplementedError
