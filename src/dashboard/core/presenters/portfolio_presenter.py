import math
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
        assets_history = data.get("assets_history", [])
        return {
            "kpi": self._kpi(snapshot, assets, data.get("portfolio_history", [])),
            "asset_table": self._asset_table_vm(assets),
            "portfolio_value_series": self._portfolio_value_series_vm(
                data.get("portfolio_history", [])
            ),
            "portfolio_pnl_series": self._portfolio_pnl_series_vm(data.get('portfolio_history', [])),
            "portfolio_drawdown": self._portfolio_drawdown_vm(data.get("portfolio_history", [])),
            "pnl_bar_series": self._pnl_bar_series_vm(
                data.get("pnl", [])
            ),
            "position_weight_series": self._position_weight_series_vm(assets),
            "position_distribution": self._position_weight_distribution_vm(assets),
            "winners": self._top_winner_bar_vm(assets),
            "losers": self._top_losers_bar_vm(assets),
            "winners_pnl": self._winners_pnl_vm(assets_history),
            "losers_pnl": self._losers_pnl_vm(assets_history),
            "profitability": self._profitablity_vm(assets),
        }
        
    def _kpi(self, snapshot: dict, assets: list, portfolio_history: list) -> dict:
        daily_change_pct = None
        if len(portfolio_history) >= 2:
            today = portfolio_history[-1]["total_value"]
            yesterday = portfolio_history[-2]["total_value"]
            if yesterday:
                daily_change_pct = (today - yesterday) / yesterday * 100

        portfolio_vol = None
        if assets:
            portfolio_vol = sum(
                (a.get("volatility_30d") or 0) * (a.get("weight_pct") or 0) / 100
                for a in assets
            )

        return {
            "value": snapshot.get('total_value', 0),
            "currency": snapshot.get('currency', "#"),
            "realized_pnl": snapshot.get('investments_realized_pnl', 0),
            "unrealized_pnl": snapshot.get('investments_unrealized_pnl', 0),
            "total_cost": snapshot.get('investments_total_cost', 0),
            "cash": snapshot.get('cash_available_to_trade', 0),
            "daily_change_pct": daily_change_pct,
            "portfolio_vol": portfolio_vol,
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

    def _profitablity_vm(self, assets: list[dict]) -> dict:

        return assets
    # ---------- Line Chart ----------

    def _portfolio_value_series_vm(self, rows: list[dict]) -> dict:
        return {
            "dates":  [r["data_date"] for r in rows],
            "values": [r["total_value"] for r in rows],
            "costs":  [r["investments_total_cost"] for r in rows],
        }
        
    def _portfolio_pnl_series_vm(self, rows: list[dict]) -> dict:
        return {
            "dates":     [r["data_date"] for r in rows],
            "values":    [r["investments_unrealized_pnl"] for r in rows],
            "realized":  [r["investments_realized_pnl"] for r in rows],
            "total_pnl": [r["investments_unrealized_pnl"] + r["investments_realized_pnl"] for r in rows],
        }
        
    def _portfolio_drawdown_vm(self, rows: list[dict]) -> dict:
        dates = [r["data_date"] for r in rows]
        values = [r["total_value"] for r in rows]
        peak = 0
        drawdown = []
        for v in values:
            if v > peak:
                peak = v
            dd = ((v - peak) / peak * 100) if peak > 0 else 0
            drawdown.append(round(dd, 4))
        return {"dates": dates, "drawdown_pct": drawdown}

    # ---------- Position Weight ----------

    def _position_weight_series_vm(self, assets: list[dict]) -> list[dict]:
        items = sorted(
            [{"ticker": a["ticker"], "weight_pct": a["weight_pct"]} for a in assets],
            key=lambda x: x["weight_pct"],
            reverse=True,
        )
        top = items[:8]
        rest_items = items[8:]
        rest = sum(i["weight_pct"] for i in rest_items)
        if rest > 0:
            breakdown = "<br>".join(
                f"{i['ticker']}: {round(i['weight_pct'], 1)}%" for i in rest_items
            )
            top.append({"ticker": "Other", "weight_pct": rest, "breakdown": breakdown})
        for item in top:
            item.setdefault("breakdown", "")
        top.sort(key=lambda x: x["weight_pct"])
        return top

    # ---------- Position Distribution ----------

    def _position_weight_distribution_vm(self, assets: list[dict]) -> list[dict]:
        def _roi_pct(a):
            cost = a.get("cost") or 0
            profit = a.get("profit") or 0
            return round((profit / cost) * 100, 2) if cost else 0

        items = sorted(
            [{"ticker": a["ticker"]
              , "weight_pct": a["weight_pct"]
              , "roi_pct": _roi_pct(a)
              , "profit": a["profit"]
              , "value": a["value"]
              , "name": a["name"]
              } for a in assets],
            key=lambda x: x["weight_pct"],
            reverse=True,
        )

        return items
    
    # ---------- Bar Chart ----------

    def _pnl_bar_series_vm(self, rows: list[dict]) -> dict:
        return {
            "labels": [r["asset"] for r in rows],
            "values": [r["pnl"] for r in rows],
        }
        
        
    def _top_winner_bar_vm(self, assets: list[dict], sort_by: str = "profit") -> dict:

        try:
            def _roi_pct(a):
                cost = a.get("cost") or 0
                profit = a.get("profit") or 0
                return round((profit / cost) * 100, 2) if cost else 0

            def _label(a):
                roi = _roi_pct(a)
                roi_str = ("+" if roi >= 0 else "") + str(roi) + "%"
                return f"{a['ticker']}  €{round(a['profit'], 2)}  {roi_str}"

            items = sorted(
                [{"ticker": a["ticker"]
                , "weight_pct": a["weight_pct"]
                , "profit": a["profit"]
                , "value": a["value"]
                , "name": a["name"]
                , "label": _label(a)
                } for a in assets],
                key=lambda x: x[sort_by],
                reverse=True,
            )

            top = items[:10]
        except Exception as e:
            print(e)
            raise e

        return top

    def _top_losers_bar_vm(self, assets: list[dict], sort_by: str = "profit") -> dict:

        try:
            def _roi_pct(a):
                cost = a.get("cost") or 0
                profit = a.get("profit") or 0
                return round((profit / cost) * 100, 2) if cost else 0

            def _label(a):
                roi = _roi_pct(a)
                roi_str = ("+" if roi >= 0 else "") + str(roi) + "%"
                return f"{a['ticker']}  €{round(a['profit'], 2)}  {roi_str}"

            items = sorted(
                [{"ticker": a["ticker"]
                , "weight_pct": a["weight_pct"]
                , "profit": a["profit"]
                , "value": a["value"]
                , "name": a["name"]
                , "label": _label(a)
                } for a in assets],
                key=lambda x: x[sort_by],
                reverse=False,
            )

            top = items[:10]
        except Exception as e:
            raise e
        return top
    
    def _winners_pnl_vm(self, assets: list[dict]) -> dict:
        try:
            import pandas as pd
            df = pd.DataFrame(assets)
            dict = df[df["is_profitable"] == 1].groupby('created_date')["profit"].sum().to_dict()
            
            return dict
        except Exception as e:
            raise e
    
    def _losers_pnl_vm(self, assets: list[dict]) -> dict:
        try:
            import pandas as pd
            df = pd.DataFrame(assets)
            dict = df[df["is_profitable"] == 0].groupby('created_date')["profit"].sum().to_dict()
            
            return dict
        except Exception as e:
            raise e