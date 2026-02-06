from dataclasses import dataclass

@dataclass
class Asset:
    id: int | None
    external_id: str
    name: str
    description: str
    source_name: str
    is_active: bool
    created_datetime: str
    updated_datetime: str | None

    to_record = lambda self: {
        "external_id": self.external_id,
        "name": self.name,
        "description": self.description,
        "source_name": self.source_name,
        "is_active": self.is_active,
        "created_datetime": self.created_datetime,
        "updated_datetime": self.updated_datetime,
    }
    
@dataclass
class Tag:
    id: int | None
    name: str
    description: str
    tag_type_id: int
    is_active: bool
    created_datetime: str
    updated_datetime: str | None

    to_record = lambda self: {
        "name": self.name,
        "description": self.description,
        "tag_type_id": self.tag_type_id,
        "is_active": self.is_active,
        "created_datetime": self.created_datetime,
        "updated_datetime": self.updated_datetime,
    }

@dataclass
class Category:
    id: int | None
    name: str
    is_active: bool
    created_datetime: str
    updated_datetime: str | None

    to_record = lambda self: {
        "name": self.name,
        "is_active": self.is_active,
        "created_datetime": self.created_datetime,
        "updated_datetime": self.updated_datetime,
    }

@dataclass
class AssetTag:
    item_id: int
    tag_id: int
    is_active: bool
    created_datetime: str | None
    updated_datetime: str | None

    to_record = lambda self: {
        "asset_id": self.item_id,
        "tag_id": self.tag_id,
        "is_active": self.is_active,
        "created_datetime": self.created_datetime,
        "updated_datetime": self.updated_datetime,
    }