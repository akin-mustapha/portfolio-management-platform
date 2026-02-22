from dataclasses import dataclass

@dataclass
class Asset:
    id: int | None
    external_id: str
    name: str
    description: str
    source_name: str
    is_active: bool
    created_timestamp: str
    updated_timestamp: str | None

    to_record = lambda self: {
        "external_id": self.external_id,
        "name": self.name,
        "description": self.description,
        "source_name": self.source_name,
        "is_active": self.is_active,
        "created_timestamp": self.created_timestamp,
        "updated_timestamp": self.updated_timestamp,
    }
    
@dataclass
class Tag:
    id: int | None
    name: str
    description: str
    tag_type_id: int
    is_active: bool
    created_timestamp: str
    updated_timestamp: str | None

    to_record = lambda self: {
        "name": self.name,
        "description": self.description,
        "tag_type_id": self.tag_type_id,
        "is_active": self.is_active,
        "created_timestamp": self.created_timestamp,
        "updated_timestamp": self.updated_timestamp,
    }

@dataclass
class Category:
    id: int | None
    name: str
    is_active: bool
    created_timestamp: str
    updated_timestamp: str | None

    to_record = lambda self: {
        "name": self.name,
        "is_active": self.is_active,
        "created_timestamp": self.created_timestamp,
        "updated_timestamp": self.updated_timestamp,
    }

@dataclass
class AssetTag:
    item_id: int | None
    tag_id: int | None
    is_active: bool
    created_timestamp: str | None
    updated_timestamp: str | None

    to_record = lambda self: {
        "asset_id": self.item_id,
        "tag_id": self.tag_id,
        "is_active": self.is_active,
        "created_timestamp": self.created_timestamp,
        "updated_timestamp": self.updated_timestamp,
    }
    
@dataclass
class Industry:
    id: int | None
    name: str
    created_timestamp: str | None
    updated_timestamp: str | None

    to_record = lambda self: {
        "industry_id": self.id,
        "name": self.name,
        "created_timestamp": self.created_timestamp,
        "updated_timestamp": self.updated_timestamp,
    }
    
@dataclass
class Sector:
    id: int | None
    industry_id: int | None
    name: str
    created_timestamp: str | None
    updated_timestamp: str | None

    to_record = lambda self: {
        "sector_id": self.id,
        "industry_id": self.industry_id,
        "name": self.name,
        "created_timestamp": self.created_timestamp,
        "updated_timestamp": self.updated_timestamp,
    }