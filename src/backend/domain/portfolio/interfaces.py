from typing import Protocol

from shared.repositories.interface import RepositoryInterface


class AssetQueryRepository(Protocol):
    def select_asset_by_tag(self, tag_id: int) -> list: ...
    def select_tag_by_asset(self, asset_id: int) -> list: ...
    def select_all_asset_tags(self) -> list: ...


__all__ = ["RepositoryInterface", "AssetQueryRepository"]
