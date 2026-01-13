from tagging_service.models import Item, Item_tag, Tag
from repository.base_repository import BaseRepository

class ItemRepository(BaseRepository):
    def __init__(self, entity_repository):
        self.entity_repository = entity_repository

    def insert(self, item: Item):
        record = item.to_record()
        res = self.entity_repository.insert([record])
        return Item(
            id=res.lastrowid,
            external_id=item.external_id,
            name=item.name,
            description=item.description,
            source_name=item.source_name,
            is_active=item.is_active,
            created_datetime=item.created_datetime,
            updated_datetime=item.updated_datetime,
        )
    
    def select_by_id(self, item_id: int):
        result = self.entity_repository.select_by_id(item_id)
        print(result)
        if result:
            row = result
            return Item(
                *row
            )
        return None
    
    def select_all(self):
        results = self.entity_repository.select_all()
        items = []
        for row in results.fetchall():
            items.append(
                Item(
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
    
    def update(self, item_id: int, item: Item):
      # record = item.to_record()
      # record["id"] = item_id
      # self.entity_repository.upsert([record], unique_key="id")

      pass

    def upsert(self, **kwargs):
      pass

    def delete(self, item_id: int):
      self.entity_repository.delete(item_id)

class TagRepository(BaseRepository):
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
    def select_by_id(self, tag_id: int):
        result = self.entity_repository.select_by_id(tag_id)
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
    

class ItemTagRepository(BaseRepository):
    def __init__(self, entity_repository):
        self.entity_repository = entity_repository
    
    def insert(self, item_tag: Item_tag):
        record = item_tag.to_record()
        res = self.entity_repository.insert([record])
        return Item_tag(
            item_id=item_tag.item_id,
            tag_id=item_tag.tag_id,
            is_active=item_tag.is_active,
            created_datetime=item_tag.created_datetime,
            updated_datetime=item_tag.updated_datetime

        )
    
    def select_by_id(self, item_tag_id: int):
        result = self.entity_repository.select_by_id(item_tag_id)
        if result:
            return Item_tag(*result
            )
        return None

    def select_all(self):
        results = self.entity_repository.select_all()
        item_tags = []
        for row in results:
            item_tags.append(
                Item_tag(*row
                )
            )
        return item_tags

    
    def delete(self, item_tag: Item_tag):
        pass

    def update(self, **kwargs):
        pass
    
    def upsert(self, **kwargs):
        pass

class DomainRepositoryFactory:
    registry = {
        "item": ItemRepository,
        "tag": TagRepository,
        "item_tag": ItemTagRepository,
    }

    @classmethod
    def get_repository(cls, entity_name, entity_repository):
        repository_class = cls.registry.get(entity_name)
        if not repository_class:
            raise ValueError(f"No repository found for entity: {entity_name}")
        return repository_class(entity_repository)

