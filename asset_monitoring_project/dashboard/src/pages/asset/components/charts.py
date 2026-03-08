import pandas as pd
import plotly.express as px

# ─────────────────────────────────────────────
# Figures
# ─────────────────────────────────────────────
class PriceStructurePlotlyLineChart:
    def render(self, data):
        asset_data: dict = data.get("asset_price")
        
        df = pd.DataFrame(
            data={
                "dates": asset_data.get("dates", []),
                "values": asset_data.get("values", [])
            })
        
        df = df.sort_values("dates")
        
        fig = px.line(
            df,
            x="dates",
            y="values",
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
        asset_data: dict = data.get("asset_value")
        
        df = pd.DataFrame(
            data={
                "dates": asset_data.get("dates", []),
                "values": asset_data.get("values", [])
            })
        
        df = df.sort_values("dates")

        fig = px.line(
            df,
            x="dates",
            y="values",
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
        asset_data: dict = data.get("asset_risk")
        
        df = pd.DataFrame(
            data={
                "dates": asset_data.get("dates", []),
                "values": asset_data.get("values", [])
            })
        
        df = df.sort_values("dates")
        fig = px.line(
            df,
            x="dates",
            y="values",
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
        asset_data: dict = data.get("asset_dca_bias")
        
        df = pd.DataFrame(
            data={
                "dates": asset_data.get("dates", []),
                "values": asset_data.get("values", [])
            })
        
        df = df.sort_values("dates")

        fig = px.line(
            df,
            x="dates",
            y="values",
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