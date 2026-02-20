"""Learning module layout - study hours (Apple Health) and Dreaming Spanish.

Left panel: Study hours this week (mindfulness minutes from Forest app via Apple Health)
  - Total hours stat with target (14 hrs/week)
  - Bootstrap progress bar
  - Daily study bar chart

Right panel: Dreaming Spanish placeholder (built in Module 6).
"""

import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc

from modules import apple_health

STUDY_TARGET_HRS = 14.0
CHART_PAPER_BG = "rgba(0,0,0,0)"
CHART_PLOT_BG = "rgba(0,0,0,0)"
CHART_FONT_COLOR = "#8b949e"
CHART_GRID_COLOR = "#21262d"
COLOR_PURPLE = "#bc8cff"


def _study_chart(df):
    """Daily study hours bar chart."""
    fig = go.Figure(go.Bar(
        x=df["date"],
        y=df["study_hours"],
        marker_color=COLOR_PURPLE,
        marker_opacity=0.8,
        hovertemplate="%{x|%a %-d}: %{y:.1f} hrs<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor=CHART_PAPER_BG,
        plot_bgcolor=CHART_PLOT_BG,
        margin={"t": 6, "b": 28, "l": 38, "r": 8},
        font={"color": CHART_FONT_COLOR, "size": 11},
        showlegend=False,
        height=120,
        xaxis={"gridcolor": CHART_GRID_COLOR, "showgrid": False, "tickformat": "%a"},
        yaxis={"gridcolor": CHART_GRID_COLOR, "ticksuffix": " h"},
        bargap=0.3,
    )
    return fig


def _study_panel(data_dir):
    """Left panel: study hours from Apple Health mindfulness data."""
    df = apple_health.get_study_hours(data_dir, days=7)

    total_hrs = df["study_hours"].sum()
    pct = min(int(total_hrs / STUDY_TARGET_HRS * 100), 100)
    bar_color = "success" if pct >= 100 else ("warning" if pct >= 70 else "info")
    total_color = "#3fb950" if pct >= 100 else ("#d29922" if pct >= 70 else COLOR_PURPLE)

    has_data = total_hrs > 0

    return html.Div([
        html.Div([
            html.Span(f"{total_hrs:.1f}",
                      style={"fontSize": "2rem", "fontWeight": "700",
                             "color": total_color}),
            html.Span(f" / {STUDY_TARGET_HRS:.0f} hrs this week",
                      style={"fontSize": "0.85rem", "color": "#8b949e",
                             "marginLeft": "6px"}),
        ], className="mb-2"),
        dbc.Progress(value=pct, color=bar_color,
                     label=f"{pct}%",
                     style={"height": "18px", "borderRadius": "4px"},
                     className="mb-3"),
        dcc.Graph(figure=_study_chart(df), config={"displayModeBar": False})
        if has_data else html.P(
            "No study sessions recorded this week.",
            style={"color": "#484f58", "fontSize": "0.85rem", "textAlign": "center",
                   "padding": "1rem"},
        ),
    ])


def layout(data_dir):
    return dbc.Card([
        dbc.CardHeader(html.H5("Learning")),
        dbc.CardBody(
            dbc.Row([
                dbc.Col(_study_panel(data_dir), md=6),
                dbc.Col(
                    html.P(
                        "Dreaming Spanish -- DS module not yet connected.",
                        className="placeholder-msg",
                    ),
                    md=6,
                ),
            ])
        ),
    ])
