import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

CHART_THEMES = {
    "light": {"paper_bgcolor": "white",   "plot_bgcolor": "white",   "font_color": "#555555", "rs_bg": "white",   "rs_active": "#f0f0f0"},
    "dark":  {"paper_bgcolor": "#1e222d", "plot_bgcolor": "#1e222d", "font_color": "#9598a1", "rs_bg": "#252d3d", "rs_active": "#1c2a4a"},
}


CHART_HEIGHT = 300
DONUT_CHART_HEIGHT = 300


def _donut_chart(labels, values, colors, theme):
    t = CHART_THEMES.get(theme or "light", CHART_THEMES["light"])
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=colors, line=dict(width=0)),
        textinfo="percent+label",
        textfont=dict(color="#ffffff", size=10),
        hovertemplate="%{label}: %{percent}<extra></extra>",
    ))
    fig.update_layout(
        height=DONUT_CHART_HEIGHT,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor=t["paper_bgcolor"],
        plot_bgcolor=t["plot_bgcolor"],
        font=dict(size=10, color=t["font_color"]),
        showlegend=False,
        legend=dict(font=dict(color=t["font_color"], size=9)),
    )
    return fig


# ─────────────────────────────────────────────
# Figures
# ─────────────────────────────────────────────

class PriceStructurePlotlyLineChart:
    def render(self, data, theme="light"):
        asset_data: dict = data.get("asset_price")

        df = pd.DataFrame({
            "dates": asset_data.get("dates", []),
            "values": asset_data.get("values", [])
        }).sort_values("dates")

        is_positive = df["values"].iloc[-1] >= df["values"].iloc[0]
        line_color = "#1a9e6e" if is_positive else "#e04040"
        fill_color = "rgba(26,158,110,0.08)" if is_positive else "rgba(224,64,64,0.08)"
        ref_value = df["values"].iloc[0]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["dates"], y=[ref_value] * len(df),
            mode="lines", line=dict(color="rgba(0,0,0,0)", width=0),
            showlegend=False, hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=df["dates"], y=df["values"],
            mode="lines",
            line=dict(color=line_color, width=1.5),
            fill="tonexty", fillcolor=fill_color,
            hovertemplate="%{y:,.2f}<extra></extra>",
            showlegend=False,
        ))
        fig.add_hline(y=ref_value, line_dash="dot",
                      line_color="rgba(0,0,0,0.25)", line_width=1)
        t = CHART_THEMES.get(theme or "light", CHART_THEMES["light"])
        fig.update_layout(
            template="plotly_white", height=CHART_HEIGHT,
            # title="Price & Moving Averages",
            hovermode="x unified",
            margin=dict(l=20, r=60, t=40, b=65),
            xaxis_title=None, yaxis_title=None,
            font=dict(size=11, color=t["font_color"]),
            paper_bgcolor=t["paper_bgcolor"], plot_bgcolor=t["plot_bgcolor"],
            yaxis=dict(side="right", tickformat=",.2f", showgrid=False, zeroline=False),
            xaxis=dict(
                showgrid=False, type="date",
                rangeselector=dict(
                    buttons=[
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=3, label="3M", step="month", stepmode="backward"),
                        dict(count=6, label="6M", step="month", stepmode="backward"),
                        dict(count=1, label="1Y", step="year", stepmode="backward"),
                        dict(step="all", label="All"),
                    ],
                    bgcolor=t["rs_bg"], activecolor=t["rs_active"],
                    borderwidth=0, font=dict(size=11), y=-0.25, x=0,
                ),
            ),
        )
        fig.update_xaxes(showspikes=True, spikemode="across", spikesnap="cursor",
                         spikedash="solid", spikecolor="rgba(0,0,0,0.2)", spikethickness=1)
        fig.update_yaxes(showspikes=True, spikesnap="cursor",
                         spikedash="solid", spikecolor="rgba(0,0,0,0.2)", spikethickness=1)
        return fig
    
