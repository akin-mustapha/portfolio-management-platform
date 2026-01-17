from repository.base_repository import BaseRepository

class AssetRepository(BaseRepository):
    def __init__(self, client, entity_name):
        self.client = client
        self.entity_name = entity_name
    
    @property
    def entity_name(self):
        return self.entity_name

    @entity_name.setter
    def entity_name(self, entity_name):
        self.entity_name = entity_name
   
    def insert(self, data):
        with self.client as client:
            client.insert("asset", [data])

    def get_by_id(self, id: int):
        pass

    def select_all(self):
        pass

    def update(self, id: int, data):
        pass

    def delete(self, id: int):
        pass