from src.app.interfaces.interface import BaseRepositoryInterface

class AssetRepository(BaseRepositoryInterface):
    def __init__(self, entity_name, schema_name):
        self._schema_name = schema_name
        self._entity_name = entity_name
   
    def insert(self, data):
        pass

    def get_by_id(self, id: int):
        pass

    def select_all(self):
        pass

    def update(self, id: int, data):
        pass

    def delete(self, id: int):
        pass