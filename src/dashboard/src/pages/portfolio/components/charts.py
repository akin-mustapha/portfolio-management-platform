import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dcc, html


class WinnersPlotlyBarChart:
    def render(self, data):
        df = pd.DataFrame(data)
        df = df.sort_values("profit", ascending=False).head(10)

        fig = px.bar(
            df,
            x="profit",
            y="ticker",
            orientation="h",
            title="Top 10 Winners",
            text="profit",
        )

        fig.update_traces(
            marker=dict(
                color="#33985D",
                line=dict(width=0),
            ),
            texttemplate="%{text:.2f}",
            textposition="outside",
        )

        fig.update_layout(
            template="plotly_white",
            height=350,
            margin=dict(l=20, r=60, t=40, b=20),
            xaxis_title="Profit",
            yaxis_title=None,
            yaxis=dict(autorange="reversed"),
            font=dict(size=12),
            bargap=0.35,
        )

        fig.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
        fig.update_yaxes(showgrid=False)

        return fig


class LosersPlotlyBarChart:
    def render(self, data):
        df = pd.DataFrame(data)
        df = df.sort_values("profit", ascending=True).head(10)

        fig = px.bar(
            df,
            x="profit",
            y="ticker",
            orientation="h",
            title="Top 10 Losers",
            text="profit",
        )

        fig.update_traces(
            marker=dict(
                color="#A73528",
                line=dict(width=0),
            ),
            texttemplate="%{text:.2f}",
            textposition="outside",
        )

        fig.update_layout(
            template="plotly_white",
            height=350,
            margin=dict(l=20, r=60, t=40, b=20),
            xaxis_title="Profit",
            yaxis_title=None,
            yaxis=dict(autorange="reversed"),
            font=dict(size=12),
            bargap=0.35,
        )

        fig.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
        fig.update_yaxes(showgrid=False)

        return fig


class PortfolioPerformancePlotlyLineChart:
    def render(self, data):
        df = pd.DataFrame(data)
        df = df.sort_values("dates")
        

        fig = px.line(
            df,
            x="dates",
            y="values",
        )

        fig.update_traces(
            line=dict(
                width=1.5,
                color="#2483cc",
            ),
            mode="lines",
        )

        fig.update_layout(
            template="plotly_white",
            height=550,
            hovermode="x unified",
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title=None,
            yaxis_title="Portfolio Value",
            title=None,
            font=dict(size=12),
        )

        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")

        return fig
    
    
class PortfolioPNLPlotlyLineChart:
    def render(self, data):
        df = pd.DataFrame(data)
        df = df.sort_values("dates")
        

        fig = px.line(
            df,
            x="dates",
            y="values",
        )

        fig.update_traces(
            line=dict(
                width=1.5,
                color="#2483cc",
            ),
            mode="lines",
        )

        fig.update_layout(
            template="plotly_white",
            height=550,
            hovermode="x unified",
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title=None,
            yaxis_title="Portfolio Unrealized PnL",
            title=None,
            font=dict(size=12),
        )

        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")

        return fig
    
    
# Duplicate logic. Needed
# Might want to move graphs - Open/Close Principle
def performance_chart(data=None):
    if data is None:
        return html.P("NO DATA")
    return dbc.Row([
        dbc.Col(dcc.Graph(id="winners_chart", figure=WinnersPlotlyBarChart().render(data)), md=6),
        dbc.Col(dcc.Graph(id="losers_chart", figure=LosersPlotlyBarChart().render(data)), md=6)
    ],  id="portfolio_page_charts")

def value_chart(data=None):
    if data is None:
        return html.P("NO DATA")
    return dcc.Graph(id="value_chart", figure=PortfolioPerformancePlotlyLineChart().render(data))


def pnl_chart(data=None):
    if data is None:
        return html.P("NO DATA")
    return dcc.Graph(id="pnl_char", figure=PortfolioPNLPlotlyLineChart().render(data))