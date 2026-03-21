import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import dcc, html
from plotly.subplots import make_subplots


_GRAPH_CONFIG = {"displayModeBar": False}

CHART_HEIGHT_1 = 200
CHART_HEIGHT = 230


def _apply_spike_config(fig):
    fig.update_xaxes(
        showspikes=True, spikemode="across", spikesnap="cursor",
        spikedash="solid", spikecolor="rgba(0,0,0,0.2)", spikethickness=1,
    )
    fig.update_yaxes(
        showspikes=True, spikesnap="cursor",
        spikedash="solid", spikecolor="rgba(0,0,0,0.2)", spikethickness=1,
    )

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
        fig.add_trace(go.Scatter(
            x=keys, y=values,
            mode="lines",
            line=dict(color="rgba(0,0,0,0)", width=0),
            showlegend=False,
            hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=keys, y=values,
            mode="lines",
            line=dict(width=1.5),
            fill=self.fill,
            hovertemplate="%{y:,.2f}<extra></extra>",
            showlegend=False,
        ))
        fig.add_hline(
            y=values[0],
            line_dash="dot",
            line_color="rgba(0,0,0,0.25)",
            line_width=1,
        )
        fig.update_layout(
            template="plotly_white",
            colorway=self.colorway,
            height=CHART_HEIGHT_1,
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

class LosersPnLPlotlyLineChart(_PnLPlotlyLineChart):
    colorway = px.colors.sequential.Brwnyl_r
    fill = "tozerox"
class PortfolioPerformanceScatterPlot:
    def render(self, data, theme="light"):
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
            hover_data=['ticker', 'name', 'profit'],
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
            line_dash="dash"
        )

        fig.add_vline(
            x=0,
            line_color="red",
            line_width=1,
            line_dash="dash"
        )

        # Quadrant label midpoints in data coordinates
        left_mid = (ret_min + 0) / 2 if ret_min < 0 else ret_min - 0.5
        right_mid = (0 + ret_max) / 2
        low_mid = (0 + threshold) / 2
        high_mid = (threshold + weight_max) / 2

        label_font = dict(size=9, color="gray")
        for text, x, y in [
            ("High Value Winners", right_mid, high_mid),
            ("Dead Weights",       left_mid,  high_mid),
            ("Low Value Winners",  right_mid, low_mid),
            ("Speculative",        left_mid,  low_mid),
        ]:
            fig.add_annotation(
                x=x, y=y,
                text=text,
                showarrow=False,
                xref="x", yref="y",
                font=label_font,
                opacity=0.7,
            )

        # Threshold line labels
        fig.add_annotation(
            x=0, y=weight_max,
            text="0% return",
            showarrow=False,
            xref="x", yref="y",
            font=dict(size=8, color="red"),
            xanchor="left", yanchor="top",
            xshift=3,
        )
        fig.add_annotation(
            x=ret_max, y=threshold,
            text=f"Median weight ({threshold:.1f}%)",
            showarrow=False,
            xref="x", yref="y",
            font=dict(size=8, color="rgba(200,180,0,0.9)"),
            xanchor="right", yanchor="bottom",
        )

        # Ticker labels on hover
        fig.update_traces(
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "%{customdata[1]}<br>"
                "ROI: %{x:.1f}%<br>"
                "Total Return: £%{customdata[2]:,.0f}<br>"
                "Weight: %{y:.1f}%<br>"
                "Value: £%{marker.color:,.0f}"
                "<extra></extra>"
            )
        )
        
        # fig.add_shape(
        #     type="rect",
        #     x0=0,
        #     x1=df["profit"].max(),
        #     y0=threshold,
        #     y1=df["weight_pct"].max(),
        #     fillcolor="rgba(0,200,CHART_HEIGHT_1,0.08)",  # green
        #     line_width=0,
        # )
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
            opacity=0.1, # yellow
            line_width=0,
        )

        fig.add_shape(
            type="rect",
            x0=ret_min,
            x1=0,
            y0=threshold,
            y1=weight_max,
            fillcolor=px.colors.sequential.Agsunset[4],
            opacity=0.1,  # red
            line_width=0,
        )
        fig.update_layout(
            template="plotly_white",
            margin=dict(l=5, r=5, t=5, b=5),
            colorway=px.colors.sequential.Agsunset,
            height=350,
            xaxis_title="ROI %",
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

        _apply_spike_config(fig)
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
            data_frame=df, x=x_col, y="ticker", orientation="h",
            text="label", labels=[x_col, "name"], color=x_col,
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
            yaxis=dict(side=self.y_axis_side, showgrid=False, zeroline=False, showticklabels=False),
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


class DailyMoversBarChart:
    def render(self, data, theme="light", x_col="daily_return"):
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
        if not data:
            return go.Figure()

        df = pd.DataFrame(data)
        df[x_col] = pd.to_numeric(df[x_col], errors="coerce").fillna(0)

        gainers = df[df[x_col] > 0].sort_values(x_col, ascending=False).head(8).copy()
        losers  = df[df[x_col] < 0].sort_values(x_col, ascending=True).head(8).copy()

        gainers["display"] = gainers["ticker"] + "  +" + gainers[x_col].map(lambda v: f"{v:.2f}%")
        losers["display"]  = losers["ticker"]  + "  "  + losers[x_col].map(lambda v: f"{v:.2f}%")

        fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.06)
        axis_style = dict(showgrid=False, zeroline=False, showticklabels=False)

        # Gainers panel — sorted ascending so the largest bar sits at the top
        g = gainers.sort_values(x_col, ascending=True)
        fig.add_trace(go.Bar(
            x=g[x_col], y=g["ticker"], orientation="h",
            text=g["display"], textposition="auto",
            marker=dict(color=px.colors.diverging.RdYlGn[-3], line=dict(width=0)),
            textfont=dict(size=11),
            showlegend=False,
            hovertemplate="%{text}<extra></extra>",
        ), row=1, col=1)

        # Losers panel — largest absolute move at the top
        l = losers.sort_values(x_col, ascending=False)
        fig.add_trace(go.Bar(
            x=l[x_col].abs(), y=l["ticker"], orientation="h",
            text=l["display"], textposition="auto",
            marker=dict(color=px.colors.diverging.RdYlGn[1], line=dict(width=0)),
            textfont=dict(size=11),
            showlegend=False,
            hovertemplate="%{text}<extra></extra>",
        ), row=1, col=2)

        fig.update_xaxes(**axis_style)
        fig.update_yaxes(**axis_style)
        fig.update_layout(
            template="plotly_white",
            height=CHART_HEIGHT_1,
            margin=dict(l=4, r=4, t=4, b=4),
            paper_bgcolor=ct["paper_bgcolor"],
            plot_bgcolor=ct["plot_bgcolor"],
            font=dict(size=11, color=ct["font_color"]),
            bargap=0.25,
        )
        return fig


