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
        return self._presenter.present_profile(asset_row, tags, industries, sectors, categories)

    def assign_tag(self, asset_name: str, tag_id: int) -> str:
        asset = self._service.get_asset_by_name(asset_name)
        if not asset:
            return f"Asset '{asset_name}' not found."
        try:
            self._service.tag_asset({"asset_id": asset["id"], "tag_id": tag_id})
            return "Tag assigned."
        except Exception as e:
            return f"Error: {e}"
