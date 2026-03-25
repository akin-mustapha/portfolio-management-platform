"""Asset-level Plotly chart implementations."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .chart_theme import FALLBACK_ACCENT, MUTED_FILL

CHART_THEMES = {
    "light": {
        "paper_bgcolor": "white",
        "plot_bgcolor": "white",
        "font_color": "#555555",
    },
    "dark": {
        "paper_bgcolor": "#1e222d",
        "plot_bgcolor": "#1e222d",
        "font_color": "#9598a1",
    },
}

CHART_HEIGHT = 200


def _hex_to_rgba(hex_color, alpha=1.0):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _apply_spike_config(fig):
    fig.update_xaxes(
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikedash="solid",
        spikecolor="rgba(0,0,0,0.2)",
        spikethickness=1,
    )
    fig.update_yaxes(
        showspikes=True,
        spikesnap="cursor",
        spikedash="solid",
        spikecolor="rgba(0,0,0,0.2)",
        spikethickness=1,
    )


def _base_layout(t):
    return dict(
        template="plotly_white",
        colorway=px.colors.sequential.Bluyl_r,
        height=CHART_HEIGHT,
        hovermode="x unified",
        margin=dict(l=2, r=2, t=2, b=2),
        xaxis_title=None,
        yaxis_title=None,
        font=dict(size=11, color=t["font_color"]),
        paper_bgcolor=t["paper_bgcolor"],
        plot_bgcolor=t["plot_bgcolor"],
        yaxis=dict(side="right", tickformat=",.2f", showgrid=False, zeroline=False),
        xaxis=dict(showgrid=False, type="date", zeroline=False),
    )


# ─────────────────────────────────────────────
# Figures
# ─────────────────────────────────────────────


class PriceStructurePlotlyLineChart:
    def render(self, data, theme="light", accent_color=None):
        asset_data = data.get("asset_price")
        df = pd.DataFrame(
            {
                "dates": asset_data.get("dates", []),
                "values": asset_data.get("values", []),
            }
        ).sort_values("dates")

        ref_value = df["values"].iloc[0]
        t = CHART_THEMES.get(theme or "light", CHART_THEMES["light"])

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=[ref_value] * len(df),
                mode="lines",
                line=dict(color="rgba(0,0,0,0)", width=0),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        line_kw = (
            dict(width=1.5, color=accent_color) if accent_color else dict(width=1.5)
        )
        fill_kw = (
            dict(fillcolor=_hex_to_rgba(accent_color, 0.12)) if accent_color else {}
        )
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=df["values"],
                mode="lines",
                line=line_kw,
                fill="tonexty",
                hovertemplate="%{y:,.2f}<extra></extra>",
                showlegend=False,
                **fill_kw,
            )
        )
        fig.add_hline(
            y=ref_value, line_dash="dot", line_color="rgba(0,0,0,0.25)", line_width=1
        )
        fig.update_layout(**_base_layout(t))
        _apply_spike_config(fig)
        return fig


class PriceWithMAPlotlyLineChart:
    MA30_COLOR = "#7b8fa1"
    MA50_COLOR = "#b0a090"

    def render(self, data, theme="light", accent_color=None):
        asset_data = data.get("asset_price", {})
        df = pd.DataFrame(
            {
                "dates": asset_data.get("dates", []),
                "values": asset_data.get("values", []),
                "value_ma_30d": asset_data.get("value_ma_30d", []),
                "value_ma_50d": asset_data.get("value_ma_50d", []),
            }
        ).sort_values("dates")

        if df.empty:
            return go.Figure()

        t = CHART_THEMES.get(theme or "light", CHART_THEMES["light"])
        ref = df["values"].iloc[0]

        fig = go.Figure()

        # invisible reference trace for area fill anchor
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=[ref] * len(df),
                mode="lines",
                line=dict(color="rgba(0,0,0,0)", width=0),
                showlegend=False,
                hoverinfo="skip",
            )
        )

        # price area
        line_kw = (
            dict(width=1.5, color=accent_color) if accent_color else dict(width=1.5)
        )
        fill_kw = (
            dict(fillcolor=_hex_to_rgba(accent_color, 0.10)) if accent_color else {}
        )
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=df["values"],
                mode="lines",
                name="Price",
                line=line_kw,
                fill="tonexty",
                hovertemplate="%{y:,.2f}<extra></extra>",
                **fill_kw,
            )
        )

        # MA30
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=df["value_ma_30d"],
                mode="lines",
                name="MA 30",
                line=dict(width=1, color=self.MA30_COLOR, dash="dot"),
                hovertemplate="MA30: %{y:,.2f}<extra></extra>",
            )
        )

        # MA50
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=df["value_ma_50d"],
                mode="lines",
                name="MA 50",
                line=dict(width=1, color=self.MA50_COLOR, dash="dot"),
                hovertemplate="MA50: %{y:,.2f}<extra></extra>",
            )
        )

        layout = _base_layout(t)
        layout["showlegend"] = True
        layout["legend"] = dict(
            orientation="h",
            yanchor="bottom",
            y=1.0,
            xanchor="right",
            x=1,
            font=dict(size=10),
        )
        fig.update_layout(**layout)
        _apply_spike_config(fig)
        return fig


class AssetValuePlotlyLineChart:
    def render(self, data, theme="light", accent_color=None):
        asset_data = data.get("asset_value")
        df = pd.DataFrame(
            {
                "dates": asset_data.get("dates", []),
                "values": asset_data.get("values", []),
            }
        ).sort_values("dates")

        ref_value = df["values"].iloc[0]
        t = CHART_THEMES.get(theme or "light", CHART_THEMES["light"])

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=[ref_value] * len(df),
                mode="lines",
                line=dict(color="rgba(0,0,0,0)", width=0),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        line_kw = (
            dict(width=1.5, color=accent_color) if accent_color else dict(width=1.5)
        )
        fill_kw = (
            dict(fillcolor=_hex_to_rgba(accent_color, 0.12)) if accent_color else {}
        )
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=df["values"],
                mode="lines",
                line=line_kw,
                fill="tonexty",
                hovertemplate="%{y:,.2f}<extra></extra>",
                showlegend=False,
                **fill_kw,
            )
        )
        fig.add_hline(
            y=ref_value, line_dash="dot", line_color="rgba(0,0,0,0.25)", line_width=1
        )
        fig.update_layout(**_base_layout(t))
        _apply_spike_config(fig)
        return fig


class RiskContextPlotlyLineChart:
    def render(self, data, theme="light", accent_color=None):
        asset_data = data.get("asset_risk")
        df = pd.DataFrame(
            {
                "dates": asset_data.get("dates", []),
                "values": asset_data.get("values", []),
            }
        ).sort_values("dates")

        t = CHART_THEMES.get(theme or "light", CHART_THEMES["light"])

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=[0] * len(df),
                mode="lines",
                line=dict(color="rgba(0,0,0,0)", width=0),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        line_kw = (
            dict(width=1.5, color=accent_color) if accent_color else dict(width=1.5)
        )
        fill_kw = (
            dict(fillcolor=_hex_to_rgba(accent_color, 0.12)) if accent_color else {}
        )
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=df["values"],
                mode="lines",
                line=line_kw,
                fill="tonexty",
                hovertemplate="%{y:,.2f}<extra></extra>",
                showlegend=False,
                **fill_kw,
            )
        )
        fig.add_hline(y=0, line_dash="dot", line_color="rgba(0,0,0,0.25)", line_width=1)
        fig.update_layout(**_base_layout(t))
        _apply_spike_config(fig)
        return fig


class DCABiasPlotlyLineChart:
    def render(self, data, theme="light", accent_color=None):
        asset_data = data.get("asset_dca_bias")
        df = pd.DataFrame(
            {
                "dates": asset_data.get("dates", []),
                "values": asset_data.get("values", []),
            }
        ).sort_values("dates")

        t = CHART_THEMES.get(theme or "light", CHART_THEMES["light"])

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=[0] * len(df),
                mode="lines",
                line=dict(color="rgba(0,0,0,0)", width=0),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        line_kw = (
            dict(width=1.5, color=accent_color) if accent_color else dict(width=1.5)
        )
        fill_kw = (
            dict(fillcolor=_hex_to_rgba(accent_color, 0.12)) if accent_color else {}
        )
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=df["values"],
                mode="lines",
                line=line_kw,
                fill="tonexty",
                hovertemplate="%{y:,.2f}<extra></extra>",
                showlegend=False,
                **fill_kw,
            )
        )
        fig.add_hline(y=0, line_dash="dot", line_color="rgba(0,0,0,0.25)", line_width=1)
        fig.update_layout(**_base_layout(t))
        _apply_spike_config(fig)
        return fig


class FXReturnAttributionDonutChart:
    def render(self, data, theme="light", accent_color=None):
        attribution = data.get("asset_fx_attribution", {})
        fx_impact = attribution.get("fx_impact") or 0
        profit = attribution.get("profit") or 0
        price_return = profit - fx_impact

        t = CHART_THEMES.get(theme or "light", CHART_THEMES["light"])

        abs_fx = abs(fx_impact)
        abs_price = abs(price_return)
        total = abs_fx + abs_price

        if total == 0:
            fig = go.Figure()
            fig.update_layout(
                paper_bgcolor=t["paper_bgcolor"],
                plot_bgcolor=t["plot_bgcolor"],
                font=dict(size=11, color=t["font_color"]),
                height=CHART_HEIGHT,
                margin=dict(l=2, r=2, t=2, b=2),
                annotations=[
                    dict(text="No FX data", x=0.5, y=0.5, showarrow=False, font_size=12)
                ],
            )
            return fig

        fx_sign = "+" if fx_impact >= 0 else ""
        colors = [
            accent_color or FALLBACK_ACCENT,
            _hex_to_rgba(accent_color, 0.35) if accent_color else MUTED_FILL,
        ]

        fig = go.Figure(
            go.Pie(
                labels=["FX Return", "Price Return"],
                values=[abs_fx, abs_price],
                customdata=[[fx_impact, price_return]],
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Amount: %{customdata[0]:+,.2f}<br>"
                    "Share: %{percent}<extra></extra>"
                ),
                hole=0.6,
                marker=dict(colors=colors, line=dict(width=0)),
                textinfo="none",
                showlegend=True,
            )
        )
        fig.update_layout(
            paper_bgcolor=t["paper_bgcolor"],
            plot_bgcolor=t["plot_bgcolor"],
            font=dict(size=11, color=t["font_color"]),
            height=CHART_HEIGHT,
            margin=dict(l=2, r=2, t=2, b=40),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5,
                font=dict(size=10),
            ),
            annotations=[
                dict(
                    text=f"{fx_sign}{fx_impact:,.2f}<br><span style='font-size:9px'>FX</span>",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=11, color=t["font_color"]),
                )
            ],
        )
        return fig


class ProfitRangePlotlyLineChart:
    def render(self, data, theme="light", accent_color=None):
        asset_data = data.get("asset_profit_range")
        if not asset_data or not asset_data.get("dates"):
            return go.Figure()

        df = pd.DataFrame(asset_data).sort_values("dates")
        t = CHART_THEMES.get(theme or "light", CHART_THEMES["light"])
        band_color = (
            _hex_to_rgba(accent_color, 0.08)
            if accent_color
            else _hex_to_rgba(FALLBACK_ACCENT, 0.08)
        )
        band_edge = (
            _hex_to_rgba(accent_color, 0.25)
            if accent_color
            else _hex_to_rgba(FALLBACK_ACCENT, 0.25)
        )

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=df["low_30d"],
                mode="lines",
                line=dict(color="rgba(0,0,0,0)", width=0),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=df["high_30d"],
                mode="lines",
                line=dict(color=band_edge, width=0),
                fill="tonexty",
                fillcolor=band_color,
                showlegend=False,
                hoverinfo="skip",
            )
        )
        line_kw = (
            dict(width=1.5, color=accent_color) if accent_color else dict(width=1.5)
        )
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=df["values"],
                mode="lines",
                line=line_kw,
                hovertemplate="%{y:,.2f}<extra></extra>",
                showlegend=False,
            )
        )
        fig.add_hline(y=0, line_dash="dot", line_color="rgba(0,0,0,0.25)", line_width=1)
        fig.update_layout(**_base_layout(t))
        _apply_spike_config(fig)
        return fig


class AssetVsPortfolioReturnChart:
    @staticmethod
    def _index_to_100(vals):
        """Shift a return % series so the first value = 100."""
        clean = [v for v in vals if v is not None]
        if not clean:
            return [None] * len(vals)
        base = clean[0]
        return [100 + (v - base) if v is not None else None for v in vals]

    def render(self, data, theme="light", accent_color=None):
        t = CHART_THEMES.get(theme, CHART_THEMES["light"])
        accent = accent_color or FALLBACK_ACCENT

        asset_series = data.get("asset_return", {})
        portfolio_series = data.get("portfolio_return", {})

        asset_dates = asset_series.get("dates", [])
        asset_vals = self._index_to_100(asset_series.get("values", []))
        port_dates = portfolio_series.get("dates", [])
        port_vals = self._index_to_100(portfolio_series.get("values", []))

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=asset_dates,
                y=asset_vals,
                name="Asset",
                mode="lines",
                line=dict(color=accent, width=1.5),
                fill="tonexty",
                fillcolor=_hex_to_rgba(accent, 0.06),
                hovertemplate="<b>%{y:.2f}</b><extra>Asset</extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=port_dates,
                y=port_vals,
                name="Portfolio",
                mode="lines",
                line=dict(color=MUTED_FILL, width=1.2, dash="dot"),
                hovertemplate="<b>%{y:.2f}</b><extra>Portfolio</extra>",
            )
        )
        fig.add_hline(y=100, line_dash="dot", line_color="rgba(0,0,0,0.15)", line_width=1)
        layout = _base_layout(t)
        layout["yaxis"]["tickformat"] = ".1f"
        layout["yaxis"].pop("ticksuffix", None)
        layout["showlegend"] = True
        layout["legend"] = dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10),
        )
        fig.update_layout(**layout)
        _apply_spike_config(fig)
        return fig
