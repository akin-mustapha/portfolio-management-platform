import pandas as pd
import plotly.express as px

# ─────────────────────────────────────────────
# Figures
# ─────────────────────────────────────────────
class PriceStructurePlotlyLineChart:
    def render(self, data):
        df = pd.DataFrame(data).sort_values("data_date")
        
        fig = px.line(
            df,
            x="data_date",
            y=["price", "ma_30d", "ma_50d"],
        )

        fig.update_traces(line=dict(width=1))
        fig.update_layout(
            template="plotly_white",
            height=350,
            title="Price & Moving Averages",
            hovermode="x unified",
            margin=dict(l=20, r=20, t=40, b=20),
        )

        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
        return fig
    
class AssetValuePlotlyLineChart:
    def render(self, data):
        df = pd.DataFrame(data).sort_values("data_date")

        fig = px.line(
            df,
            x="data_date",
            y="value",
        )

        fig.update_traces(
            line=dict(width=1, color="#34495e"),
            mode="lines",
        )

        fig.update_layout(
            template="plotly_white",
            height=350,
            title="Asset Value Over Time",
            hovermode="x unified",
            margin=dict(l=20, r=20, t=20, b=20),
        )

        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")

        return fig
    
class RiskContextPlotlyLineChart:
    def render(self, data):
        df = pd.DataFrame(data).sort_values("data_date")
        
        fig = px.line(
            df,
            x="data_date",
            y=["volatility_30d", "pct_drawdown"],
        )

        fig.update_traces(line=dict(width=1))
        fig.update_layout(
            template="plotly_white",
            height=350,
            title="Risk Context (Volatility & Drawdown)",
            hovermode="x unified",
            margin=dict(l=20, r=20, t=40, b=20),
        )

        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")

        return fig
    

class DCABiasPlotlyLineChart:
    def render(self, data):
        df = pd.DataFrame(data).sort_values("data_date")

        fig = px.line(
            df,
            x="data_date",
            y="dca_bias",
        )

        fig.update_traces(
            line=dict(width=1, color="#4F7E5F"),
        )

        fig.update_layout(
            template="plotly_white",
            height=350,
            title="Dollar Cost Averaging Bias",
            hovermode="x unified",
            margin=dict(l=20, r=20, t=40, b=20),
        )

        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
        return fig
        

# ─────────────────────────────────────────────
# Depreciated
# ─────────────────────────────────────────────
class PriceOverTimePlotlyLineChart:
    def render (self, data):
      df = pd.DataFrame(data)
      df = df.sort_values("data_date")

      fig = px.line(df, x="data_date", y=["price", "value"], title="price over time")
      fig.update_layout(template="plotly_white", height=350)
      fig.update_traces(connectgaps=False, line=dict(color="#1f77b4", width=2))
      return fig
    
class VolatilityOverTimePlotlyLineChart:
    def render (self, data):
      df = pd.DataFrame(data)
      df = df.sort_values("data_date")

      fig = px.line(df, x="data_date", y="volatility_30d", title="volatility_30d over time")
      fig.update_layout(template="plotly_white", height=350)
      fig.update_traces(connectgaps=False, line=dict(color="#1f77b4", width=2))
      return fig
    
    
class ProfitOverTimePlotlyLineChart:
    def render (self, data):
      df = pd.DataFrame(data)
      df = df.sort_values("data_date")

      fig = px.line(df, x="data_date", y="profit", title="Profit over time")
      fig.update_layout(template="plotly_white", height=350)
      fig.update_traces(connectgaps=False, line=dict(color="#1f77b4", width=2))
      return fig

class MovingAveragePriceOverTimePlotlyLineChart:
    def render (self, data):
      df = pd.DataFrame(data)
      df = df.sort_values("data_date")

      fig = px.line(df, x="data_date", y=["ma_30d", "ma_50d"], title="Moving Averages")
      fig.update_layout(template="plotly_white", height=350)
      fig.update_traces(connectgaps=False, line=dict(color="#1f77b4", width=2))
      return fig

class RecentHeighDrawdownOverTimePlotlyLineChart:
    def render (self, data):
      df = pd.DataFrame(data)
      df = df.sort_values("data_date")

      fig = px.line(df, x="data_date", y="pct_drawdown", title="Drawdown vs Recent High")
      fig.update_layout(template="plotly_white", height=350)
      fig.update_traces(connectgaps=False, line=dict(color="#1f77b4", width=2))
      return fig


class DollarCostAVGBiasOverTimePlotlyLineChart:
    def render (self, data):
      df = pd.DataFrame(data)
      df = df.sort_values("data_date")

      fig = px.line(df, x="data_date", y="dca_bias", title="DCA Bias over Time")
      fig.update_layout(template="plotly_white", height=350)
      fig.update_traces(connectgaps=False, line=dict(color="#1f77b4", width=2))
      return fig