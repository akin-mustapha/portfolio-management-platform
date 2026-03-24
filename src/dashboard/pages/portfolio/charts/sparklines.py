"""Small inline chart functions used inside component molecules."""
import plotly.graph_objects as go

from .chart_theme import TEAL_COLOR, TEAL_FILL, NEGATIVE_COLOR, NEGATIVE_SPARKLINE_FILL, CHART_THEMES


def daily_change_sparkline(series: dict, change_sign: int, theme: str = "light") -> go.Figure:
    ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
    dates = series.get("dates", [])
    values = series.get("values", [])

    if change_sign > 0:
        line_color = TEAL_COLOR
        fill_color = TEAL_FILL
    elif change_sign < 0:
        line_color = NEGATIVE_COLOR
        fill_color = NEGATIVE_SPARKLINE_FILL
    else:
        line_color = "rgba(150,150,150,0.6)"
        fill_color = "rgba(150,150,150,0.10)"

    zeros = [0] * len(dates)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=zeros,
        mode="lines", line=dict(color="rgba(0,0,0,0)", width=0),
        showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=dates, y=values,
        mode="lines",
        line=dict(color=line_color, width=1.5),
        fill="tonexty",
        fillcolor=fill_color,
        showlegend=False, hoverinfo="skip",
    ))
    fig.update_layout(
        height=22, width=56,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=ct["paper_bgcolor"],
        plot_bgcolor=ct["plot_bgcolor"],
        xaxis=dict(visible=False, showgrid=False, zeroline=False, fixedrange=True),
        yaxis=dict(visible=False, showgrid=False, zeroline=False, fixedrange=True),
        dragmode=False,
    )
    return fig
