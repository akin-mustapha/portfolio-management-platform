

from repository.entity_repository import EntityRepository

# Ingredient
from database.client import SQLModelClient

if __name__ == "__main__":
  client = SQLModelClient(database_url="sqlite:///./data/trading212.db")

  result = client.execute("SELECT TOP 1 * FROM raw_data WHERE id =: id", params={"id": 1})
  print(result)
  asset_snapshot_repo = EntityRepository("asset_snapshot", client)
  res = asset_snapshot_repo.select({"id": 1})
  print(res[0])