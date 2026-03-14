import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import dcc, html


_GRAPH_CONFIG = {"displayModeBar": False}

CHART_HEIGHT = 250

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


class PortfolioPerformanceScatterPlot:
    def render(self, data, theme="light"):
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
        df = pd.DataFrame(data)
        
        fig = px.scatter(
            df,
            x="profit",
            y="weight_pct",
            color="value",
            size="weight_pct",
            hover_data=['ticker', 'name'],
            color_continuous_scale=px.colors.sequential.Agsunset,
            color_discrete_sequence=px.colors.sequential.Agsunset,
            
        )

        # Add horizontal line at profit = 0
        threshold = df["weight_pct"].median()

        fig.add_hline(
            y=threshold,
            line_color="rgba(255,220,0,0.6)",
            line_width=1,
            line_dash="dash"
        )
        
        fig.add_vline(
            x=0,
            line_color="red",
            line_width=1,
            line_dash="dash"
        )
        
        
        fig.add_annotation(
            x=0.95,
            y=0.95,
            text="High Value Winners",
            showarrow=False,
            xref="paper",
            yref="paper"
        )
        
        fig.add_annotation(
            x=0.05,
            y=0.05,
            text="Speculative",
            showarrow=False,
            xref="paper",
            yref="paper"
        )
        
        fig.add_annotation(
            x=0.95,
            y=0.05,
            text="Low Value Winners",
            showarrow=False,
            xref="paper",
            yref="paper"
        )
        
        fig.add_annotation(
            x=0.05,
            y=0.95,
            text="Dead Weights",
            showarrow=False,
            xref="paper",
            yref="paper"
        )
        
        # fig.add_shape(
        #     type="rect",
        #     x0=0,
        #     x1=df["profit"].max(),
        #     y0=threshold,
        #     y1=df["weight_pct"].max(),
        #     fillcolor="rgba(0,200,150,0.08)",  # green
        #     line_width=0,
        # )
        fig.add_shape(
            type="rect",
            x0=0,
            x1=df["profit"].max(),
            y0=threshold,
            y1=df["weight_pct"].max(),
            fillcolor=px.colors.sequential.Aggrnyl[1],
            opacity=0.2,
            line_width=0,
        )

        fig.add_shape(
            type="rect",
            x0=0,
            x1=df["profit"].max(),
            y0=0,
            y1=threshold,
            fillcolor=px.colors.sequential.Agsunset[1],
            opacity=0.2, # yellow
            line_width=0,
        )

        fig.add_shape(
            type="rect",
            x0=df["profit"].min(),
            x1=0,
            y0=threshold,
            y1=df["weight_pct"].max(),
            fillcolor=px.colors.sequential.Agsunset[4],
            opacity=0.2,  # red
            line_width=0,
        )
        fig.update_layout(
            template="plotly_white",
            margin=dict(l=5, r=5, t=5, b=5),
            colorway=px.colors.sequential.Agsunset,
            height=500,
            xaxis_title="Profit - €",
            yaxis_title="% Weight",
            # xaxis_title=None,
            # yaxis_title=None,
            yaxis=dict(side="right", showgrid=False, zeroline=False),
            xaxis=dict(showgrid=False, zeroline=False),
            font=dict(size=11, color=ct["font_color"]),
            # bargap=0.3,
            paper_bgcolor=ct["paper_bgcolor"],
            plot_bgcolor=ct["plot_bgcolor"],
            showlegend=False,
            coloraxis_showscale=False,
            title=None,
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
 
class WinnersPlotlyBarChart:
    def render(self, data, theme="light"):
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
        
        df = pd.DataFrame(data)
        df = df.sort_values("profit", ascending=True)

        fig = px.bar(
            df,
            x="profit",
            y="ticker",
            orientation="h",
            text="profit",
            labels=["profit", "name"],
            color="profit",
            # color_discrete_map=px.colors.sequential.Bluyl_r,
            color_discrete_sequence=px.colors.sequential.Bluyl_r,
            color_continuous_scale=px.colors.sequential.Bluyl,
            
        )

        fig.update_traces(
            marker=dict(
                # color="#1a9e6e",
                line=dict(width=0),
            ),
            texttemplate="%{text:+.2f}",
            textposition="inside",
            textfont=dict(color=ct["font_color"], size=11),
        )

        fig.update_layout(
            template="plotly_white",
            colorway=px.colors.sequential.Bluyl_r,
            margin=dict(l=5, r=5, t=5, b=5),
            height=250,
            xaxis_title=None,
            yaxis_title=None,
            yaxis=dict(side="left", showgrid=False, zeroline=False),
            xaxis=dict(showgrid=False, zeroline=False),
            font=dict(size=11, color=ct["font_color"]),
            bargap=0.3,
            paper_bgcolor=ct["paper_bgcolor"],
            plot_bgcolor=ct["plot_bgcolor"],
            title=None,
            coloraxis_showscale=False,
            showlegend=False,
        )

        return fig


class LosersPlotlyBarChart:
    def render(self, data, theme="light"):
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
        df = pd.DataFrame(data)
        df = df.sort_values("profit", ascending=False)

        fig = px.bar(
            df,
            x="profit",
            y="ticker",
            orientation="h",
            text="profit",
            color="profit",
            labels=["profit", "name"],
            color_continuous_scale=px.colors.sequential.Reds_r,
            color_discrete_sequence=px.colors.sequential.Brwnyl_r,
        )

        fig.update_traces(
            marker=dict(
                # color="#d34b49",
                line=dict(width=0),
            ),
            texttemplate="%{text:+.2f}",
            textposition="inside",
            textfont=dict(color=ct["font_color"], size=11),
        )

        fig.update_layout(
            template="plotly_white",
            colorway=px.colors.sequential.Bluyl_r,
            # height=350,
            height=250,
            margin=dict(l=5, r=5, t=5, b=5),
            xaxis_title=None,
            yaxis_title=None,
            yaxis=dict(side="right", showgrid=False, zeroline=False),
            xaxis=dict(showgrid=False, zeroline=False),
            font=dict(size=11, color=ct["font_color"]),
            bargap=0.3,
            paper_bgcolor=ct["paper_bgcolor"],
            plot_bgcolor=ct["plot_bgcolor"],
            coloraxis_showscale=False,
            title=None,
        )

        return fig


class PositionWeightPlotlyDonutChart:
    
    def render (self, data, theme="light"):
        t = CHART_THEMES.get(theme or "light", CHART_THEMES["light"])
        if not data:
            return go.Figure()
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
        df = pd.DataFrame(data)
        
        labels = df['ticker']
        values = df['weight_pct']
        
        fig = go.Figure(go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            # marker=dict(colors=colors, line=dict(width=0)),
            textinfo="percent+label",
            textfont=dict(color="#ffffff", size=10),
            hovertemplate="%{label}: %{percent}<extra></extra>",
        ))
        fig.update_layout(
            colorway=px.colors.sequential.Bluyl_r,
            # colorway=px.colors.sequential.Agsunset,
            height=400,
            # width=300,
            margin=dict(l=2, r=2, t=2, b=2),
            paper_bgcolor=t["paper_bgcolor"],
            plot_bgcolor=t["plot_bgcolor"],
            font=dict(size=10, color=t["font_color"]),
            showlegend=True,
            legend=dict(font=dict(color=t["font_color"], size=9)),
        )
        return fig

