from abc import ABC, abstractmethod
from collections.abc import Iterable


class RepositoryInterface(ABC):
    def __init__(
        self,
        entity_name: str,
        schema_name: str | None = None,
        field_map: dict[str, str] | None = None,
    ):
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
    def insert(self, records: Iterable[dict]):
        raise NotImplementedError

    @abstractmethod
    def upsert(self, records: Iterable[dict], unique_key: list[str]):
        raise NotImplementedError

    @abstractmethod
    def select(self, params: dict):
        raise NotImplementedError

    @abstractmethod
    def select_all(self):
        raise NotImplementedError

    @abstractmethod
    def select_all_by(self, params: dict):
        raise NotImplementedError

    @abstractmethod
    def update(self, params: dict, data: dict):
        raise NotImplementedError

    @abstractmethod
    def delete(self, params: dict):
        raise NotImplementedError
