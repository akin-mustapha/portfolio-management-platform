from backend.application.portfolio.factory import build_portfolio_service
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
        current_tags = self._resolve_current_tags(
            asset_row.get("ticker", ""),
            tags,
            asset_row.get("broker"),
            asset_row.get("currency"),
        )
        return self._presenter.present_profile(
            asset_row, tags, industries, sectors, categories, current_tags
        )

    def _resolve_current_tags(
        self,
        ticker: str,
        all_tags: list,
        broker: str | None = None,
        currency: str | None = None,
    ) -> list:
        if not ticker:
            return []
        asset = self._service.get_asset_by_ticker(ticker, broker, currency)
        if not asset:
            return []
        tag_links = self._service.search_tag_by_asset_id(asset["id"])
        tag_id_to_name = {
            t["id"]: t["name"] for t in all_tags if t.get("id") and t.get("name")
        }
        return [
            tag_id_to_name[link["tag_id"]]
            for link in tag_links
            if link.get("tag_id") in tag_id_to_name
        ]

    def assign_tag(
        self,
        ticker: str,
        tag_id: int,
        broker: str | None = None,
        currency: str | None = None,
    ) -> str:
        asset = self._service.get_asset_by_ticker(ticker, broker, currency)
        if not asset:
            return f"Asset '{ticker}' not found."
        try:
            self._service.tag_asset({"asset_id": asset["id"], "tag_id": tag_id})
            return "Tag assigned."
        except Exception as e:
            return f"Error: {e}"