class AssetValuePlotlyLineChart:
    def render(self, data, theme="light"):
        asset_data: dict = data.get("asset_value")

        df = pd.DataFrame({
            "dates": asset_data.get("dates", []),
            "values": asset_data.get("values", [])
        }).sort_values("dates")

        is_positive = df["values"].iloc[-1] >= df["values"].iloc[0]
        line_color = "#1a9e6e" if is_positive else "#e04040"
        fill_color = "rgba(26,158,110,0.08)" if is_positive else "rgba(224,64,64,0.08)"
        ref_value = df["values"].iloc[0]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["dates"], y=[ref_value] * len(df),
            mode="lines", line=dict(color="rgba(0,0,0,0)", width=0),
            showlegend=False, hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=df["dates"], y=df["values"],
            mode="lines",
            line=dict(color=line_color, width=1.5),
            fill="tonexty", fillcolor=fill_color,
            hovertemplate="%{y:,.2f}<extra></extra>",
            showlegend=False,
        ))
        fig.add_hline(y=ref_value, line_dash="dot",
                      line_color="rgba(0,0,0,0.25)", line_width=1)
        t = CHART_THEMES.get(theme or "light", CHART_THEMES["light"])
        fig.update_layout(
            template="plotly_white", height=CHART_HEIGHT,
            # title="Asset Value Over Time",
            hovermode="x unified",
            margin=dict(l=20, r=60, t=40, b=65),
            xaxis_title=None, yaxis_title=None,
            font=dict(size=11, color=t["font_color"]),
            paper_bgcolor=t["paper_bgcolor"], plot_bgcolor=t["plot_bgcolor"],
            yaxis=dict(side="right", tickformat=",.2f", showgrid=False, zeroline=False),
            xaxis=dict(
                showgrid=False, type="date",
                rangeselector=dict(
                    buttons=[
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=3, label="3M", step="month", stepmode="backward"),
                        dict(count=6, label="6M", step="month", stepmode="backward"),
                        dict(count=1, label="1Y", step="year", stepmode="backward"),
                        dict(step="all", label="All"),
                    ],
                    bgcolor=t["rs_bg"], activecolor=t["rs_active"],
                    borderwidth=0, font=dict(size=11), y=-0.25, x=0,
                ),
            ),
        )
        fig.update_xaxes(showspikes=True, spikemode="across", spikesnap="cursor",
                         spikedash="solid", spikecolor="rgba(0,0,0,0.2)", spikethickness=1)
        fig.update_yaxes(showspikes=True, spikesnap="cursor",
                         spikedash="solid", spikecolor="rgba(0,0,0,0.2)", spikethickness=1)
        return fig
    
class RiskContextPlotlyLineChart:
    def render(self, data, theme="light"):
        asset_data: dict = data.get("asset_risk")

        df = pd.DataFrame({
            "dates": asset_data.get("dates", []),
            "values": asset_data.get("values", [])
        }).sort_values("dates")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["dates"], y=[0] * len(df),
            mode="lines", line=dict(color="rgba(0,0,0,0)", width=0),
            showlegend=False, hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=df["dates"], y=df["values"],
            mode="lines",
            line=dict(color="#5b8db8", width=1.5),
            fill="tonexty", fillcolor="rgba(91,141,184,0.08)",
            hovertemplate="%{y:,.2f}<extra></extra>",
            showlegend=False,
        ))
        fig.add_hline(y=0, line_dash="dot",
                      line_color="rgba(0,0,0,0.25)", line_width=1)
        t = CHART_THEMES.get(theme or "light", CHART_THEMES["light"])
        fig.update_layout(
            template="plotly_white", height=CHART_HEIGHT,
            # title="Risk Context (Volatility & Drawdown)",
            hovermode="x unified",
            margin=dict(l=20, r=60, t=40, b=65),
            xaxis_title=None, yaxis_title=None,
            font=dict(size=11, color=t["font_color"]),
            paper_bgcolor=t["paper_bgcolor"], plot_bgcolor=t["plot_bgcolor"],
            yaxis=dict(side="right", tickformat=",.2f", showgrid=False, zeroline=False),
            xaxis=dict(
                showgrid=False, type="date",
                rangeselector=dict(
                    buttons=[
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=3, label="3M", step="month", stepmode="backward"),
                        dict(count=6, label="6M", step="month", stepmode="backward"),
                        dict(count=1, label="1Y", step="year", stepmode="backward"),
                        dict(step="all", label="All"),
                    ],
                    bgcolor=t["rs_bg"], activecolor=t["rs_active"],
                    borderwidth=0, font=dict(size=11), y=-0.25, x=0,
                ),
            ),
        )
        fig.update_xaxes(showspikes=True, spikemode="across", spikesnap="cursor",
                         spikedash="solid", spikecolor="rgba(0,0,0,0.2)", spikethickness=1)
        fig.update_yaxes(showspikes=True, spikesnap="cursor",
                         spikedash="solid", spikecolor="rgba(0,0,0,0.2)", spikethickness=1)
        return fig
    

