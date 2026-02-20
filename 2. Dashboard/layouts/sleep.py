"""Sleep module layout (Apple Health).

Shows:
  - Average sleep hours this week (stat)
  - Bar chart: hours per night for last 7 days with 8-hr target line

Calls modules/apple_health.py at render time.
"""

import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc

from modules import apple_health

CHART_PAPER_BG = "rgba(0,0,0,0)"
CHART_PLOT_BG = "rgba(0,0,0,0)"
CHART_FONT_COLOR = "#8b949e"
CHART_GRID_COLOR = "#21262d"
COLOR_BLUE = "#58a6ff"
TARGET_SLEEP_HRS = 8.0


def _sleep_chart(df):
    """Bar chart of nightly sleep hours."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["date"],
        y=df["sleep_hours"],
        marker_color=COLOR_BLUE,
        marker_opacity=0.8,
        hovertemplate="%{x|%a %-d}: %{y:.1f} hrs<extra></extra>",
    ))
    fig.add_hline(
        y=TARGET_SLEEP_HRS,
        line_dash="dot",
        line_color="#484f58",
        annotation_text=f"{TARGET_SLEEP_HRS} hr target",
        annotation_font_color="#484f58",
        annotation_font_size=10,
    )
    fig.update_layout(
        paper_bgcolor=CHART_PAPER_BG,
        plot_bgcolor=CHART_PLOT_BG,
        margin={"t": 8, "b": 30, "l": 38, "r": 8},
        font={"color": CHART_FONT_COLOR, "size": 11},
        showlegend=False,
        height=160,
        xaxis={"gridcolor": CHART_GRID_COLOR, "showgrid": False,
               "tickformat": "%a"},
        yaxis={"gridcolor": CHART_GRID_COLOR, "range": [0, 10],
               "ticksuffix": " h"},
        bargap=0.25,
    )
    return fig


def layout(data_dir):
    df = apple_health.get_sleep(data_dir, days=7)

    has_data = df["sleep_hours"].gt(0).any()
    if not has_data:
        return dbc.Card([
            dbc.CardHeader(html.H5("Sleep")),
            dbc.CardBody(html.P(
                "Waiting for Apple Health data.",
                className="placeholder-msg",
            )),
        ])

    valid = df.loc[df["sleep_hours"].gt(0), "sleep_hours"]
    avg = valid.mean()
    avg_color = "#3fb950" if avg >= 7.0 else "#d29922"

    return dbc.Card([
        dbc.CardHeader(html.H5("Sleep")),
        dbc.CardBody([
            html.Div([
                html.Span(f"{avg:.1f}", style={"fontSize": "2rem", "fontWeight": "700",
                                               "color": avg_color}),
                html.Span(" hrs/night avg",
                          style={"fontSize": "0.85rem", "color": "#8b949e",
                                 "marginLeft": "6px"}),
            ], className="mb-2"),
            dcc.Graph(figure=_sleep_chart(df), config={"displayModeBar": False}),
        ]),
    ])
