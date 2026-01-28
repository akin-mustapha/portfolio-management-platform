import pandas as pd
import plotly.express as px

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

      fig = px.line(df, x="data_date", y=["ma_30", "ma_50"], title="Moving Averages")
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