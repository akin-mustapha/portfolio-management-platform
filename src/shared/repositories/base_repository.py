from abc import ABC, abstractmethod


class BaseRepository(ABC):
    def __init__(self, client, entity_name):
        self.client = client
        self.entity_name = entity_name

    @property
    def entity_name(self):
        return self.entity_name
    @entity_name.setter
    def entity_name(self, entity_name):
        self.entity_name = entity_name

    @abstractmethod
    def insert(self, **kwargs):
        raise NotImplementedError("Subclasses must implement this method")
    @abstractmethod
    def upsert(self, **kwargs):
        raise NotImplementedError("Subclasses must implement this method")
    @abstractmethod
    def select(self, **kwargs):
        raise NotImplementedError("Subclasses must implement this method")
    @abstractmethod
    def select_all(self, **kwargs):
        raise NotImplementedError("Subclasses must implement this method")
    @abstractmethod
    def update(self, **kwargs):
        raise NotImplementedError("Subclasses must implement this method")
    @abstractmethod
    def delete(self, **kwargs):
        raise NotImplementedError("Subclasses must implement this method")