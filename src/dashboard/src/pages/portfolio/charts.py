import pandas as pd
import plotly.express as px

class WinnersPlotlyBarChart:
    def render (self, data):
        df = pd.DataFrame(data)
        df = df.sort_values("data_date")

        fig = px.line(df, x="data_date", y="profit", title="Profit over time")
        fig.update_layout(template="plotly_white", height=350)
        fig.update_traces(connectgaps=False, line=dict(color="#1f77b4", width=2))    
        return fig

class LosersPlotlyBarChart:
    def render (self, data):
      df = pd.DataFrame(data)
      df = df.sort_values("data_date")

      fig = px.line(df, x="data_date", y="profit", title="Profit over time")
      fig.update_layout(template="plotly_white", height=350)
      fig.update_traces(connectgaps=False, line=dict(color="#1f77b4", width=2))
      return fig