class VaRBarChart(_BaseRankedBarChart):
    sort_ascending = True
    y_axis_side = "right"
    color_scale = px.colors.sequential.OrRd
    use_range_color = False

    def render(self, data, theme="light"):
        return super().render(data, theme=theme, x_col="var_95_1d")

class PositionWeightPlotlyDonutChart:
    def render (self, data, theme="light"):
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
        if not data:
            return go.Figure()
        df = pd.DataFrame(data)

        labels = df['ticker']
        values = df['weight_pct']
        customdata = df['breakdown'].fillna("").values if 'breakdown' in df.columns else [""] * len(df)

        fig = go.Figure(go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            customdata=customdata,
            textinfo="percent+label",
            textfont=dict(color="#ffffff", size=10),
            hovertemplate="%{label}: %{percent}%{customdata}<extra></extra>",
        ))
        fig.update_traces(textposition='inside')
        fig.update_layout(
            colorway=px.colors.sequential.Bluyl_r,
            # colorway=px.colors.sequential.Agsunset,
            height=CHART_HEIGHT_1,
            # width=300,
            margin=dict(l=2, r=2, t=2, b=2),
            paper_bgcolor=ct["paper_bgcolor"],
            plot_bgcolor=ct["plot_bgcolor"],
            font=dict(size=10, color=ct["font_color"]),
            showlegend=False,
            legend=dict(font=dict(color=ct["font_color"], size=9)),
        )
        return fig

