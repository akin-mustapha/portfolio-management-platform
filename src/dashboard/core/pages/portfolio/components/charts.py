import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import dcc, html


_GRAPH_CONFIG = {"displayModeBar": False}

CHART_HEIGHT = 300

CHART_THEMES = {
    "light": {
        "paper_bgcolor": "white",
        "plot_bgcolor": "white",
        "font_color": "#555555",
        "rs_bg": "white",
        "rs_active": "#f0f0f0",
    },
    "dark": {
        "paper_bgcolor": "#1e222d",
        "plot_bgcolor": "#1e222d",
        "font_color": "#9598a1",
        "rs_bg": "#252d3d",
        "rs_active": "#1c2a4a",
    },
}


class WinnersPlotlyBarChart:
    def render(self, data, theme="light"):
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
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
                color="#1a9e6e",
                line=dict(width=0),
            ),
            texttemplate="%{text:+.2f}",
            textposition="outside",
            textfont=dict(color=ct["font_color"], size=11),
        )

        fig.update_layout(
            template="plotly_white",
            margin=dict(l=60, r=20, t=10, b=20),
            height=CHART_HEIGHT,
            xaxis_title=None,
            yaxis_title=None,
            yaxis=dict(autorange="reversed", side="left", showgrid=False, zeroline=False),
            xaxis=dict(autorange="reversed", showgrid=False, zeroline=False),
            font=dict(size=11, color=ct["font_color"]),
            bargap=0.3,
            paper_bgcolor=ct["paper_bgcolor"],
            plot_bgcolor=ct["plot_bgcolor"],
            title=None,
        )

        return fig


class LosersPlotlyBarChart:
    def render(self, data, theme="light"):
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
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
                color="#ef5350",
                line=dict(width=0),
            ),
            texttemplate="%{text:+.2f}",
            textposition="outside",
            textfont=dict(color=ct["font_color"], size=11),
        )

        fig.update_layout(
            template="plotly_white",
            # height=350,
            height=CHART_HEIGHT,
            margin=dict(l=20, r=60, t=10, b=20),
            xaxis_title=None,
            yaxis_title=None,
            yaxis=dict(autorange="reversed", showgrid=False, zeroline=False),
            xaxis=dict(showgrid=False, zeroline=False),
            font=dict(size=11, color=ct["font_color"]),
            bargap=0.3,
            paper_bgcolor=ct["paper_bgcolor"],
            plot_bgcolor=ct["plot_bgcolor"],
            title=None,
        )

        return fig


class PositionWeightPlotlyBarChart:
    def render(self, data, theme="light"):
        if not data:
            return go.Figure()
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
        df = pd.DataFrame(data)
        df = df.sort_values("weight_pct", ascending=True)

        fig = px.bar(
            df,
            x="weight_pct",
            y="ticker",
            orientation="h",
            text="weight_pct",
        )

        fig.update_traces(
            marker=dict(
                color="#5b7fcf",
                line=dict(width=0),
            ),
            texttemplate="%{text:.1f}%",
            textposition="outside",
            textfont=dict(color=ct["font_color"], size=11),
        )

        fig.add_vline(
            x=5,
            line_dash="dot",
            line_color="rgba(200,80,80,0.5)",
            line_width=1.5,
            annotation_text="5%",
            annotation_font_size=10,
            annotation_font_color="rgba(200,80,80,0.7)",
        )

        fig.update_layout(
            template="plotly_white",
            margin=dict(l=80, r=60, t=10, b=20),
            height=450,
            xaxis_title=None,
            yaxis_title=None,
            yaxis=dict(showgrid=False, zeroline=False),
            xaxis=dict(showgrid=False, zeroline=False),
            font=dict(size=11, color=ct["font_color"]),
            bargap=0.3,
            paper_bgcolor=ct["paper_bgcolor"],
            plot_bgcolor=ct["plot_bgcolor"],
            title=None,
        )

        return fig


