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
            "kpi": self._kpi(snapshot),
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
            "var_by_position": self._var_bar_vm(assets),
            "daily_movers":    self._daily_movers_vm(assets),
        }
        
    def _kpi(self, snapshot: dict) -> dict:
        return {
            "value": snapshot.get('total_value', 0),
            "currency": snapshot.get('currency', "#"),
            "realized_pnl": snapshot.get('investments_realized_pnl', 0),
            "unrealized_pnl": snapshot.get('investments_unrealized_pnl', 0),
            "total_cost": snapshot.get('investments_total_cost', 0),
            "cash": snapshot.get('cash_available_to_trade', 0),
            "cash_reserved": snapshot.get("cash_reserved_for_orders", 0),
            "cash_in_pies":  snapshot.get("cash_in_pies", 0),
            "daily_change_pct": snapshot.get('daily_change_pct'),
            "portfolio_vol": snapshot.get('portfolio_volatility_weighted'),
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

    def _var_bar_vm(self, assets):
        items = [{"ticker": a["ticker"], "var_95_1d": a.get("var_95_1d"), "label": a["ticker"]}
                 for a in assets if a.get("var_95_1d") is not None]
        return sorted(items, key=lambda x: x["var_95_1d"], reverse=True)[:10]

    def _daily_movers_vm(self, assets):
        items = [{"ticker": a["ticker"], "daily_return": a.get("daily_return"), "label": a["ticker"]}
                 for a in assets if a.get("daily_return") is not None]
        return sorted(items, key=lambda x: abs(x["daily_return"]), reverse=True)[:15]
    # ---------- Line Chart ----------

    def _portfolio_value_series_vm(self, rows: list[dict]) -> dict:
        return {
            "dates":  [r["data_date"] for r in rows],
            "values": [r["investments_total_cost"] + r["investments_unrealized_pnl"] for r in rows],
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
        top = items[:14]
        rest_items = items[14:]
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
        items = sorted(
            [{"ticker": a["ticker"]
              , "weight_pct": a["weight_pct"]
              , "roi_pct": round(a.get("pnl_pct") or 0, 2)
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
            def _label(a):
                roi = round(a.get("pnl_pct") or 0, 2)
                roi_str = ("+" if roi >= 0 else "") + str(roi) + "%"
                return f"{a['ticker']} {roi_str}"

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
            def _label(a):
                roi = round(a.get("pnl_pct") or 0, 2)
                roi_str = ("+" if roi >= 0 else "") + str(roi) + "%"
                return f"{a['ticker']} {roi_str}"

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
            return df[df["is_profitable"] == 1].groupby('data_date')["profit"].sum().to_dict()
        except Exception as e:
            raise e

    def _losers_pnl_vm(self, assets: list[dict]) -> dict:
        try:
            import pandas as pd
            df = pd.DataFrame(assets)
            return df[df["is_profitable"] == 0].groupby('data_date')["profit"].sum().to_dict()
        except Exception as e:
            raise e