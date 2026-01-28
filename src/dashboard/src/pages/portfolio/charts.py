import pandas as pd
import plotly.express as px

class WinnersPlotlyBarChart:
    def render(self, data):
        df = pd.DataFrame(data)
        df = df.sort_values("profit", ascending=False).head(5)

        fig = px.bar(
            df,
            x="name",
            y="profit",
            title="Top 5 Winners",
            text="profit",
        )

        fig.update_traces(
            marker=dict(
                color="#2ecc71",
                line=dict(width=0),
            ),
            texttemplate="%{text:.2f}",
            textposition="outside",
        )

        fig.update_layout(
            template="plotly_white",
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_title=None,
            yaxis_title="Profit",
            font=dict(size=12),
        )

        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")

        return fig

class LosersPlotlyBarChart:
    def render(self, data):
        df = pd.DataFrame(data)
        df = df.sort_values("profit", ascending=True).head(5)

        fig = px.bar(
            df,
            x="name",
            y="profit",
            title="Top 5 Losers",
            text="profit",
        )

        fig.update_traces(
            marker=dict(
                color="#e74c3c",
                line=dict(width=0),
            ),
            texttemplate="%{text:.2f}",
            textposition="outside",
        )

        fig.update_layout(
            template="plotly_white",
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_title=None,
            yaxis_title="Profit",
            font=dict(size=12),
        )

        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")

        return fig

class PortfolioPerformancePlotlyLineChart:
    def render(self, data):
        df = pd.DataFrame(data)
        df = df.sort_values("data_date")

        fig = px.line(
            df,
            x="data_date",
            y="portfolio_value",
        )

        fig.update_traces(
            line=dict(
                width=3,
                color="#34495e",
            ),
            mode="lines",
        )

        fig.update_layout(
            template="plotly_white",
            height=350,
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