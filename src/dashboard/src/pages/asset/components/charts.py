import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# Figures
# ─────────────────────────────────────────────
class PriceStructurePlotlyLineChart:
    def render(self, data):
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
        fig.update_layout(
            template="plotly_white", height=350,
            title="Price & Moving Averages",
            hovermode="x unified",
            margin=dict(l=20, r=60, t=40, b=65),
            xaxis_title=None, yaxis_title=None,
            font=dict(size=11, color="#555"),
            paper_bgcolor="white", plot_bgcolor="white",
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
                    bgcolor="white", activecolor="#f0f0f0",
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
    def render(self, data):
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
        fig.update_layout(
            template="plotly_white", height=350,
            title="Asset Value Over Time",
            hovermode="x unified",
            margin=dict(l=20, r=60, t=40, b=65),
            xaxis_title=None, yaxis_title=None,
            font=dict(size=11, color="#555"),
            paper_bgcolor="white", plot_bgcolor="white",
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
                    bgcolor="white", activecolor="#f0f0f0",
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
    def render(self, data):
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
        fig.update_layout(
            template="plotly_white", height=350,
            title="Risk Context (Volatility & Drawdown)",
            hovermode="x unified",
            margin=dict(l=20, r=60, t=40, b=65),
            xaxis_title=None, yaxis_title=None,
            font=dict(size=11, color="#555"),
            paper_bgcolor="white", plot_bgcolor="white",
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
                    bgcolor="white", activecolor="#f0f0f0",
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
    def render(self, data):
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
        fig.update_layout(
            template="plotly_white", height=350,
            title="Dollar Cost Averaging Bias",
            hovermode="x unified",
            margin=dict(l=20, r=60, t=40, b=65),
            xaxis_title=None, yaxis_title=None,
            font=dict(size=11, color="#555"),
            paper_bgcolor="white", plot_bgcolor="white",
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
                    bgcolor="white", activecolor="#f0f0f0",
                    borderwidth=0, font=dict(size=11), y=-0.25, x=0,
                ),
            ),
        )
        fig.update_xaxes(showspikes=True, spikemode="across", spikesnap="cursor",
                         spikedash="solid", spikecolor="rgba(0,0,0,0.2)", spikethickness=1)
        fig.update_yaxes(showspikes=True, spikesnap="cursor",
                         spikedash="solid", spikecolor="rgba(0,0,0,0.2)", spikethickness=1)
        return fig
        

# ─────────────────────────────────────────────
# Depreciated
# ─────────────────────────────────────────────
class PriceOverTimePlotlyLineChart:
    def render (self, data):
      df = pd.DataFrame(data)
      df = df.sort_values("dates")

      fig = px.line(df, x="dates", y=["price", "value"], title="price over time")
      fig.update_layout(template="plotly_white", height=350)
      fig.update_traces(connectgaps=False, line=dict(color="#1f77b4", width=2))
      return fig
    
class VolatilityOverTimePlotlyLineChart:
    def render (self, data):
      df = pd.DataFrame(data)
      df = df.sort_values("dates")

      fig = px.line(df, x="dates", y="volatility_30d", title="volatility_30d over time")
      fig.update_layout(template="plotly_white", height=350)
      fig.update_traces(connectgaps=False, line=dict(color="#1f77b4", width=2))
      return fig
    
    
class ProfitOverTimePlotlyLineChart:
    def render (self, data):
      df = pd.DataFrame(data)
      df = df.sort_values("dates")

      fig = px.line(df, x="dates", y="profit", title="Profit over time")
      fig.update_layout(template="plotly_white", height=350)
      fig.update_traces(connectgaps=False, line=dict(color="#1f77b4", width=2))
      return fig

class MovingAveragePriceOverTimePlotlyLineChart:
    def render (self, data):
      df = pd.DataFrame(data)
      df = df.sort_values("dates")

      fig = px.line(df, x="dates", y=["ma_30d", "ma_50d"], title="Moving Averages")
      fig.update_layout(template="plotly_white", height=350)
      fig.update_traces(connectgaps=False, line=dict(color="#1f77b4", width=2))
      return fig

class RecentHeighDrawdownOverTimePlotlyLineChart:
    def render (self, data):
      df = pd.DataFrame(data)
      df = df.sort_values("dates")

      fig = px.line(df, x="dates", y="pct_drawdown", title="Drawdown vs Recent High")
      fig.update_layout(template="plotly_white", height=350)
      fig.update_traces(connectgaps=False, line=dict(color="#1f77b4", width=2))
      return fig


class DollarCostAVGBiasOverTimePlotlyLineChart:
    def render (self, data):
      df = pd.DataFrame(data)
      df = df.sort_values("dates")

      fig = px.line(df, x="dates", y="dca_bias", title="DCA Bias over Time")
      fig.update_layout(template="plotly_white", height=350)
      fig.update_traces(connectgaps=False, line=dict(color="#1f77b4", width=2))
      return fig