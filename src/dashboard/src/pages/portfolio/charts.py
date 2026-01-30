import pandas as pd
import plotly.express as px


class WinnersPlotlyBarChart:
    def render(self, data):
        df = pd.DataFrame(data)
        df = df.sort_values("profit", ascending=False).head(10)

        fig = px.bar(
            df,
            x="name",
            y="profit",
            title="Top 10 Winners",
            text="profit",
        )

        fig.update_traces(
            marker=dict(
                color="#33985D",
                line=dict(width=0),
            ),
            width=0.35,
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
            bargap=0.45,        # 👈 more air between bars
            bargroupgap=0.1,
        )

        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")

        return fig


class LosersPlotlyBarChart:
    def render(self, data):
        df = pd.DataFrame(data)
        df = df.sort_values("profit", ascending=True).head(10)

        fig = px.bar(
            df,
            x="name",
            y="profit",
            title="Top 10 Losers",
            text="profit",
        )

        fig.update_traces(
            marker=dict(
                color="#A73528",
                line=dict(width=0),
            ),
            width=0.35,
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
            bargap=0.45,
            bargroupgap=0.1,
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