class PortfolioPerformancePlotlyLineChart:
    def render(self, data, theme="light"):
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
        df = pd.DataFrame(data).sort_values("dates")

        is_positive = df["values"].iloc[-1] >= df["values"].iloc[0]
        line_color = "#1a9e6e" if is_positive else "#e04040"
        fill_color = "rgba(26,158,110,0.08)" if is_positive else "rgba(224,64,64,0.08)"
        ref_value = df["values"].iloc[0]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["dates"],
            y=[ref_value] * len(df),
            mode="lines",
            line=dict(color="rgba(0,0,0,0)", width=0),
            showlegend=False,
            hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=df["dates"],
            y=df["values"],
            mode="lines",
            line=dict(color=line_color, width=1.5),
            fill="tonexty",
            fillcolor=fill_color,
            hovertemplate="%{y:,.2f}<extra></extra>",
            showlegend=False,
        ))

        fig.add_hline(
            y=ref_value,
            line_dash="dot",
            line_color="rgba(0,0,0,0.25)",
            line_width=1,
        )

        fig.update_layout(
            template="plotly_white",
            # height=350,
            height=CHART_HEIGHT,
            hovermode="x unified",
            margin=dict(l=20, r=60, t=20, b=65),
            xaxis_title=None,
            yaxis_title=None,
            title=None,
            font=dict(size=11, color=ct["font_color"]),
            paper_bgcolor=ct["paper_bgcolor"],
            plot_bgcolor=ct["plot_bgcolor"],
            yaxis=dict(
                side="right",
                tickformat=",.0f",
                showgrid=False,
                zeroline=False,
            ),
            xaxis=dict(
                showgrid=False,
                type="date",
                rangeselector=dict(
                    buttons=[
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=3, label="3M", step="month", stepmode="backward"),
                        dict(count=6, label="6M", step="month", stepmode="backward"),
                        dict(count=1, label="1Y", step="year", stepmode="backward"),
                        dict(step="all", label="All"),
                    ],
                    bgcolor=ct["rs_bg"],
                    activecolor=ct["rs_active"],
                    borderwidth=0,
                    font=dict(size=11),
                    y=-0.25,
                    x=0,
                ),
            ),
        )

        fig.update_xaxes(
            showspikes=True, spikemode="across", spikesnap="cursor",
            spikedash="solid", spikecolor="rgba(0,0,0,0.2)", spikethickness=1,
        )
        fig.update_yaxes(
            showspikes=True, spikesnap="cursor",
            spikedash="solid", spikecolor="rgba(0,0,0,0.2)", spikethickness=1,
        )

        return fig


class PortfolioPNLPlotlyLineChart:
    def render(self, data, theme="light"):
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
        df = pd.DataFrame(data).sort_values("dates")

        is_positive = df["values"].iloc[-1] >= 0
        line_color = "#1a9e6e" if is_positive else "#e04040"
        fill_color = "rgba(26,158,110,0.08)" if is_positive else "rgba(224,64,64,0.08)"

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["dates"],
            y=[0] * len(df),
            mode="lines",
            line=dict(color="rgba(0,0,0,0)", width=0),
            showlegend=False,
            hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=df["dates"],
            y=df["values"],
            mode="lines",
            line=dict(color=line_color, width=1.5),
            fill="tonexty",
            fillcolor=fill_color,
            hovertemplate="%{y:,.2f}<extra></extra>",
            showlegend=False,
        ))

        fig.add_hline(
            y=0,
            line_dash="dot",
            line_color="rgba(0,0,0,0.25)",
            line_width=1,
        )

        fig.update_layout(
            template="plotly_white",
            # height=350,
            height=CHART_HEIGHT,
            hovermode="x unified",
            margin=dict(l=20, r=60, t=20, b=65),
            xaxis_title=None,
            yaxis_title=None,
            title=None,
            font=dict(size=11, color=ct["font_color"]),
            paper_bgcolor=ct["paper_bgcolor"],
            plot_bgcolor=ct["plot_bgcolor"],
            yaxis=dict(
                side="right",
                tickformat=",.0f",
                showgrid=False,
                zeroline=False,
            ),
            xaxis=dict(
                showgrid=False,
                type="date",
                rangeselector=dict(
                    buttons=[
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=3, label="3M", step="month", stepmode="backward"),
                        dict(count=6, label="6M", step="month", stepmode="backward"),
                        dict(count=1, label="1Y", step="year", stepmode="backward"),
                        dict(step="all", label="All"),
                    ],
                    bgcolor=ct["rs_bg"],
                    activecolor=ct["rs_active"],
                    borderwidth=0,
                    font=dict(size=11),
                    y=-0.25,
                    x=0,
                ),
            ),
        )

        fig.update_xaxes(
            showspikes=True, spikemode="across", spikesnap="cursor",
            spikedash="solid", spikecolor="rgba(0,0,0,0.2)", spikethickness=1,
        )
        fig.update_yaxes(
            showspikes=True, spikesnap="cursor",
            spikedash="solid", spikecolor="rgba(0,0,0,0.2)", spikethickness=1,
        )

        return fig


# Duplicate logic. Needed
# Might want to move graphs - Open/Close Principle
def performance_chart(data=None, theme="light"):
    if data is None:
        return html.P("NO DATA")
    return dbc.Row([
        dbc.Col([
            html.H6("Winners", className="text-muted mb-2"),
            dcc.Graph(id="winners_chart", figure=WinnersPlotlyBarChart().render(data, theme=theme), config=_GRAPH_CONFIG),
        ], md=6),
        dbc.Col([
            html.H6("Losers", className="text-muted mb-2"),
            dcc.Graph(id="losers_chart", figure=LosersPlotlyBarChart().render(data, theme=theme), config=_GRAPH_CONFIG),
        ], md=6),
    ], id="portfolio_page_charts")

def value_chart(data=None, theme="light"):
    if data is None:
        return html.P("NO DATA")
    return dcc.Graph(
        id="value_chart",
        figure=PortfolioPerformancePlotlyLineChart().render(data, theme=theme),
        config=_GRAPH_CONFIG,
    )


def pnl_chart(data=None, theme="light"):
    if data is None:
        return html.P("NO DATA")
    return dcc.Graph(
        id="pnl_char",
        figure=PortfolioPNLPlotlyLineChart().render(data, theme=theme),
        config=_GRAPH_CONFIG,
    )
