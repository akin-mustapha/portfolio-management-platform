class AssetProfilePresenter:

    def present_profile(self, asset_row: dict, tags: list, industries: list, sectors: list, categories: list) -> dict:
        return {
            "ticker": asset_row.get("ticker", "—"),
            "name": asset_row.get("name", "—"),
            "description": asset_row.get("asset_description", "—"),
            "created": str(asset_row.get("data_date", "—")),
            "last_ingestion": str(asset_row.get("data_date", "—")),
            "tag_options": self._to_options(tags, "name", "id"),
            "industry_options": self._to_options(industries, "name", "id"),
            "sector_options": self._to_options(sectors, "name", "id"),
            "category_options": self._to_options(categories, "name", "id"),
        }

    def _to_options(self, items: list, label_key: str, value_key: str) -> list:
        return [{"label": i[label_key], "value": i[value_key]} for i in items if i.get(label_key) and i.get(value_key) is not None]
