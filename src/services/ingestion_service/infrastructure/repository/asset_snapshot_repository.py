
from repository.base_repository import BaseRepository

class AssetSnapshotRepository(BaseRepository):
    def __init__(self, client):
        self.client = client
        self.entity_name = 'asset_snapshot'
    
    def save(self, data):
        with self.client as client:
            client.insert("asset_snapshot", [data])

    def get_by_id(self, id: int):
        pass
    def get_all(self):
        pass
    def update(self, id: int, data):
        pass
    def delete(self, id: int):
        pass