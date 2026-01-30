from src.shared.repositories.base_repository import BaseRepository

class PortfolioSnapshotRepository(BaseRepository):
    def __init__(self, client, entity_name):
        self.client = client
        self.entity_name = entity_name
        
    def insert(self, data):
        with self.client as client:
            client.insert("portfolio_snapshot", [data])

    def get_by_id(self, id: int):
        pass
    def get_all(self):
        pass
    def update(self, id: int, data):
        pass
    def delete(self, id: int):
        pass