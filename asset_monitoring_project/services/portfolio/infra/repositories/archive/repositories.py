from src.services.portfolio.app.models import Asset, AssetTag, Tag
from src.services.portfolio.app.interfaces import BaseRepositoryInterface
from datetime import datetime, UTC

# Domain Repositories
class AssetRepository(BaseRepositoryInterface):
    def __init__(self, entity_repository):
        self.entity_repository = entity_repository

    def insert(self, asset: Asset):
        record = asset.to_record()
        res = self.entity_repository.insert([record])
        return Asset(
            id=res.lastrowid,
            external_id=asset.external_id,
            name=asset.name,
            description=asset.description,
            source_name=asset.source_name,
            is_active=asset.is_active,
            created_datetime=asset.created_datetime,
            updated_datetime=asset.updated_datetime,
        )
    
    def select(self, asset_id: int):
        result = self.entity_repository.select({"id": asset_id})
        if result:
            row = result
            return Asset(
                *row
            )
        return None
    
    def select_all(self):
        results = self.entity_repository.select_all()
        items = []
        for row in results.fetchall():
            items.append(
                Asset(
                    id=row["id"],
                    external_id=row["external_id"],
                    name=row["name"],
                    description=row["description"],
                    source_name=row["source_name"],
                    is_active=row["is_active"],
                    created_datetime=row["created_datetime"],
                    updated_datetime=row["updated_datetime"],
                )
            )
        return items
    
    def update(self, item_id: int, item: Asset):
      # record = item.to_record()
      # record["id"] = item_id
      # self.entity_repository.upsert([record], unique_key="id")

      pass

    def upsert(self, **kwargs):
      pass

    def delete(self, item_id: int):
      self.entity_repository.delete(item_id)

class TagRepository(BaseRepositoryInterface):
    def __init__(self, entity_repository):
        self.entity_repository = entity_repository

    def insert(self, tag: Tag):
        record = tag.to_record()
        res = self.entity_repository.insert([record])
        return Tag(
            id=res.lastrowid,
            name=tag.name,
            description=tag.description,
            tag_type_id=tag.tag_type_id,
            is_active=tag.is_active,
            created_datetime=tag.created_datetime,
            updated_datetime=tag.updated_datetime,
        )
    
    def select(self, tag_id: int):
        result = self.entity_repository.select({"id": tag_id})
        if result:
            return Tag(
                *result
            )
        return None
    
    def select_all(self):
        results = self.entity_repository.select_all()
        tags = []
        for row in results:
            tags.append(
                Tag(
                    *row
                )
            )
        return tags
    
    def update(self, tag_id: int, tag: Tag):
      # record = tag.to_record()
      # record["id"] = tag_id
      # self.entity_repository.upsert([record], unique_key="id")

      pass

    def upsert(self, **kwargs):
      pass

    def delete(self, tag_id: int):
      self.entity_repository.delete(tag_id)
    

class AssetTagRepository(BaseRepositoryInterface):
    def __init__(self, entity_repository):
        self.entity_repository = entity_repository
    
    def insert(self, item_tag: AssetTag):
        record = item_tag.to_record()
        res = self.entity_repository.insert([record])
        return AssetTag(
            item_id=item_tag.item_id,
            tag_id=item_tag.tag_id,
            is_active=item_tag.is_active,
            created_datetime=item_tag.created_datetime,
            updated_datetime=item_tag.updated_datetime

        )
    def insert_2(self, item_tag: dict):
        record = {

            "tag_id": item_tag.get("tag_id"),
            "asset_id": item_tag.get("item_id"),
            "is_active": 1,
            "created_datetime": datetime.now(UTC)
        }
        res = self.entity_repository.insert([record])
        return record
    def select(self, item_tag_id: int):
        result = self.entity_repository.select({"tag_id": item_tag_id})
        if result:
            return AssetTag(*result
            )
        return None

    def select_all(self):
        results = self.entity_repository.select_all()
        item_tags = []
        for row in results:
            item_tags.append(
                AssetTag(*row
                )
            )
        return item_tags

    
    def delete(self, item_tag: AssetTag):
        params = {'asset_id': item_tag.item_id, 'tag_id': item_tag.tag_id}

        self.entity_repository.update(params, {'is_active': 0, 'updated_datetime': '1'})

    def update(self, **kwargs):
        pass
    
    def upsert(self, **kwargs):
        pass

class DomainRepositoryFactory:
    registry = {
        "asset": AssetRepository,
        "tag": TagRepository,
        "asset_tag": AssetTagRepository,
    }

    @classmethod
    def get_repository(cls, entity_name, entity_repository):
        repository_class = cls.registry.get(entity_name)
        if not repository_class:
            raise ValueError(f"No repository found for entity: {entity_name}")
        return repository_class(entity_repository)

