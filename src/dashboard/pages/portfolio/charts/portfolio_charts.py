"""Portfolio-level Plotly chart implementations."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html

from .chart_theme import (
    NEGATIVE_COLOR,
    POSITIVE_FILL,
    NEGATIVE_FILL,
    ANNOTATION_COLOR,
    MEDIAN_ANNOTATION_COLOR,
    PIE_TEXT_COLOR,
    FX_CHART_COLORS,
    CHART_THEMES,
)

CHART_HEIGHT_1 = 200
CHART_HEIGHT = 230


def _apply_spike_config(fig):
    fig.update_xaxes(
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikedash="solid",
        spikecolor="rgba(0,0,0,0.2)",
        spikethickness=1,
    )
    fig.update_yaxes(
        showspikes=True,
        spikesnap="cursor",
        spikedash="solid",
        spikecolor="rgba(0,0,0,0.2)",
        spikethickness=1,
    )


class _PnLPlotlyLineChart:
    colorway = None
    fill = "toself"

    def render(self, data, theme="light"):
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
        keys = list(data.keys())
        values = list(data.values())
        if not values:
            return go.Figure()
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=keys,
                y=values,
                mode="lines",
                line=dict(color="rgba(0,0,0,0)", width=0),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=keys,
                y=values,
                mode="lines",
                line=dict(width=1.5),
                fill=self.fill,
                hovertemplate="%{y:,.2f}<extra></extra>",
                showlegend=False,
            )
        )
        fig.add_hline(
            y=values[0],
            line_dash="dot",
            line_color="rgba(0,0,0,0.25)",
            line_width=1,
        )
        fig.update_layout(
            template="plotly_white",
            colorway=self.colorway,
            height=getattr(self, "chart_height", CHART_HEIGHT_1),
            hovermode="x unified",
            margin=dict(l=2, r=2, t=2, b=2),
            xaxis_title=None,
            yaxis_title=None,
            title=None,
            font=dict(size=11, color=ct["font_color"]),
            paper_bgcolor=ct["paper_bgcolor"],
            plot_bgcolor=ct["plot_bgcolor"],
            yaxis=dict(side="right", tickformat=",.0f", showgrid=False, zeroline=False),
            xaxis=dict(showgrid=False, type="date", zeroline=False),
        )
        _apply_spike_config(fig)
        return fig


class WinnersPnLPlotlyLineChart(_PnLPlotlyLineChart):
    colorway = px.colors.sequential.Bluyl_r
    fill = "toself"
    chart_height = 280


class LosersPnLPlotlyLineChart(_PnLPlotlyLineChart):
    colorway = px.colors.sequential.Brwnyl_r
    fill = "tozerox"


class PortfolioPerformanceScatterPlot:
    def render(self, data, theme="light", currency="", selected_tickers=None):
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
        if not data:
            return go.Figure()
        df = pd.DataFrame(data)
        for col in ["roi_pct", "weight_pct", "value", "profit"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        fig = px.scatter(
            df,
            x="roi_pct",
            y="weight_pct",
            color="value",
            size="weight_pct",
            hover_data=["ticker", "name", "profit"],
            color_continuous_scale=px.colors.sequential.Agsunset,
            color_discrete_sequence=px.colors.sequential.Agsunset,
        )

        threshold = df["weight_pct"].median()
        ret_min = df["roi_pct"].min()
        ret_max = df["roi_pct"].max()
        weight_max = df["weight_pct"].max()

        fig.add_hline(
            y=threshold,
            line_color="rgba(255,220,0,0.6)",
            line_width=1,
            line_dash="dash",
        )

        fig.add_vline(x=0, line_color=NEGATIVE_COLOR, line_width=1, line_dash="dash")

        left_mid = (ret_min + 0) / 2 if ret_min < 0 else ret_min - 0.5
        right_mid = (0 + ret_max) / 2
        low_mid = (0 + threshold) / 2
        high_mid = (threshold + weight_max) / 2

        label_font = dict(size=9, color=ANNOTATION_COLOR)
        for text, x, y in [
            ("High Value Winners", right_mid, high_mid),
            ("Dead Weights", left_mid, high_mid),
            ("Low Value Winners", right_mid, low_mid),
            ("Speculative", left_mid, low_mid),
        ]:
            fig.add_annotation(
                x=x,
                y=y,
                text=text,
                showarrow=False,
                xref="x",
                yref="y",
                font=label_font,
                opacity=0.7,
            )

        fig.add_annotation(
            x=0,
            y=weight_max,
            text="0% return",
            showarrow=False,
            xref="x",
            yref="y",
            font=dict(size=8, color=NEGATIVE_COLOR),
            xanchor="left",
            yanchor="top",
            xshift=3,
        )
        fig.add_annotation(
            x=ret_max,
            y=threshold,
            text=f"Median weight ({threshold:.1f}%)",
            showarrow=False,
            xref="x",
            yref="y",
            font=dict(size=8, color=MEDIAN_ANNOTATION_COLOR),
            xanchor="right",
            yanchor="bottom",
        )

        fig.update_traces(
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "%{customdata[1]}<br>"
                "ROI: %{x:.1f}%<br>"
                f"Total Return: {currency}%{{customdata[2]:,.0f}}<br>"
                "Weight: %{y:.1f}%<br>"
                f"Value: {currency}%{{marker.color:,.0f}}"
                "<extra></extra>"
            )
        )

        fig.add_shape(
            type="rect",
            x0=0,
            x1=ret_max,
            y0=threshold,
            y1=weight_max,
            fillcolor=px.colors.sequential.Bluyl_r[1],
            opacity=0.1,
            line_width=0,
        )
        fig.add_shape(
            type="rect",
            x0=0,
            x1=ret_max,
            y0=0,
            y1=threshold,
            fillcolor=px.colors.sequential.Agsunset[1],
            opacity=0.1,
            line_width=0,
        )
        fig.add_shape(
            type="rect",
            x0=ret_min,
            x1=0,
            y0=threshold,
            y1=weight_max,
            fillcolor=px.colors.sequential.Agsunset[4],
            opacity=0.1,
            line_width=0,
        )
        fig.update_layout(
            template="plotly_white",
            margin=dict(l=5, r=5, t=5, b=5),
            colorway=px.colors.sequential.Agsunset,
            height=280,
            xaxis_title="ROI %",
            yaxis_title="% Weight",
            yaxis=dict(side="right", showgrid=False, zeroline=False),
            xaxis=dict(showgrid=False, zeroline=False),
            font=dict(size=11, color=ct["font_color"]),
            paper_bgcolor=ct["paper_bgcolor"],
            plot_bgcolor=ct["plot_bgcolor"],
            showlegend=False,
            coloraxis_showscale=False,
            title=None,
        )

        _apply_spike_config(fig)

        if selected_tickers:
            sel_df = df[df["ticker"].isin(selected_tickers)]
            if not sel_df.empty:
                fig.update_traces(opacity=0.15)

                max_weight = df["weight_pct"].max()
                sizeref = 2.0 * max_weight / (20.0**2)

                fig.add_trace(
                    go.Scatter(
                        x=sel_df["roi_pct"],
                        y=sel_df["weight_pct"],
                        mode="markers",
                        marker=dict(
                            size=sel_df["weight_pct"].values,
                            sizemode="area",
                            sizeref=sizeref,
                            color=sel_df["value"].values,
                            colorscale=px.colors.sequential.Agsunset,
                            showscale=False,
                            line=dict(color="white", width=2),
                            opacity=1.0,
                        ),
                        customdata=sel_df[["ticker", "name", "profit"]].values,
                        hovertemplate=(
                            "<b>%{customdata[0]}</b><br>"
                            "%{customdata[1]}<br>"
                            "ROI: %{x:.1f}%<br>"
                            f"Total Return: {currency}%{{customdata[2]:,.0f}}<br>"
                            "Weight: %{y:.1f}%<br>"
                            "<extra></extra>"
                        ),
                        showlegend=False,
                    )
                )

        return fig


class _BaseRankedBarChart:
    sort_ascending: bool = True
    y_axis_side: str = "left"
    color_scale = px.colors.diverging.RdYlGn
    use_range_color: bool = True

    def render(self, data, theme="light", x_col="profit"):
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
        df = pd.DataFrame(data)
        df[x_col] = pd.to_numeric(df[x_col], errors="coerce")
        df = df.sort_values(x_col, ascending=self.sort_ascending)
        max_val = df[x_col].abs().max() or 1

        bar_kwargs = dict(
            data_frame=df,
            x=x_col,
            y="ticker",
            orientation="h",
            text="label",
            labels=[x_col, "name"],
            color=x_col,
            color_continuous_scale=self.color_scale,
        )
        if self.use_range_color:
            bar_kwargs["range_color"] = [-max_val, max_val]
        fig = px.bar(**bar_kwargs)

        fig.update_traces(
            marker=dict(line=dict(width=0)),
            texttemplate="%{text}",
            textposition="auto",
            textfont=dict(color=ct["font_color"], size=13),
        )

        fig.update_layout(
            template="plotly_white",
            margin=dict(l=4, r=4, t=4, b=4),
            height=CHART_HEIGHT_1,
            xaxis_title=None,
            yaxis_title=None,
            yaxis=dict(
                side=self.y_axis_side,
                showgrid=False,
                zeroline=False,
                showticklabels=False,
            ),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            font=dict(size=11, color=ct["font_color"]),
            bargap=0.15,
            paper_bgcolor=ct["paper_bgcolor"],
            plot_bgcolor=ct["plot_bgcolor"],
            title=None,
            coloraxis_showscale=False,
            showlegend=False,
        )

        return fig


class WinnersPlotlyBarChart(_BaseRankedBarChart):
    sort_ascending = True
    y_axis_side = "left"


class LosersPlotlyBarChart(_BaseRankedBarChart):
    sort_ascending = False
    y_axis_side = "right"


_PCT_COLS = {"daily_return", "cumulative_return", "weight_pct", "pnl_pct"}


def _ranked_panel(data, sort_by="profit", is_gain=True):
    """Single Winners or Losers inline-bar panel. Data is pre-sorted."""
    if not data:
        return html.Div("—", className="movers-empty")

    df = pd.DataFrame(data)
    values = pd.to_numeric(df[sort_by], errors="coerce").fillna(0)
    max_val = values.abs().max() or 1

    fmt = (
        (lambda v: f"+{v:.2f}%" if v >= 0 else f"{v:.2f}%")
        if sort_by in _PCT_COLS
        else (lambda v: f"+{v:,.2f}" if v >= 0 else f"{v:,.2f}")
    )

    bg = POSITIVE_FILL if is_gain else NEGATIVE_FILL
    val_cls = "movers-value--gain" if is_gain else "movers-value--loss"
    lbl_cls = "movers-panel-label--gain" if is_gain else "movers-panel-label--loss"

    rows = []
    for v, (_, r) in zip(values, df.iterrows()):
        fill = abs(v) / max_val * 100
        rows.append(
            html.Div(
                [
                    html.Span(r["ticker"], className="movers-ticker"),
                    html.Span(fmt(v), className=val_cls),
                ],
                id={"type": "chart-mover-row", "index": str(r["ticker"])},
                n_clicks=0,
                className="movers-row",
                style={
                    "background": f"linear-gradient(to right, {bg} {fill:.0f}%, transparent {fill:.0f}%)",
                    "cursor": "pointer",
                },
            )
        )

    label = "Winners" if is_gain else "Losers"
    return html.Div(
        [
            html.Div(label, className=f"movers-panel-label {lbl_cls}"),
            html.Div(rows),
        ]
    )


def daily_movers_table(data, n=5):
    """Inline-bar movers table: two panels (Gainers / Losers), each with n rows."""
    if not data:
        return html.Div()

    df = pd.DataFrame(data)
    df["daily_return"] = pd.to_numeric(df["daily_return"], errors="coerce").fillna(0)

    gainers = (
        df[df["daily_return"] > 0].sort_values("daily_return", ascending=False).head(n)
    )
    losers = (
        df[df["daily_return"] < 0].sort_values("daily_return", ascending=True).head(n)
    )

    gain_max = gainers["daily_return"].max() if not gainers.empty else 1
    loss_max = losers["daily_return"].abs().max() if not losers.empty else 1

    def _row(ticker, value, is_gain):
        fill = abs(value) / (gain_max if is_gain else loss_max) * 100
        bg = POSITIVE_FILL if is_gain else NEGATIVE_FILL
        label = f"+{value:.2f}%" if is_gain else f"{value:.2f}%"
        return html.Div(
            [
                html.Span(ticker, className="movers-ticker"),
                html.Span(
                    label,
                    className="movers-value--gain" if is_gain else "movers-value--loss",
                ),
            ],
            className="movers-row",
            style={
                "background": f"linear-gradient(to right, {bg} {fill:.0f}%, transparent {fill:.0f}%)",
            },
        )

    def _panel(label, rows_df, is_gain):
        rows = (
            [
                _row(r["ticker"], r["daily_return"], is_gain)
                for _, r in rows_df.iterrows()
            ]
            if not rows_df.empty
            else [html.Div("—", className="movers-empty")]
        )
        cls = "movers-panel-label--gain" if is_gain else "movers-panel-label--loss"
        return html.Div(
            [
                html.Div(label, className=f"movers-panel-label {cls}"),
                html.Div(rows),
            ]
        )

    return dbc.Row(
        [
            dbc.Col(_panel("Gainers", gainers, True)),
            dbc.Col(_panel("Losers", losers, False)),
        ],
        className="g-3",
    )


class VaRBarChart(_BaseRankedBarChart):
    sort_ascending = True
    y_axis_side = "right"
    color_scale = px.colors.sequential.OrRd
    use_range_color = False

    def render(self, data, theme="light"):
        return super().render(data, theme=theme, x_col="var_95_1d")


class PositionWeightPlotlyDonutChart:
    def render(self, data, avg_weight=0, theme="light"):
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
        if not data:
            return go.Figure()
        df = pd.DataFrame(data)

        labels = df["ticker"]
        values = df["weight_pct"]
        customdata = (
            df["breakdown"].fillna("").values
            if "breakdown" in df.columns
            else [""] * len(df)
        )

        fig = go.Figure(
            go.Pie(
                labels=labels,
                values=values,
                hole=0.6,
                customdata=customdata,
                textinfo="none",
                marker=dict(line=dict(width=0)),
                hovertemplate="%{label}: %{percent}%{customdata}<extra></extra>",
            )
        )
        fig.update_layout(
            colorway=px.colors.sequential.Bluyl_r,
            height=CHART_HEIGHT_1,
            margin=dict(l=2, r=2, t=2, b=40),
            paper_bgcolor=ct["paper_bgcolor"],
            plot_bgcolor=ct["plot_bgcolor"],
            font=dict(size=10, color=ct["font_color"]),
            showlegend=False,
            annotations=[
                dict(
                    text=f"{avg_weight}%<br><span style='font-size:9px'>Avg Weight</span>",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=11, color=ct["font_color"]),
                )
            ],
        )
        return fig


class PositionProfitabilityPlotlyDonutChart:
    def render(self, data, theme="light"):
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
        if not data:
            return go.Figure()
        df = pd.DataFrame(data)
        total = len(df)

        df["profitable"] = df["profit"].apply(lambda x: "profit" if x > 0 else "loss")
        df = df["profitable"].value_counts().to_frame().reset_index()

        labels = df["profitable"]
        values = df["count"]

        fig = go.Figure(
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                customdata=df["count"].values,
                textinfo="percent+label",
                textfont=dict(color=PIE_TEXT_COLOR, size=10),
                hovertemplate="%{label}: %{percent} (%{customdata} of "
                + str(total)
                + " positions)<extra></extra>",
            )
        )

        fig.update_traces(textposition="inside")

        fig.add_annotation(
            text="by # of positions",
            x=0.5,
            y=-0.08,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=8, color=ANNOTATION_COLOR),
        )

        fig.update_layout(
            colorway=px.colors.sequential.Bluyl_r,
            height=CHART_HEIGHT_1,
            margin=dict(l=2, r=2, t=2, b=2),
            paper_bgcolor=ct["paper_bgcolor"],
            plot_bgcolor=ct["plot_bgcolor"],
            font=dict(size=10, color=ct["font_color"]),
            showlegend=False,
            legend=dict(font=dict(color=ct["font_color"], size=9)),
        )
        return fig


class PortfolioDrawdownPlotlyLineChart:
    def render(self, data, theme="light"):
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
        if not data or not data.get("dates"):
            return go.Figure()
        df = pd.DataFrame(data).sort_values("dates")
        max_dd = df["drawdown_pct"].min()

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=[0] * len(df),
                mode="lines",
                line=dict(color="rgba(0,0,0,0)", width=0),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=df["drawdown_pct"],
                mode="lines",
                line=dict(width=1.5, color="rgba(200,60,60,0.8)"),
                fill="toself",
                fillcolor="rgba(200,60,60,0.15)",
                hovertemplate="%{y:.2f}%<extra></extra>",
                showlegend=False,
            )
        )
        fig.add_hline(y=0, line_dash="dot", line_color="rgba(0,0,0,0.2)", line_width=1)
        fig.add_annotation(
            x=1,
            y=1,
            xref="paper",
            yref="paper",
            text=f"Max: {max_dd:.2f}%",
            showarrow=False,
            font=dict(size=10, color="rgba(200,60,60,0.8)"),
            xanchor="right",
            yanchor="top",
        )
        fig.update_layout(
            template="plotly_white",
            height=CHART_HEIGHT_1,
            hovermode="x unified",
            margin=dict(l=2, r=2, t=2, b=2),
            xaxis_title=None,
            yaxis_title=None,
            title=None,
            font=dict(size=11, color=ct["font_color"]),
            paper_bgcolor=ct["paper_bgcolor"],
            plot_bgcolor=ct["plot_bgcolor"],
            yaxis=dict(
                side="right",
                tickformat=".1f",
                ticksuffix="%",
                showgrid=False,
                zeroline=False,
            ),
            xaxis=dict(showgrid=False, type="date", zeroline=False),
        )
        _apply_spike_config(fig)
        return fig


class PortfolioPerformancePlotlyLineChart:
    def render(self, data, theme="light"):
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
        df = pd.DataFrame(data)
        if df.empty or "dates" not in df.columns:
            fig = go.Figure()
            fig.update_layout(
                paper_bgcolor=ct["paper_bgcolor"],
                plot_bgcolor=ct["plot_bgcolor"],
                font=dict(color=ct["font_color"]),
                margin=dict(l=2, r=2, t=2, b=2),
            )
            return fig
        df = df.sort_values("dates")
        ref_value = df["costs"].iloc[0]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=df["costs"],
                name="Invested",
                mode="lines",
                line=dict(color="rgba(0,0,0,0)", width=0),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=df["values"],
                name="Portfolio Value",
                mode="lines",
                line=dict(width=1.5),
                fill="tonexty",
                hovertemplate="Portfolio Value: %{y:,.2f}<extra></extra>",
                showlegend=True,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=df["costs"],
                name="Invested",
                mode="lines",
                line=dict(width=1, dash="dot", color="rgba(150,150,150,0.6)"),
                hovertemplate="Invested: %{y:,.2f}<extra></extra>",
                showlegend=True,
            )
        )

        fig.add_hline(
            y=ref_value,
            line_dash="dot",
            line_color="rgba(0,0,0,0.25)",
            line_width=0.1,
            opacity=0.2,
        )

        fig.update_layout(
            template="plotly_white",
            colorway=px.colors.sequential.Bluyl_r,
            height=CHART_HEIGHT_1,
            hovermode="x unified",
            margin=dict(l=2, r=2, t=2, b=2),
            xaxis_title=None,
            yaxis_title=None,
            title=None,
            showlegend=True,
            legend=dict(
                orientation="h",
                x=1,
                y=1,
                xanchor="right",
                yanchor="bottom",
                font=dict(size=9, color=ct["font_color"]),
                bgcolor="rgba(0,0,0,0)",
                borderwidth=0,
            ),
            font=dict(size=11, color=ct["font_color"]),
            paper_bgcolor=ct["paper_bgcolor"],
            plot_bgcolor=ct["plot_bgcolor"],
            yaxis=dict(side="right", tickformat=",.0f", showgrid=False, zeroline=False),
            xaxis=dict(showgrid=False, type="date"),
        )

        _apply_spike_config(fig)
        return fig


class PortfolioPNLPlotlyLineChart:
    def render(self, data, theme="light", currency=""):
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
        df = pd.DataFrame(data).sort_values("dates")

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=[0] * len(df),
                mode="lines",
                line=dict(color="rgba(0,0,0,0)", width=0),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=df["values"],
                name="Unrealized",
                mode="lines",
                line=dict(width=1.5),
                fill="tonexty",
                hovertemplate="Unrealized: %{y:,.2f}<extra></extra>",
                showlegend=True,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=df["realized"],
                name="Realized",
                mode="lines",
                line=dict(width=1, dash="dot", color="rgba(150,150,150,0.6)"),
                hovertemplate="Realized: %{y:,.2f}<extra></extra>",
                showlegend=True,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df["dates"],
                y=df["total_pnl"],
                name="Total P&L",
                mode="lines",
                line=dict(width=1.5, color="rgba(100,180,100,0.8)"),
                hovertemplate="Total P&L: %{y:,.2f}<extra></extra>",
                showlegend=True,
            )
        )

        fig.add_hline(
            y=df["values"].iloc[0],
            line_dash="dot",
            line_color="rgba(0,0,0,0.25)",
            line_width=1,
        )

        fig.update_layout(
            template="plotly_white",
            colorway=px.colors.sequential.Bluyl_r,
            height=CHART_HEIGHT_1,
            hovermode="x unified",
            margin=dict(l=5, r=5, t=5, b=5),
            xaxis_title=None,
            yaxis_title=None,
            title=None,
            showlegend=True,
            legend=dict(
                orientation="h",
                x=1,
                y=1,
                xanchor="right",
                yanchor="bottom",
                font=dict(size=9, color=ct["font_color"]),
                bgcolor="rgba(0,0,0,0)",
                borderwidth=0,
            ),
            font=dict(size=11, color=ct["font_color"]),
            paper_bgcolor=ct["paper_bgcolor"],
            plot_bgcolor=ct["plot_bgcolor"],
            yaxis=dict(
                side="right",
                title=dict(text=f"P&L ({currency})", font=dict(size=9), standoff=4),
                tickformat=",.0f",
                showgrid=False,
                zeroline=False,
            ),
            xaxis=dict(showgrid=False, type="date"),
        )

        _apply_spike_config(fig)
        return fig


class PortfolioFXAttributionDonutChart:
    def render(self, data, theme="light"):
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
        fx_impact = data.get("fx_impact_total") or 0
        unrealized_pnl = data.get("unrealized_pnl") or 0
        price_return = unrealized_pnl - fx_impact

        abs_fx = abs(fx_impact)
        abs_price = abs(price_return)
        total = abs_fx + abs_price

        if total == 0:
            fig = go.Figure()
            fig.update_layout(
                paper_bgcolor=ct["paper_bgcolor"],
                plot_bgcolor=ct["plot_bgcolor"],
                height=CHART_HEIGHT_1,
                margin=dict(l=2, r=2, t=2, b=2),
                annotations=[
                    dict(
                        text="No FX data",
                        x=0.5,
                        y=0.5,
                        showarrow=False,
                        font=dict(size=12, color=ct["font_color"]),
                    )
                ],
            )
            return fig

        fx_sign = "+" if fx_impact >= 0 else ""
        colors = FX_CHART_COLORS.get(theme, FX_CHART_COLORS["light"])

        fig = go.Figure(
            go.Pie(
                labels=["FX Return", "Price Return"],
                values=[abs_fx, abs_price],
                hole=0.6,
                marker=dict(colors=colors, line=dict(width=0)),
                textinfo="none",
                hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>",
                showlegend=True,
            )
        )
        fig.update_layout(
            paper_bgcolor=ct["paper_bgcolor"],
            plot_bgcolor=ct["plot_bgcolor"],
            font=dict(size=11, color=ct["font_color"]),
            height=CHART_HEIGHT_1,
            margin=dict(l=2, r=2, t=2, b=40),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5,
                font=dict(size=10, color=ct["font_color"]),
            ),
            annotations=[
                dict(
                    text=f"{fx_sign}{fx_impact:,.2f}<br><span style='font-size:9px'>Portfolio FX</span>",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=11, color=ct["font_color"]),
                )
            ],
        )
        return fig
