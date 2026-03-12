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
        snapshot = data.get("portfolio_current_snapshot", {})
        assets = data.get("assets", [])
        return {
            "kpi": self._kpi(snapshot),
            "asset_table": self._asset_table_vm(assets),
            "portfolio_value_series": self._portfolio_value_series_vm(
                data.get("portfolio_history", [])
            ),
            "portfolio_pnl_series": self._portfolio_pnl_series_vm(data.get('portfolio_history', [])),
            "pnl_bar_series": self._pnl_bar_series_vm(
                data.get("pnl", [])
            ),
            "position_weight_series": self._position_weight_series_vm(
                assets, snapshot.get("total_value", 0)
            ),
        }
        
    def _kpi(self, rows: dict) -> dict:
        total_value = rows.get('total_value', 0)
        cash = rows.get('cash_available_to_trade', 0)
        return {
            "value": total_value,
            "currency": rows.get('currency', "#"),
            "realized_pnl": rows.get('investments_realized_pnl', 0),
            "unrealized_pnl": rows.get('investments_unrealized_pnl', 0),
            "total_cost": rows.get('investments_total_cost', 0),
            "cash": cash,
            "cash_pct": (cash / total_value * 100) if total_value else 0,
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
        
    # ---------- Position Weight ----------

    def _position_weight_series_vm(self, assets: list[dict], total_value: float) -> list[dict]:
        if not assets or total_value == 0:
            return []
        items = sorted(
            [{"ticker": a["ticker"], "weight_pct": a["value"] / total_value * 100} for a in assets],
            key=lambda x: x["weight_pct"],
            reverse=True,
        )
        top = items[:15]
        rest = sum(i["weight_pct"] for i in items[15:])
        if rest > 0:
            top.append({"ticker": "Other", "weight_pct": rest})
        return top

    # ---------- Bar Chart ----------

    def _pnl_bar_series_vm(self, rows: list[dict]) -> dict:
        return {
            "labels": [r["asset"] for r in rows],
            "values": [r["pnl"] for r in rows],
        }