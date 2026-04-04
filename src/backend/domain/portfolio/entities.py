from dataclasses import dataclass

from .value_objects import Ticker, Currency, Broker


@dataclass
class Asset:
    # NOTE: domain rule — ticker and name are required; id is None until persisted
    id: str | None
    ticker: Ticker
    name: str
    broker: Broker | None
    currency: Currency | None
    is_active: bool = True
    from_timestamp: str | None = None
    to_timestamp: str | None = None
    updated_timestamp: str | None = None

    def to_record(self):
        return {
            "ticker": str(self.ticker),
            "name": self.name,
            "broker": str(self.broker) if self.broker is not None else None,
            "currency": str(self.currency) if self.currency is not None else None,
            "is_active": self.is_active,
            "from_timestamp": self.from_timestamp,
            "to_timestamp": self.to_timestamp,
            "updated_timestamp": self.updated_timestamp,
        }


@dataclass
class Tag:
    # NOTE: domain rule — tag_type_id (category) is required; a tag without a category is invalid
    id: int | None
    name: str
    description: str
    tag_type_id: int
    created_timestamp: str

    def to_record(self):
        return {
            "name": self.name,
            "description": self.description,
            "tag_type_id": self.tag_type_id,
            "created_timestamp": self.created_timestamp,
        }


@dataclass
class Category:
    # NOTE: domain rule — name is required and must be unique
    id: int | None
    name: str
    description: str
    created_timestamp: str

    def to_record(self):
        return {
            "name": self.name,
            "description": self.description,
            "created_timestamp": self.created_timestamp,
        }


@dataclass
class AssetTag:
    # NOTE: domain rule — both asset_id and tag_id are required; neither can be None
    asset_id: int | None
    tag_id: int | None
    created_timestamp: str | None

    def to_record(self):
        return {
            "asset_id": self.asset_id,
            "tag_id": self.tag_id,
            "created_timestamp": self.created_timestamp,
        }


@dataclass
class Industry:
    # NOTE: domain rule — name is required and must be unique
    id: int | None
    name: str
    description: str
    created_timestamp: str | None

    def to_record(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_timestamp": self.created_timestamp,
        }


@dataclass
class Sector:
    # NOTE: domain rule — industry_id is required; a sector must belong to an industry
    id: int | None
    industry_id: int | None
    name: str
    description: str
    created_timestamp: str | None

    def to_record(self):
        return {
            "id": self.id,
            "industry_id": self.industry_id,
            "name": self.name,
            "description": self.description,
            "created_timestamp": self.created_timestamp,
        }
