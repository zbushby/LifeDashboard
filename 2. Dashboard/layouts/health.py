"""Health module layout - body composition and calories (Apple Health).

Shows:
  - Stats row: current weight, body fat %, lean mass
  - Weight trend line chart (28 days) with 70 kg target line
  - Daily calories bar chart (7 days)

Calls modules/apple_health.py at render time (data read from disk).
Returns placeholder content if no data files exist yet.
"""

import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc

from modules import apple_health

# --- Visual constants ---
TARGET_WEIGHT_KG = 70.0
TARGET_BF_PCT = 12.0
CHART_PAPER_BG = "rgba(0,0,0,0)"
CHART_PLOT_BG = "rgba(0,0,0,0)"
CHART_FONT_COLOR = "#8b949e"
CHART_GRID_COLOR = "#21262d"
COLOR_BLUE = "#58a6ff"
COLOR_GREEN = "#3fb950"
COLOR_ORANGE = "#d29922"


def _stat_card(label, value, sub=None, color=None):
    """Small inline stat display: label / big number / optional subtext."""
    return html.Div([
        html.Div(label, style={"fontSize": "0.7rem", "color": "#8b949e",
                               "textTransform": "uppercase", "letterSpacing": "1px"}),
        html.Div(value, style={"fontSize": "1.6rem", "fontWeight": "700",
                               "color": color or "#e6edf3", "lineHeight": "1.2"}),
        html.Div(sub or "", style={"fontSize": "0.75rem", "color": "#8b949e"}),
    ], style={"textAlign": "center", "padding": "0.5rem 1rem"})


def _weight_chart(df_comp):
    """28-day weight trend line chart with 70 kg target dashed line."""
    mask = df_comp["weight_kg"].notna()
    fig = go.Figure()

    if mask.any():
        fig.add_trace(go.Scatter(
            x=df_comp.loc[mask, "date"],
            y=df_comp.loc[mask, "weight_kg"],
            mode="lines+markers",
            line={"color": COLOR_BLUE, "width": 2},
            marker={"size": 5, "color": COLOR_BLUE},
            name="Weight",
            hovertemplate="%{x|%d %b}: %{y:.1f} kg<extra></extra>",
        ))

    # Target line
    fig.add_hline(
        y=TARGET_WEIGHT_KG,
        line_dash="dash",
        line_color="#484f58",
        annotation_text=f"Target {TARGET_WEIGHT_KG} kg",
        annotation_font_color="#484f58",
        annotation_font_size=10,
    )

    fig.update_layout(
        paper_bgcolor=CHART_PAPER_BG,
        plot_bgcolor=CHART_PLOT_BG,
        margin={"t": 8, "b": 30, "l": 45, "r": 10},
        font={"color": CHART_FONT_COLOR, "size": 11},
        showlegend=False,
        height=160,
        xaxis={"gridcolor": CHART_GRID_COLOR, "showgrid": False,
               "tickformat": "%d %b", "nticks": 6},
        yaxis={"gridcolor": CHART_GRID_COLOR, "ticksuffix": " kg"},
    )
    return fig


def _calories_chart(df_cal):
    """7-day calories bar chart."""
    mask = df_cal["calories"].notna()
    fig = go.Figure()

    if mask.any():
        avg = df_cal.loc[mask, "calories"].mean()
        fig.add_trace(go.Bar(
            x=df_cal["date"],
            y=df_cal["calories"],
            marker_color=COLOR_GREEN,
            marker_opacity=0.8,
            hovertemplate="%{x|%d %b}: %{y:.0f} kcal<extra></extra>",
        ))
        fig.add_hline(
            y=avg,
            line_dash="dot",
            line_color="#484f58",
            annotation_text=f"Avg {avg:.0f}",
            annotation_font_color="#484f58",
            annotation_font_size=10,
        )

    fig.update_layout(
        paper_bgcolor=CHART_PAPER_BG,
        plot_bgcolor=CHART_PLOT_BG,
        margin={"t": 8, "b": 30, "l": 55, "r": 10},
        font={"color": CHART_FONT_COLOR, "size": 11},
        showlegend=False,
        height=130,
        xaxis={"gridcolor": CHART_GRID_COLOR, "showgrid": False,
               "tickformat": "%a %-d"},
        yaxis={"gridcolor": CHART_GRID_COLOR, "ticksuffix": " kcal"},
        bargap=0.3,
    )
    return fig


def layout(data_dir):
    df_comp = apple_health.get_body_composition(data_dir, days=28)
    df_cal = apple_health.get_calories(data_dir, days=7)

    # --- Current values (most recent non-NaN reading) ---
    has_data = df_comp["weight_kg"].notna().any()

    if not has_data:
        return dbc.Card([
            dbc.CardHeader(html.H5("Health")),
            dbc.CardBody(html.P(
                "Waiting for Apple Health data -- configure Health Auto Export on iPhone.",
                className="placeholder-msg",
            )),
        ])

    # Latest readings
    last_weight = df_comp.loc[df_comp["weight_kg"].notna(), "weight_kg"].iloc[-1]
    last_bf = df_comp.loc[df_comp["body_fat_pct"].notna(), "body_fat_pct"].iloc[-1] \
        if df_comp["body_fat_pct"].notna().any() else None
    last_lm = df_comp.loc[df_comp["lean_mass_kg"].notna(), "lean_mass_kg"].iloc[-1] \
        if df_comp["lean_mass_kg"].notna().any() else None

    # Colour-code vs targets
    w_color = COLOR_GREEN if last_weight <= TARGET_WEIGHT_KG + 0.5 else COLOR_ORANGE
    bf_color = (COLOR_GREEN if last_bf is not None and last_bf <= TARGET_BF_PCT
                else COLOR_ORANGE) if last_bf is not None else None

    stats_row = dbc.Row([
        dbc.Col(_stat_card("Weight", f"{last_weight:.1f} kg",
                           f"target {TARGET_WEIGHT_KG} kg", w_color), md=4),
        dbc.Col(_stat_card(
            "Body Fat",
            f"{last_bf:.1f}%" if last_bf is not None else "—",
            f"target <{TARGET_BF_PCT}%", bf_color,
        ), md=4),
        dbc.Col(_stat_card(
            "Lean Mass",
            f"{last_lm:.1f} kg" if last_lm is not None else "—",
        ), md=4),
    ], className="mb-2")

    return dbc.Card([
        dbc.CardHeader(html.H5("Health")),
        dbc.CardBody([
            stats_row,
            html.Div("Weight (28 days)", style={"fontSize": "0.7rem", "color": "#8b949e",
                                                 "textTransform": "uppercase",
                                                 "letterSpacing": "1px",
                                                 "marginBottom": "2px"}),
            dcc.Graph(figure=_weight_chart(df_comp), config={"displayModeBar": False}),
            html.Div("Calories this week", style={"fontSize": "0.7rem", "color": "#8b949e",
                                                   "textTransform": "uppercase",
                                                   "letterSpacing": "1px",
                                                   "marginTop": "8px",
                                                   "marginBottom": "2px"}),
            dcc.Graph(figure=_calories_chart(df_cal), config={"displayModeBar": False}),
        ]),
    ])
