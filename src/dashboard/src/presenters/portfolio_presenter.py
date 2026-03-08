class PortfolioPresenter:
    """
    Presenter for the Portfolio Dashboard screen.

    Input contract (from Service):
    {
        "assets": List[Dict],
        "portfolio_value": List[Dict],
        "pnl": List[Dict]
    }
    """

    def present(self, data: dict) -> dict:
        return {
            "kpi": self._kpi(data.get("portfolio_current_snapshot", {})),
            "asset_table": self._asset_table_vm(data.get("assets", [])),
            "portfolio_value_series": self._portfolio_value_series_vm(
                data.get("portfolio_history", [])
            ),
            "portfolio_pnl_series": self._portfolio_pnl_series_vm(data.get('portfolio_history', [])),
            "pnl_bar_series": self._pnl_bar_series_vm(
                data.get("pnl", [])
            ),
        }
        
    def _kpi(self, rows: dict) -> dict:
        return {
            "value": rows.get('total_value', 0),
            "currency": rows.get('currency', "#"),
            "realized_pnl": rows.get('investments_realized_pnl', 0),
            "unrealized_pnl": rows.get('investments_unrealized_pnl', 0),
            "total_cost": rows.get('investments_total_cost', 0),
        }

    # ---------- Table ----------

    def _asset_table_vm(self, assets: list[dict]) -> dict:
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
            "values": [r["total_value"] for r in rows],
        }
        
    def _portfolio_pnl_series_vm(self, rows: list[dict]) -> dict:
        return {
            "dates": [r["data_date"] for r in rows],
            "values": [r["investments_unrealized_pnl"] for r in rows],
        }
        
    # ---------- Bar Chart ----------

    def _pnl_bar_series_vm(self, rows: list[dict]) -> dict:
        return {
            "labels": [r["asset"] for r in rows],
            "values": [r["pnl"] for r in rows],
        }