class DCABiasPlotlyLineChart:
    def render(self, data, theme="light"):
        asset_data: dict = data.get("asset_dca_bias")

        df = pd.DataFrame({
            "dates": asset_data.get("dates", []),
            "values": asset_data.get("values", [])
        }).sort_values("dates")

        is_positive = df["values"].iloc[-1] >= 0
        line_color = "#1a9e6e" if is_positive else "#e04040"
        fill_color = "rgba(26,158,110,0.08)" if is_positive else "rgba(224,64,64,0.08)"

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["dates"], y=[0] * len(df),
            mode="lines", line=dict(color="rgba(0,0,0,0)", width=0),
            showlegend=False, hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=df["dates"], y=df["values"],
            mode="lines",
            line=dict(color=line_color, width=1.5),
            fill="tonexty", fillcolor=fill_color,
            hovertemplate="%{y:,.2f}<extra></extra>",
            showlegend=False,
        ))
        fig.add_hline(y=0, line_dash="dot",
                      line_color="rgba(0,0,0,0.25)", line_width=1)
        t = CHART_THEMES.get(theme or "light", CHART_THEMES["light"])
        fig.update_layout(
            template="plotly_white", height=CHART_HEIGHT,
            # title="Dollar Cost Averaging Bias",
            hovermode="x unified",
            margin=dict(l=20, r=60, t=40, b=65),
            xaxis_title=None, yaxis_title=None,
            font=dict(size=11, color=t["font_color"]),
            paper_bgcolor=t["paper_bgcolor"], plot_bgcolor=t["plot_bgcolor"],
            yaxis=dict(side="right", tickformat=",.2f", showgrid=False, zeroline=False),
            xaxis=dict(
                showgrid=False, type="date",
                rangeselector=dict(
                    buttons=[
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=3, label="3M", step="month", stepmode="backward"),
                        dict(count=6, label="6M", step="month", stepmode="backward"),
                        dict(count=1, label="1Y", step="year", stepmode="backward"),
                        dict(step="all", label="All"),
                    ],
                    bgcolor=t["rs_bg"], activecolor=t["rs_active"],
                    borderwidth=0, font=dict(size=11), y=-0.25, x=0,
                ),
            ),
        )
        fig.update_xaxes(showspikes=True, spikemode="across", spikesnap="cursor",
                         spikedash="solid", spikecolor="rgba(0,0,0,0.2)", spikethickness=1)
        fig.update_yaxes(showspikes=True, spikesnap="cursor",
                         spikedash="solid", spikecolor="rgba(0,0,0,0.2)", spikethickness=1)
        return fig


class ProfitRangePlotlyLineChart:
    def render(self, data, theme="light"):
        asset_data = data.get("asset_profit_range")
        if not asset_data or not asset_data.get("dates"):
            return go.Figure()

        df = pd.DataFrame(asset_data).sort_values("dates")
        t = CHART_THEMES.get(theme or "light", CHART_THEMES["light"])

        is_positive = (df["values"].iloc[-1] or 0) >= 0
        line_color = "#1a9e6e" if is_positive else "#e04040"

        fig = go.Figure()

        # Band lower boundary (invisible fill reference)
        fig.add_trace(go.Scatter(
            x=df["dates"], y=df["low_30d"],
            mode="lines", line=dict(color="rgba(0,0,0,0)", width=0),
            showlegend=False, hoverinfo="skip",
        ))
        # Band upper boundary (filled to lower)
        fig.add_trace(go.Scatter(
            x=df["dates"], y=df["high_30d"],
            mode="lines", line=dict(color="rgba(150,150,150,0.3)", width=0),
            fill="tonexty", fillcolor="rgba(150,150,150,0.1)",
            showlegend=False, hoverinfo="skip",
        ))
        # Profit line on top
        fig.add_trace(go.Scatter(
            x=df["dates"], y=df["values"],
            mode="lines",
            line=dict(color=line_color, width=1.5),
            hovertemplate="%{y:,.2f}<extra></extra>",
            showlegend=False,
        ))
        fig.add_hline(y=0, line_dash="dot", line_color="rgba(0,0,0,0.25)", line_width=1)

        fig.update_layout(
            template="plotly_white", height=CHART_HEIGHT,
            hovermode="x unified",
            margin=dict(l=20, r=60, t=40, b=65),
            xaxis_title=None, yaxis_title=None,
            font=dict(size=11, color=t["font_color"]),
            paper_bgcolor=t["paper_bgcolor"], plot_bgcolor=t["plot_bgcolor"],
            yaxis=dict(side="right", tickformat=",.2f", showgrid=False, zeroline=False),
            xaxis=dict(
                showgrid=False, type="date",
                rangeselector=dict(
                    buttons=[
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=3, label="3M", step="month", stepmode="backward"),
                        dict(count=6, label="6M", step="month", stepmode="backward"),
                        dict(count=1, label="1Y", step="year", stepmode="backward"),
                        dict(step="all", label="All"),
                    ],
                    bgcolor=t["rs_bg"], activecolor=t["rs_active"],
                    borderwidth=0, font=dict(size=11), y=-0.25, x=0,
                ),
            ),
        )
        fig.update_xaxes(showspikes=True, spikemode="across", spikesnap="cursor",
                         spikedash="solid", spikecolor="rgba(0,0,0,0.2)", spikethickness=1)
        fig.update_yaxes(showspikes=True, spikesnap="cursor",
                         spikedash="solid", spikecolor="rgba(0,0,0,0.2)", spikethickness=1)
        return fig
