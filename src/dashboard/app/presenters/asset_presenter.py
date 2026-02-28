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
            "asset_filter": self._asset_filter_vm(data.get("asset_data", [])),
            "asset_data": data.get("asset_data")
        }

    def present_asset_history(self, data: dict) -> dict:
        
        return {
            "asset_price": self._asset_price_series_vm(data.get("asset_history", [])),
            "asset_value": self._asset_value_series_vm(data.get("asset_history", [])),
            "asset_risk": self._asset_risk_series_vm(data.get("asset_history", [])),
            "asset_dca_bias": self._asset_dca_bias_series_vm(data.get("asset_history", [])),
        }
    # ---------- Table ----------

    def _asset_filter_vm(self, assets: list[dict]) -> dict:
        if not assets:
            return {
                "fields": [],
                "rows": [],
            }

        return {
            "fields": ['ticker'],
            "rows": [a.get('ticker') for a in assets],
        }

    # ---------- Line Chart ----------

    def _asset_price_series_vm(self, rows: list[dict]) -> dict:
        return {
            "dates": [r["data_date"] for r in rows],
            "values": [r["price"] for r in rows],
            # y=["price", "ma_30d", "ma_50d"],
            "title": "Price"
        }

    def _asset_value_series_vm(self, rows: list[dict]) -> dict:
        return {
            "dates": [r["data_date"] for r in rows],
            "values": [r["value"] for r in rows],
            "title": "Asset Value Over Time"
        }

    def _asset_risk_series_vm(self, rows: list[dict]) -> dict:
        return {
            "dates": [r["data_date"] for r in rows],
            "values": [r["pct_drawdown"] for r in rows],
        }

    def _asset_dca_bias_series_vm(self, rows: list[dict]) -> dict:
        return {
            "dates": [r["data_date"] for r in rows],
            "values": [r["dca_bias"] for r in rows],
        }