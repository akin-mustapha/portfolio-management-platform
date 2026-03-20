from backend.services.portfolio.portfolio_service_builder import build_portfolio_service
from ..presenters.asset_profile_presenter import AssetProfilePresenter


class AssetProfileController:
    def __init__(self):
        self._service = build_portfolio_service()
        self._presenter = AssetProfilePresenter()

    def get_profile(self, asset_row: dict) -> dict:
        tags = self._service.get_all_tags()
        industries = self._service.get_all_industries()
        sectors = self._service.get_all_sectors()
        categories = self._service.get_all_categories()
        current_tags = self._resolve_current_tags(asset_row.get("name", ""), tags)
        return self._presenter.present_profile(asset_row, tags, industries, sectors, categories, current_tags)

    def _resolve_current_tags(self, asset_name: str, all_tags: list) -> list:
        if not asset_name:
            return []
        asset = self._service.get_asset_by_name(asset_name)
        if not asset:
            return []
        from backend.services.portfolio.domain.entities import Asset
        asset_obj = Asset(id=asset["id"], external_id="", name=asset_name, description="", source_name="", created_timestamp="")
        tag_links = self._service.search_tag_by_asset(asset_obj)
        tag_id_to_name = {t["id"]: t["name"] for t in all_tags if t.get("id") and t.get("name")}
        return [tag_id_to_name[link["tag_id"]] for link in tag_links if link.get("tag_id") in tag_id_to_name]

    def assign_tag(self, asset_name: str, tag_id: int) -> str:
        asset = self._service.get_asset_by_name(asset_name)
        if not asset:
            return f"Asset '{asset_name}' not found."
        try:
            self._service.tag_asset({"asset_id": asset["id"], "tag_id": tag_id})
            return "Tag assigned."
        except Exception as e:
            return f"Error: {e}"
