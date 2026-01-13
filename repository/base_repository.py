from abc import ABC, abstractmethod


class BaseRepository(ABC):
    @abstractmethod
    def insert(self, **kwargs):
        raise NotImplementedError("Subclasses must implement this method")
    
    @abstractmethod
    def upsert(self, **kwargs):
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def select_by_id(self, **kwargs):
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