from repository.base_repository import BaseRepository

class AssetDataRepository(BaseRepository):
    def __init__(self, client):
        self.client = client
        
    def save(self, data):
        with self.client as client:
            client.insert("asset_data", [data])

    def get_by_id(self, id: int):
        pass
    def get_all(self):
        pass
    def update(self, id: int, data):
        pass
    def delete(self, id: int):
        pass