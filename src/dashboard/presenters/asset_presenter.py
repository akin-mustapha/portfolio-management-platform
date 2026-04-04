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
            "asset_data": data.get("asset_data"),
        }

    def present_asset_history(self, data: dict) -> dict:

        return {
            "asset_price": self._asset_price_series_vm(data.get("asset_history", [])),
            "asset_value": self._asset_value_series_vm(data.get("asset_history", [])),
            "asset_risk": self._asset_risk_series_vm(data.get("asset_history", [])),
            "asset_dca_bias": self._asset_dca_bias_series_vm(
                data.get("asset_history", [])
            ),
            "asset_profit_range": self._asset_profit_range_series_vm(
                data.get("asset_history", [])
            ),
            "asset_fx_attribution": self._asset_fx_attribution_vm(
                data.get("asset_history", [])
            ),
            "asset_return": self._asset_return_series_vm(data.get("asset_history", [])),
            "asset_daily_return": self._asset_daily_return_series_vm(data.get("asset_history", [])),
        }

    # ---------- Table ----------

    def _asset_filter_vm(self, assets: list[dict]) -> dict:
        if not assets:
            return {
                "fields": [],
                "rows": [],
            }

        return {
            "fields": ["ticker"],
            "rows": [a.get("ticker") for a in assets],
        }

    # ---------- Line Chart ----------

    def _asset_price_series_vm(self, rows: list[dict]) -> dict:
        return {
            "dates": [r["data_date"] for r in rows],
            "values": [r["price"] for r in rows],
            "value_ma_30d": [r.get("value_ma_30d") for r in rows],
            "value_ma_50d": [r.get("value_ma_50d") for r in rows],
            "title": "Price",
        }

    def _asset_value_series_vm(self, rows: list[dict]) -> dict:
        return {
            "dates": [r["data_date"] for r in rows],
            "values": [r["value"] for r in rows],
            "title": "Asset Value Over Time",
        }

    def _asset_risk_series_vm(self, rows: list[dict]) -> dict:
        return {
            "dates": [r["data_date"] for r in rows],
            "values": [r["value_drawdown_pct_30d"] for r in rows],
        }

    def _asset_dca_bias_series_vm(self, rows: list[dict]) -> dict:
        return {
            "dates": [r["data_date"] for r in rows],
            "values": [r["dca_bias"] for r in rows],
        }

    def _asset_profit_range_series_vm(self, rows: list[dict]) -> dict:
        return {
            "dates": [r["data_date"] for r in rows],
            "values": [r["profit"] for r in rows],
            "high_30d": [r.get("recent_profit_high_30d") for r in rows],
            "low_30d": [r.get("recent_profit_low_30d") for r in rows],
        }

    def _asset_fx_attribution_vm(self, rows: list[dict]) -> dict:
        if not rows:
            return {"fx_impact": 0, "profit": 0}
        latest = rows[-1]
        return {
            "fx_impact": latest.get("fx_impact") or 0,
            "profit": latest.get("profit") or 0,
        }

    def _asset_return_series_vm(self, rows: list[dict]) -> dict:
        return {
            "dates": [r["data_date"] for r in rows],
            "values": [r.get("cumulative_value_return") for r in rows],
        }

    def _asset_daily_return_series_vm(self, rows: list[dict]) -> dict:
        return {
            "dates": [r["data_date"] for r in rows],
            "values": [r.get("daily_value_return") for r in rows],
        }
