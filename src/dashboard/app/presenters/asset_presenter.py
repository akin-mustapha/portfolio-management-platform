class AssetPresenter:
    """
    Presenter for the Asset Dashboard screen.

    Input contract (from Service):
    {
        "assets": List[Dict],
        "portfolio_value": List[Dict],
        "pnl": List[Dict]
    }
    """

    def present(self, data: dict) -> dict:
        return {
            "kpi": None,
            "asset_filter": self._asset_filter_vm(data.get("assets", [])),
            "portfolio_value_series": self._portfolio_value_series_vm(
                data.get("portfolio_value", [])
            ),
            "pnl_bar_series": self._pnl_bar_series_vm(
                data.get("pnl", [])
            ),
        }

    # ---------- Table ----------

    def _asset_filter_vm(self, assets: list[dict]) -> dict:
        if not assets:
            return {
                "fields": [],
                "rows": [],
            }

        return {
            "fields": list(assets[0].keys()),
            "rows": assets,
        }

    # ---------- Line Chart ----------

    def _portfolio_value_series_vm(self, rows: list[dict]) -> dict:
        return {
            "dates": [r["data_date"] for r in rows],
            "values": [r["unrealized_return"] for r in rows],
        }

    # ---------- Bar Chart ----------

    def _pnl_bar_series_vm(self, rows: list[dict]) -> dict:
        return {
            "labels": [r["asset"] for r in rows],
            "values": [r["pnl"] for r in rows],
        }