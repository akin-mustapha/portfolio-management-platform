from abc import ABC, abstractmethod


class BaseRepository(ABC):
    @abstractmethod
    def save(self, **kwargs):
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def get_by_id(self, **kwargs):
        raise NotImplementedError("Subclasses must implement this method")
    
    @abstractmethod
    def get_all(self, **kwargs):
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def update(self, **kwargs):
        raise NotImplementedError("Subclasses must implement this method")
    
    @abstractmethod
    def delete(self, **kwargs):
        raise NotImplementedError("Subclasses must implement this method")