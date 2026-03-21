import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

CHART_THEMES = {
    "light": {"paper_bgcolor": "white",   "plot_bgcolor": "white",   "font_color": "#555555"},
    "dark":  {"paper_bgcolor": "#1e222d", "plot_bgcolor": "#1e222d", "font_color": "#9598a1"},
}

CHART_HEIGHT = 200


def _hex_to_rgba(hex_color, alpha=1.0):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _apply_spike_config(fig):
    fig.update_xaxes(
        showspikes=True, spikemode="across", spikesnap="cursor",
        spikedash="solid", spikecolor="rgba(0,0,0,0.2)", spikethickness=1,
    )
    fig.update_yaxes(
        showspikes=True, spikesnap="cursor",
        spikedash="solid", spikecolor="rgba(0,0,0,0.2)", spikethickness=1,
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
        df = pd.DataFrame({
            "dates": asset_data.get("dates", []),
            "values": asset_data.get("values", []),
        }).sort_values("dates")

        ref_value = df["values"].iloc[0]
        t = CHART_THEMES.get(theme or "light", CHART_THEMES["light"])

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["dates"], y=[ref_value] * len(df),
            mode="lines", line=dict(color="rgba(0,0,0,0)", width=0),
            showlegend=False, hoverinfo="skip",
        ))
        line_kw = dict(width=1.5, color=accent_color) if accent_color else dict(width=1.5)
        fill_kw = dict(fillcolor=_hex_to_rgba(accent_color, 0.12)) if accent_color else {}
        fig.add_trace(go.Scatter(
            x=df["dates"], y=df["values"],
            mode="lines",
            line=line_kw,
            fill="tonexty",
            hovertemplate="%{y:,.2f}<extra></extra>",
            showlegend=False,
            **fill_kw,
        ))
        fig.add_hline(y=ref_value, line_dash="dot", line_color="rgba(0,0,0,0.25)", line_width=1)
        fig.update_layout(**_base_layout(t))
        _apply_spike_config(fig)
        return fig


class AssetValuePlotlyLineChart:
    def render(self, data, theme="light", accent_color=None):
        asset_data = data.get("asset_value")
        df = pd.DataFrame({
            "dates": asset_data.get("dates", []),
            "values": asset_data.get("values", []),
        }).sort_values("dates")

        ref_value = df["values"].iloc[0]
        t = CHART_THEMES.get(theme or "light", CHART_THEMES["light"])

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["dates"], y=[ref_value] * len(df),
            mode="lines", line=dict(color="rgba(0,0,0,0)", width=0),
            showlegend=False, hoverinfo="skip",
        ))
        line_kw = dict(width=1.5, color=accent_color) if accent_color else dict(width=1.5)
        fill_kw = dict(fillcolor=_hex_to_rgba(accent_color, 0.12)) if accent_color else {}
        fig.add_trace(go.Scatter(
            x=df["dates"], y=df["values"],
            mode="lines",
            line=line_kw,
            fill="tonexty",
            hovertemplate="%{y:,.2f}<extra></extra>",
            showlegend=False,
            **fill_kw,
        ))
        fig.add_hline(y=ref_value, line_dash="dot", line_color="rgba(0,0,0,0.25)", line_width=1)
        fig.update_layout(**_base_layout(t))
        _apply_spike_config(fig)
        return fig


class RiskContextPlotlyLineChart:
    def render(self, data, theme="light", accent_color=None):
        asset_data = data.get("asset_risk")
        df = pd.DataFrame({
            "dates": asset_data.get("dates", []),
            "values": asset_data.get("values", []),
        }).sort_values("dates")

        t = CHART_THEMES.get(theme or "light", CHART_THEMES["light"])

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["dates"], y=[0] * len(df),
            mode="lines", line=dict(color="rgba(0,0,0,0)", width=0),
            showlegend=False, hoverinfo="skip",
        ))
        line_kw = dict(width=1.5, color=accent_color) if accent_color else dict(width=1.5)
        fill_kw = dict(fillcolor=_hex_to_rgba(accent_color, 0.12)) if accent_color else {}
        fig.add_trace(go.Scatter(
            x=df["dates"], y=df["values"],
            mode="lines",
            line=line_kw,
            fill="tonexty",
            hovertemplate="%{y:,.2f}<extra></extra>",
            showlegend=False,
            **fill_kw,
        ))
        fig.add_hline(y=0, line_dash="dot", line_color="rgba(0,0,0,0.25)", line_width=1)
        fig.update_layout(**_base_layout(t))
        _apply_spike_config(fig)
        return fig


class DCABiasPlotlyLineChart:
    def render(self, data, theme="light", accent_color=None):
        asset_data = data.get("asset_dca_bias")
        df = pd.DataFrame({
            "dates": asset_data.get("dates", []),
            "values": asset_data.get("values", []),
        }).sort_values("dates")

        t = CHART_THEMES.get(theme or "light", CHART_THEMES["light"])

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["dates"], y=[0] * len(df),
            mode="lines", line=dict(color="rgba(0,0,0,0)", width=0),
            showlegend=False, hoverinfo="skip",
        ))
        line_kw = dict(width=1.5, color=accent_color) if accent_color else dict(width=1.5)
        fill_kw = dict(fillcolor=_hex_to_rgba(accent_color, 0.12)) if accent_color else {}
        fig.add_trace(go.Scatter(
            x=df["dates"], y=df["values"],
            mode="lines",
            line=line_kw,
            fill="tonexty",
            hovertemplate="%{y:,.2f}<extra></extra>",
            showlegend=False,
            **fill_kw,
        ))
        fig.add_hline(y=0, line_dash="dot", line_color="rgba(0,0,0,0.25)", line_width=1)
        fig.update_layout(**_base_layout(t))
        _apply_spike_config(fig)
        return fig


class ProfitRangePlotlyLineChart:
    def render(self, data, theme="light", accent_color=None):
        asset_data = data.get("asset_profit_range")
        if not asset_data or not asset_data.get("dates"):
            return go.Figure()

        df = pd.DataFrame(asset_data).sort_values("dates")
        t = CHART_THEMES.get(theme or "light", CHART_THEMES["light"])
        band_color = _hex_to_rgba(accent_color, 0.08) if accent_color else "rgba(150,150,150,0.1)"
        band_edge  = _hex_to_rgba(accent_color, 0.25) if accent_color else "rgba(150,150,150,0.3)"

        fig = go.Figure()
        # Band lower boundary (invisible fill reference)
        fig.add_trace(go.Scatter(
            x=df["dates"], y=df["low_30d"],
            mode="lines", line=dict(color="rgba(0,0,0,0)", width=0),
            showlegend=False, hoverinfo="skip",
        ))
        # Band upper boundary
        fig.add_trace(go.Scatter(
            x=df["dates"], y=df["high_30d"],
            mode="lines", line=dict(color=band_edge, width=0),
            fill="tonexty", fillcolor=band_color,
            showlegend=False, hoverinfo="skip",
        ))
        # Profit line
        line_kw = dict(width=1.5, color=accent_color) if accent_color else dict(width=1.5)
        fig.add_trace(go.Scatter(
            x=df["dates"], y=df["values"],
            mode="lines",
            line=line_kw,
            hovertemplate="%{y:,.2f}<extra></extra>",
            showlegend=False,
        ))
        fig.add_hline(y=0, line_dash="dot", line_color="rgba(0,0,0,0.25)", line_width=1)
        fig.update_layout(**_base_layout(t))
        _apply_spike_config(fig)
        return fig