class PositionWeightPlotlyBarChart:
    def render(self, data, theme="light"):
        if not data:
            return go.Figure()
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
        df = pd.DataFrame(data)

        fig = px.bar(
            df,
            x="weight_pct",
            y="ticker",
            # orientation="h",
            text="weight_pct",
            color_continuous_scale=px.colors.sequential.Bluyl_r,
            color_discrete_sequence=px.colors.sequential.Bluyl_r,
        )

        fig.update_traces(
            marker=dict(
                color="#3d89a7",
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
            line_width=2,
            annotation_text="5%",
            annotation_font_size=10,
            annotation_font_color="rgba(200,80,80,0.7)",
        )

        fig.update_layout(
            template="plotly_white",
            colorway=px.colors.sequential.Bluyl_r,
            margin=dict(l=80, r=60, t=10, b=20),
            height=380,
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
            line=dict(color="rgba(0,0,0,0)", width=1),
            showlegend=False,
            hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=df["dates"],
            y=df["values"],
            mode="lines",
            # line=dict(color=line_color, width=1.5),
            fill="tonexty",
            # fillcolor=fill_color,
            hovertemplate="%{y:,.2f}<extra></extra>",
            showlegend=False,
        ))

        fig.add_hline(
            y=ref_value,
            line_dash="dot",
            line_color="rgba(0,0,0,0.25)",
            line_width=0.1,
        )

        fig.update_layout(
            template="plotly_white",
            # height=350,
            colorway=px.colors.sequential.Bluyl_r,
            height=CHART_HEIGHT,
            hovermode="x unified",
            margin=dict(l=5, r=5, t=5, b=5),
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
                # rangeselector=dict(
                #     buttons=[
                #         dict(count=1, label="1M", step="month", stepmode="backward"),
                #         dict(count=3, label="3M", step="month", stepmode="backward"),
                #         dict(count=6, label="6M", step="month", stepmode="backward"),
                #         dict(count=1, label="1Y", step="year", stepmode="backward"),
                #         dict(step="all", label="All"),
                #     ],
                #     bgcolor=ct["rs_bg"],
                #     activecolor=ct["rs_active"],
                #     borderwidth=0,
                #     font=dict(size=11),
                #     y=-0.25,
                #     x=0,
                # ),
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
            # line=dict(color=line_color, width=1.5),
            fill="tonexty",
            # fillcolor=fill_color,
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
            colorway=px.colors.sequential.Bluyl_r,
            # height=350,
            height=CHART_HEIGHT,
            hovermode="x unified",
            margin=dict(l=5, r=5, t=5, b=5),
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
                # rangeselector=dict(
                #     buttons=[
                #         dict(count=1, label="1M", step="month", stepmode="backward"),
                #         dict(count=3, label="3M", step="month", stepmode="backward"),
                #         dict(count=6, label="6M", step="month", stepmode="backward"),
                #         dict(count=1, label="1Y", step="year", stepmode="backward"),
                #         dict(step="all", label="All"),
                #     ],
                #     bgcolor=ct["rs_bg"],
                #     activecolor=ct["rs_active"],
                #     borderwidth=0,
                #     font=dict(size=11),
                #     y=-0.25,
                #     x=0,
                # ),
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