class PositionProfitabilityPlotlyDonutChart:
    def render (self, data, theme="light"):
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
        if not data:
            return go.Figure()
        df = pd.DataFrame(data)
        total = len(df)

        df["profitable"] = df["profit"].apply(lambda x: "profit" if x > 0 else "loss")
        df = df["profitable"].value_counts().to_frame().reset_index()

        labels = df['profitable']
        values = df['count']

        fig = go.Figure(go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            customdata=df['count'].values,
            textinfo="percent+label",
            textfont=dict(color="#ffffff", size=10),
            hovertemplate="%{label}: %{percent} (%{customdata} of " + str(total) + " positions)<extra></extra>",
        ))

        fig.update_traces(textposition='inside')

        fig.add_annotation(
            text="by # of positions",
            x=0.5, y=-0.08,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=8, color="gray"),
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
        fig.add_trace(go.Scatter(
            x=df["dates"], y=[0] * len(df),
            mode="lines", line=dict(color="rgba(0,0,0,0)", width=0),
            showlegend=False, hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=df["dates"], y=df["drawdown_pct"],
            mode="lines",
            line=dict(width=1.5, color="rgba(200,60,60,0.8)"),
            fill="toself",
            fillcolor="rgba(200,60,60,0.15)",
            hovertemplate="%{y:.2f}%<extra></extra>",
            showlegend=False,
        ))
        fig.add_hline(y=0, line_dash="dot", line_color="rgba(0,0,0,0.2)", line_width=1)
        fig.add_annotation(
            x=1, y=1, xref="paper", yref="paper",
            text=f"Max: {max_dd:.2f}%",
            showarrow=False, font=dict(size=10, color="rgba(200,60,60,0.8)"),
            xanchor="right", yanchor="top",
        )
        fig.update_layout(
            template="plotly_white",
            height=CHART_HEIGHT_1,
            hovermode="x unified",
            margin=dict(l=2, r=2, t=2, b=2),
            xaxis_title=None, yaxis_title=None, title=None,
            font=dict(size=11, color=ct["font_color"]),
            paper_bgcolor=ct["paper_bgcolor"],
            plot_bgcolor=ct["plot_bgcolor"],
            yaxis=dict(side="right", tickformat=".1f", ticksuffix="%", showgrid=False, zeroline=False),
            xaxis=dict(showgrid=False, type="date", zeroline=False),
        )
        _apply_spike_config(fig)
        return fig


class PortfolioPerformancePlotlyLineChart:
    def render(self, data, theme="light"):
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
        df = pd.DataFrame(data).sort_values("dates")

        ref_value = df["costs"].iloc[0]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["dates"],
            y=df["costs"],
            name="Invested",
            mode="lines",
            line=dict(color="rgba(0,0,0,0)", width=0),
            showlegend=False,
            hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=df["dates"],
            y=df["values"],
            name="Portfolio Value",
            mode="lines",
            line=dict(width=1.5),
            fill="tonexty",
            hovertemplate="Portfolio Value: %{y:,.2f}<extra></extra>",
            showlegend=True,
        ))
        fig.add_trace(go.Scatter(
            x=df["dates"],
            y=df["costs"],
            name="Invested",
            mode="lines",
            line=dict(width=1, dash="dot", color="rgba(150,150,150,0.6)"),
            hovertemplate="Invested: %{y:,.2f}<extra></extra>",
            showlegend=True,
        ))

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
                x=1, y=1,
                xanchor="right", yanchor="bottom",
                font=dict(size=9, color=ct["font_color"]),
                bgcolor="rgba(0,0,0,0)",
                borderwidth=0,
            ),
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

        _apply_spike_config(fig)
        return fig

class PortfolioPNLPlotlyLineChart:
    def render(self, data, theme="light"):
        ct = CHART_THEMES.get(theme, CHART_THEMES["light"])
        df = pd.DataFrame(data).sort_values("dates")

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
            name="Unrealized",
            mode="lines",
            line=dict(width=1.5),
            fill="tonexty",
            hovertemplate="Unrealized: %{y:,.2f}<extra></extra>",
            showlegend=True,
        ))
        fig.add_trace(go.Scatter(
            x=df["dates"],
            y=df["realized"],
            name="Realized",
            mode="lines",
            line=dict(width=1, dash="dot", color="rgba(150,150,150,0.6)"),
            hovertemplate="Realized: %{y:,.2f}<extra></extra>",
            showlegend=True,
        ))
        fig.add_trace(go.Scatter(
            x=df["dates"],
            y=df["total_pnl"],
            name="Total P&L",
            mode="lines",
            line=dict(width=1.5, color="rgba(100,180,100,0.8)"),
            hovertemplate="Total P&L: %{y:,.2f}<extra></extra>",
            showlegend=True,
        ))

        fig.add_hline(
            y=df["values"].iloc[0],
            line_dash="dot",
            line_color="rgba(0,0,0,0.25)",
            line_width=1,
        )

        fig.update_layout(
            template="plotly_white",
            colorway=px.colors.sequential.Bluyl_r,
            # height=350,
            height=CHART_HEIGHT_1,
            hovermode="x unified",
            margin=dict(l=5, r=5, t=5, b=5),
            xaxis_title=None,
            yaxis_title=None,
            title=None,
            showlegend=True,
            legend=dict(
                orientation="h",
                x=1, y=1,
                xanchor="right", yanchor="bottom",
                font=dict(size=9, color=ct["font_color"]),
                bgcolor="rgba(0,0,0,0)",
                borderwidth=0,
            ),
            font=dict(size=11, color=ct["font_color"]),
            paper_bgcolor=ct["paper_bgcolor"],
            plot_bgcolor=ct["plot_bgcolor"],
            yaxis=dict(
                side="right",
                title=dict(text="P&L (€)", font=dict(size=9), standoff=4),
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

        _apply_spike_config(fig)
        return fig

