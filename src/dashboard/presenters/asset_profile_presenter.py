class AssetProfilePresenter:

    def present_profile(self, asset_row: dict, tags: list, industries: list, sectors: list, categories: list, current_tags: list = None) -> dict:
        return {
            "ticker": asset_row.get("ticker", "—"),
            "name": asset_row.get("name", "—"),
            "description": asset_row.get("asset_description") or asset_row.get("name", "—"),
            "created": self._format_date(asset_row.get("data_date")),
            "last_ingestion": self._format_date(asset_row.get("data_date")),
            "tag_options": self._to_options(tags, "name", "id"),
            "industry_options": self._to_options(industries, "name", "id"),
            "sector_options": self._to_options(sectors, "name", "id"),
            "category_options": self._to_options(categories, "name", "id"),
            "current_tags": current_tags or [],
        }

    def _format_date(self, value) -> str:
        if value is None:
            return "—"
        s = str(value)
        return s[:10] if len(s) >= 10 else s

    def _to_options(self, items: list, label_key: str, value_key: str) -> list:
        return [{"label": i[label_key], "value": i[value_key]} for i in items if i.get(label_key) and i.get(value_key) is not None]
