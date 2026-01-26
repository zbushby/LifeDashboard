import colorsys
import datetime as dt
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    from streamlit_elements import dashboard, elements, html, mui, nivo
except Exception:
    st.error("Missing dependency: streamlit-elements. Install with: pip install streamlit-elements")
    st.stop()

APP_TITLE = "Life Dashboard"
DATA_DIR = Path(__file__).parent / "data"


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        st.error(f"Missing CSV: {path}")
        st.stop()
    return pd.read_csv(path)


def fmt_money(value: float) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value):,.0f}"


def week_to_date_bounds(reference_date: dt.date) -> tuple[dt.date, dt.date, dt.date, dt.date]:
    start = reference_date - dt.timedelta(days=reference_date.weekday())
    end = reference_date
    prev_start = start - dt.timedelta(days=7)
    prev_end = end - dt.timedelta(days=7)
    return start, end, prev_start, prev_end


def week_to_date_values(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    agg: str = "sum",
    reference_date: dt.date | None = None,
) -> tuple[float, float]:
    if df.empty or date_col not in df.columns or value_col not in df.columns:
        return 0.0, 0.0
    data = df.copy()
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce").dt.date
    data = data.dropna(subset=[date_col])
    if data.empty:
        return 0.0, 0.0
    ref = reference_date or dt.date.today()
    max_date = max(data[date_col])
    if max_date < ref:
        ref = max_date
    start, end, prev_start, prev_end = week_to_date_bounds(ref)
    data[value_col] = pd.to_numeric(data[value_col], errors="coerce")
    curr = data.loc[(data[date_col] >= start) & (data[date_col] <= end), value_col]
    prev = data.loc[(data[date_col] >= prev_start) & (data[date_col] <= prev_end), value_col]
    if agg == "mean":
        return float(curr.mean() or 0), float(prev.mean() or 0)
    if agg == "count_positive":
        return float((curr > 0).sum()), float((prev > 0).sum())
    return float(curr.sum() or 0), float(prev.sum() or 0)


def format_hours_minutes(hours: float) -> str:
    total_minutes = int(round(hours * 60))
    hrs = total_minutes // 60
    mins = total_minutes % 60
    if hrs and mins:
        return f"{hrs}h {mins}m"
    if hrs:
        return f"{hrs}h"
    return f"{mins}m"


def distinct_colors(count: int) -> list[str]:
    if count <= 0:
        return []

    def vdc(n: int, base: int = 2) -> float:
        vdc_value = 0.0
        denom = 1.0
        while n:
            n, remainder = divmod(n, base)
            denom *= base
            vdc_value += remainder / denom
        return vdc_value

    hues = [0.0] + [vdc(i) for i in range(1, count)]
    colors = []
    for hue in hues[:count]:
        r, g, b = colorsys.hls_to_rgb(hue, 0.55, 0.75)
        colors.append(f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}")
    return colors


def latest_snapshot(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    if date_col in df.columns:
        data = df.copy()
        data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
        data = data.dropna(subset=[date_col])
        if data.empty:
            return df.copy()
        latest_date = data[date_col].max()
        return data.loc[data[date_col] == latest_date].copy()
    return df.copy()


def pie_series(df: pd.DataFrame, label_col: str, value_col: str) -> list[dict]:
    if df.empty:
        return []
    labels = df[label_col].astype(str).tolist()
    values = pd.to_numeric(df[value_col], errors="coerce").fillna(0).tolist()
    colors = distinct_colors(len(labels))
    return [
        {"id": label, "label": label, "value": float(value), "color": color}
        for label, value, color in zip(labels, values, colors)
    ]


def progress_pie_data(value: float, total: float, color: str) -> list[dict]:
    if total <= 0:
        total = 1
    value = max(min(value, total), 0)
    return [
        {"id": "value", "value": float(value), "color": color},
        {"id": "remaining", "value": float(total - value), "color": "#e5e7eb"},
    ]


def line_series(series: pd.Series, name: str) -> list[dict]:
    data = []
    for idx, value in series.dropna().items():
        if isinstance(idx, pd.Timestamp):
            x_val = idx.strftime("%b %d")
        else:
            x_val = str(idx)
        data.append({"x": x_val, "y": float(value)})
    return [{"id": name, "data": data}]


def render_value_card(
    title: str,
    value: str,
    sub: str = "",
    change: str = "",
    change_color: str = "#16a34a",
    tone: str | None = None,
) -> None:
    bg = "#ffffff"
    border = "#e5e7eb"
    title_color = "#6b7280"
    sub_color = "#9ca3af"
    if tone == "spanish":
        bg = "#fffbe6"
        border = "#fdecc8"
        title_color = "#92400e"
        sub_color = "#b45309"
    if tone == "study":
        bg = "#f5f3ff"
        border = "#ddd6fe"
        title_color = "#5b21b6"
        sub_color = "#7c3aed"
    with mui.Paper(
        variant="outlined",
        sx={
            "p": 2,
            "textAlign": "center",
            "height": "100%",
            "backgroundColor": bg,
            "borderColor": border,
        },
    ):
        mui.Typography(title, sx={"fontSize": 12, "fontWeight": 700, "color": title_color})
        mui.Typography(value, sx={"fontSize": 24, "fontWeight": 700})
        if change:
            mui.Typography(change, sx={"fontSize": 14, "fontWeight": 600, "color": change_color})
        if sub:
            mui.Typography(sub, sx={"fontSize": 12, "color": sub_color})


def render_drag_card(
    key: str,
    title: str,
    value: str,
    sub: str = "",
    change: str = "",
    change_color: str = "#16a34a",
    tone: str | None = None,
) -> None:
    bg = "#ffffff"
    border = "#e5e7eb"
    title_color = "#6b7280"
    sub_color = "#9ca3af"
    if tone == "spanish":
        bg = "#fffbe6"
        border = "#fdecc8"
        title_color = "#92400e"
        sub_color = "#b45309"
    if tone == "study":
        bg = "#f5f3ff"
        border = "#ddd6fe"
        title_color = "#5b21b6"
        sub_color = "#7c3aed"
    with mui.Paper(
        key=key,
        variant="outlined",
        sx={
            "p": 2,
            "height": "100%",
            "backgroundColor": bg,
            "borderColor": border,
        },
    ):
        mui.Typography(
            title,
            className="drag-handle",
            sx={
                "fontSize": 12,
                "fontWeight": 700,
                "color": title_color,
                "textTransform": "uppercase",
                "letterSpacing": ".08em",
                "mb": 0.5,
            },
        )
        mui.Typography(value, sx={"fontSize": 24, "fontWeight": 700})
        if change:
            mui.Typography(change, sx={"fontSize": 14, "fontWeight": 600, "color": change_color})
        if sub:
            mui.Typography(sub, sx={"fontSize": 12, "color": sub_color})


def render_drag_donut_card(
    key: str,
    title: str,
    value: float,
    total: float,
    color: str,
    height: int = 200,
    inner_radius: float = 0.72,
) -> None:
    with mui.Paper(
        key=key,
        variant="outlined",
        sx={
            "p": 2,
            "height": "100%",
            "borderColor": "#e5e7eb",
        },
    ):
        mui.Typography(
            title,
            className="drag-handle",
            sx={
                "fontSize": 12,
                "fontWeight": 700,
                "color": "#6b7280",
                "textTransform": "uppercase",
                "letterSpacing": ".08em",
                "mb": 0.5,
            },
        )
        render_donut(
            progress_pie_data(value, total, color),
            height=height,
            inner_radius=inner_radius,
            center_text=f"{int(value)} / {int(total)}",
            center_font_size=20,
        )


def render_donut(
    data: list[dict],
    height: int = 200,
    inner_radius: float = 0.6,
    center_text: str = "",
    center_font_size: int = 18,
) -> None:
    with html.div(style={"position": "relative", "height": f"{height}px"}):
        nivo.Pie(
            data=data,
            margin={"top": 10, "right": 10, "bottom": 10, "left": 10},
            innerRadius=inner_radius,
            padAngle=1,
            cornerRadius=3,
            colors={"datum": "data.color"},
            enableArcLabels=False,
            enableArcLinkLabels=False,
            isInteractive=False,
        )
        if center_text:
            html.div(
                center_text,
                style={
                    "position": "absolute",
                    "top": "50%",
                    "left": "50%",
                    "transform": "translate(-50%, -50%)",
                    "fontSize": f"{center_font_size}px",
                    "fontWeight": 700,
                    "color": "#111827",
                },
            )


def render_line(data: list[dict], height: int = 240) -> None:
    with html.div(style={"height": f"{height}px"}):
        nivo.Line(
            data=data,
            margin={"top": 10, "right": 20, "bottom": 40, "left": 50},
            xScale={"type": "point"},
            yScale={"type": "linear", "min": "auto", "max": "auto", "stacked": False},
            axisBottom={"tickRotation": -45},
            axisLeft={"tickSize": 5, "tickPadding": 5, "tickRotation": 0},
            enablePoints=False,
            useMesh=True,
        )


def github_heatmap_html(df: pd.DataFrame, date_col: str, value_col: str) -> str:
    data = df.copy()
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce").dt.date
    data = data.dropna(subset=[date_col])
    data[value_col] = pd.to_numeric(data[value_col], errors="coerce").fillna(0)
    if data.empty:
        return ""

    end = max(data[date_col])
    start = max(min(data[date_col]), end - dt.timedelta(days=364))
    start = start - dt.timedelta(days=start.weekday())
    end = end + dt.timedelta(days=(6 - end.weekday()))

    values = {row[date_col]: row[value_col] for _, row in data.iterrows()}
    non_zero = [v for v in values.values() if v > 0]
    if non_zero:
        q1 = pd.Series(non_zero).quantile(0.25)
        q2 = pd.Series(non_zero).quantile(0.5)
        q3 = pd.Series(non_zero).quantile(0.75)
    else:
        q1 = q2 = q3 = 0

    def level(val: float) -> int:
        if val <= 0:
            return 0
        if val <= q1:
            return 1
        if val <= q2:
            return 2
        if val <= q3:
            return 3
        return 4

    cells = []
    week_starts = []
    week_start = start
    while week_start <= end:
        week_starts.append(week_start)
        for dow in range(7):
            day = week_start + dt.timedelta(days=dow)
            val = values.get(day, 0)
            lvl = level(val) if start <= day <= end else 0
            title = f"{day.isoformat()}: {val:.2f}"
            cells.append(f'<div class="heatmap-cell lvl-{lvl}" title="{title}"></div>')
        week_start += dt.timedelta(weeks=1)

    month_labels = []
    for ws in week_starts:
        label = ""
        for i in range(7):
            day = ws + dt.timedelta(days=i)
            if day.day == 1:
                label = day.strftime("%b")
                break
        month_labels.append(label)

    month_html = "".join(
        f'<div class="heatmap-month">{label}</div>' for label in month_labels
    )
    day_labels = ["Mon", "", "Wed", "", "Fri", "", ""]
    day_html = "".join(f'<div class="heatmap-day">{lbl}</div>' for lbl in day_labels)

    cols = len(week_starts)
    cells_html = "".join(cells)
    return (
        f'<div class="heatmap-wrap" style="--cols:{cols};">'
        f'<div class="heatmap-months">{month_html}</div>'
        f'<div class="heatmap-body">'
        f'<div class="heatmap-days">{day_html}</div>'
        f'<div class="heatmap-grid" style="aspect-ratio:{cols} / 7;">{cells_html}</div>'
        f"</div>"
        f'<div class="heatmap-legend">'
        f"<span>Less</span>"
        f'<div class="legend-cell lvl-0"></div>'
        f'<div class="legend-cell lvl-1"></div>'
        f'<div class="legend-cell lvl-2"></div>'
        f'<div class="legend-cell lvl-3"></div>'
        f'<div class="legend-cell lvl-4"></div>'
        f"<span>More</span>"
        f"</div>"
        f"</div>"
    )


def card(
    title: str,
    value: str,
    sub: str = "",
    change: str = "",
    change_class: str = "",
    tone_class: str = "",
) -> None:
    st.markdown(
        f"""
        <div class="card {tone_class}">
          <div class="card-title">{title}</div>
          <div class="card-value">{value}</div>
          <div class="card-change {change_class}">{change}</div>
          <div class="card-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stat_bubble(
    title: str,
    value: str,
    sub: str = "",
    change: str = "",
    change_class: str = "",
    tone_class: str = "",
) -> None:
    st.markdown(
        f"""
        <div class="stat-bubble {tone_class}">
          <div class="stat-title">{title}</div>
          <div class="stat-value">{value}</div>
          <div class="stat-change {change_class}">{change}</div>
          <div class="stat-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def weather_icon(summary: str) -> str:
    mapping = {
        "Clear": "☀️",
        "Sunny": "☀️",
        "Cloudy": "☁️",
        "Rain": "🌧️",
        "Windy": "💨",
        "Fog": "🌫️",
    }
    return mapping.get(summary, "⛅")


def donut_progress(
    value: float,
    goal: float,
    color: str,
    height: int = 140,
    hole: float = 0.55,
    center_text: str | None = None,
    center_font_size: int = 16,
) -> go.Figure:
    if not goal or goal <= 0:
        st.error("Invalid goal value in CSV.")
        st.stop()
    value = max(min(value, goal), 0)
    fig = go.Figure(
        data=[
            go.Pie(
                values=[value, max(goal - value, 0)],
                hole=hole,
                marker=dict(colors=[color, "#e5e7eb"]),
                textinfo="none",
                hovertemplate="Value: %{value}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=height,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[
            dict(
                text=center_text if center_text is not None else f"{int(value)} / {int(goal)}",
                x=0.5,
                y=0.5,
                font_size=center_font_size,
                showarrow=False,
            )
        ],
    )
    return fig


def expense_pie(
    df: pd.DataFrame,
    height: int = 140,
) -> go.Figure:
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            height=height,
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            annotations=[
                dict(
                    text="No data",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=12, color="#6b7280"),
                )
            ],
        )
        return fig
    colors = distinct_colors(len(df))
    fig = go.Figure(
        data=[
            go.Pie(
                labels=df["item"],
                values=df["amount"],
                hole=0.55,
                marker=dict(colors=colors),
                hovertemplate="%{label}: %{value:$,.0f}<extra></extra>",
                textinfo="none",
            )
        ]
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=height,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def get_goal(goals_df: pd.DataFrame, metric: str) -> float:
    match = goals_df.loc[goals_df["metric"] == metric, "weekly_goal"]
    if match.empty:
        st.error(f"Missing weekly goal for '{metric}' in weekly_goals.csv")
        st.stop()
    return float(match.iloc[0])


def goal_card(title: str, heatmap_html: str) -> None:
    st.markdown(
        f"""
        <div class="card tone-goals">
          <div class="card-title">{title}</div>
          {heatmap_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def chart_card(title: str, fig: go.Figure, footer: str = "", key: str | None = None) -> None:
    with st.container(border=True):
        st.markdown(
            f'<div class="chart-card-title">{title}</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
            key=key,
            config={"displayModeBar": False},
        )
        if footer:
            st.markdown(
                f'<div class="chart-card-footer">{footer}</div>',
                unsafe_allow_html=True,
            )


def birthdays_reminders_section(birthdays_df: pd.DataFrame, reminders_df: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">Upcoming (Next 7 Days) & Reminders</div>', unsafe_allow_html=True)
    birthdays_df = birthdays_df.copy()
    birthdays_df["date"] = pd.to_datetime(birthdays_df["date"])
    today_dt = pd.Timestamp.today().normalize()
    end_dt = today_dt + pd.Timedelta(days=7)
    next_dates = []
    for _, row in birthdays_df.iterrows():
        date = row["date"]
        next_date = date.replace(year=today_dt.year)
        if next_date < today_dt:
            next_date = next_date.replace(year=today_dt.year + 1)
        next_dates.append(next_date)
    birthdays_df["next_date"] = next_dates
    birthdays_df = birthdays_df[
        (birthdays_df["next_date"] >= today_dt) & (birthdays_df["next_date"] <= end_dt)
    ].sort_values("next_date")

    left, right = st.columns(2)
    with left:
        items = []
        for _, row in birthdays_df.iterrows():
            date_str = row["next_date"].strftime("%b %d, %Y")
            items.append(
                f'<div class="birthday-item"><span>{row["name"]}</span><span class="birthday-date">{date_str}</span></div>'
            )
        empty_birthday = '<div class="birthday-item">No upcoming days in next 7 days</div>'
        birthday_items_html = "".join(items) if items else empty_birthday
        list_html = (
            '<div class="list-card">'
            '<div class="list-title">🎂 Upcoming Birthdays & Days</div>'
            f'<div class="birthday-list">{birthday_items_html}</div>'
            "</div>"
        )
        st.markdown(list_html, unsafe_allow_html=True)

    with right:
        reminder_items = []
        if not reminders_df.empty and "item" in reminders_df.columns:
            for _, row in reminders_df.iterrows():
                reminder_items.append(
                    f'<div class="reminder-item"><span>{row["item"]}</span></div>'
                )
        empty_reminder = '<div class="reminder-item">No reminders yet</div>'
        reminder_items_html = "".join(reminder_items) if reminder_items else empty_reminder
        reminder_html = (
            '<div class="list-card">'
            '<div class="list-title">💡 Reminders</div>'
            f'<div class="reminder-list">{reminder_items_html}</div>'
            "</div>"
        )
        st.markdown(reminder_html, unsafe_allow_html=True)


st.set_page_config(page_title=APP_TITLE, layout="wide")

st.markdown(
    """
    <style>
    .app-bg { background: #f6f6f6; }
    .block-container { padding-top: 0.6rem; padding-bottom: 0.8rem; max-width: 100%; padding-left: 1rem; padding-right: 1rem; }
    .element-container { margin-bottom: 6px; }
    div[data-testid="stVerticalBlock"] > div { gap: 6px; }
    body { background: #f7f5f2; }
    .welcome {
      font-size: 24px;
      font-weight: 700;
      margin-top: -2px;
      margin-bottom: 4px;
      color: #111827;
    }
    .card {
      background: #ffffff;
      border: 1px solid #ededed;
      border-radius: 16px;
      padding: 10px;
      box-shadow: 0 4px 14px rgba(0,0,0,0.05);
      height: 100%;
    }
    .card { text-align: center; }
    .drag-handle {
      cursor: grab;
      user-select: none;
    }
    .drag-handle:active {
      cursor: grabbing;
    }
    .card-title { color: #6b7280; font-size: 14px; text-transform: uppercase; letter-spacing: .08em; }
    .card-value { font-size: 28px; font-weight: 700; color: #111827; margin-top: 3px; }
    .card-sub { font-size: 13px; color: #9ca3af; margin-top: 2px; }
    .section-title { font-size: 20px; font-weight: 700; margin: 12px 0 8px 0; text-align: center; }
    .weather-mini { text-align: center; padding: 6px 4px; border-radius: 10px; }
    .weather-day { font-size: 16px; color: #6b7280; }
    .weather-icon { font-size: 44px; margin: 6px 0; }
    .weather-temp { font-size: 17px; color: #111827; font-weight: 600; }
    .card-change { font-size: 15px; margin-top: 6px; font-weight: 600; }
    .change-pos { color: #16a34a; }
    .change-neg { color: #dc2626; }
    .tone-finance { border-top: 3px solid #2563eb; }
    .tone-health { border-top: 3px solid #10b981; background: #f2fbf7; }
    .tone-study { border-top: 3px solid #8b5cf6; background: #f5f3ff; border: 1px solid #ddd6fe; }
    .tone-spanish { border-top: 3px solid #f59e0b; background: #fffbe6; border: 1px solid #fdecc8; }
    .tone-goals { border-top: 3px solid #8b5cf6; background: #f5f3ff; }
    .tone-weather { border-top: 3px solid #0ea5e9; background: #f0f9ff; }
    .tone-finance { background: #eff6ff; }
    .heatmap-wrap { background: #ffffff; border: 1px solid #ededed; border-radius: 12px; padding: 6px 8px; width: 100%; }
    .heatmap-months { display: grid; gap: 2px; margin-left: 26px; margin-bottom: 4px; grid-template-columns: repeat(var(--cols), 1fr); }
    .heatmap-month { font-size: 11px; color: #6b7280; white-space: nowrap; }
    .heatmap-body { display: flex; gap: 6px; align-items: stretch; }
    .heatmap-days { display: grid; grid-template-rows: repeat(7, 1fr); gap: 2px; margin-top: 1px; }
    .heatmap-day { font-size: 10px; color: #6b7280; line-height: 1; }
    .heatmap-grid {
      display: grid;
      grid-auto-flow: column;
      grid-template-columns: repeat(var(--cols), 1fr);
      grid-template-rows: repeat(7, 1fr);
      gap: 2px;
      padding: 2px 2px;
      width: 100%;
    }
    .heatmap-cell { width: 100%; aspect-ratio: 1 / 1; border-radius: 3px; }
    .heatmap-legend { display: flex; align-items: center; gap: 6px; margin-top: 4px; font-size: 10px; color: #6b7280; }
    .legend-cell { width: 10px; height: 10px; border-radius: 3px; }
    .lvl-0 { background: #ebedf0; }
    .lvl-1 { background: #c6e48b; }
    .lvl-2 { background: #7bc96f; }
    .lvl-3 { background: #239a3b; }
    .lvl-4 { background: #196127; }
    .list-card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 16px; padding: 12px; text-align: left; }
    .list-title { font-size: 16px; font-weight: 700; color: #111827; margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
    .birthday-list, .reminder-list { display: grid; gap: 8px; }
    .birthday-item, .reminder-item {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      font-size: 16px;
      padding: 10px 12px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      font-weight: 600;
    }
    .birthday-date, .reminder-date { color: #6b7280; font-weight: 500; }
    .spanish-panel { padding: 12px 14px; }
    .spanish-title { font-size: 20px; font-weight: 700; margin-bottom: 8px; color: #92400e; background: #fffbe6; padding: 10px 12px; border-radius: 10px; text-align: center; }
    .study-title { font-size: 20px; font-weight: 700; margin-bottom: 8px; color: #5b21b6; background: #f5f3ff; padding: 10px 12px; border-radius: 10px; text-align: center; }
    .stat-bubble { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 16px; padding: 16px; text-align: center; min-height: 94px; }
    .stat-bubble.spanish { background: #fffbe6; border-color: #fdecc8; }
    .stat-bubble.study { background: #f5f3ff; border-color: #ddd6fe; }
    .stat-title { font-size: 12px; text-transform: uppercase; letter-spacing: .08em; color: #6b7280; }
    .stat-bubble.spanish .stat-title { color: #92400e; }
    .stat-bubble.study .stat-title { color: #5b21b6; }
    .stat-value { font-size: 24px; font-weight: 700; color: #111827; margin-top: 4px; }
    .stat-change { font-size: 14px; margin-top: 6px; font-weight: 600; }
    .stat-sub { font-size: 13px; color: #6b7280; margin-top: 4px; }
    .stat-bubble.spanish .stat-sub { color: #b45309; }
    .stat-bubble.study .stat-sub { color: #7c3aed; }
    .day-bubble { background: #fef3c7; border: 1px solid #fcd34d; border-radius: 14px; padding: 8px 6px 8px 6px; text-align: center; }
    .day-label { font-size: 11px; font-weight: 600; color: #92400e; margin-bottom: 2px; }
    .chart-card-title { font-size: 20px; font-weight: 700; color: #0f172a; margin-bottom: 8px; text-align: center; }
    .chart-card-footer { font-size: 16px; font-weight: 700; color: #0f172a; text-align: center; margin-top: 8px; padding-top: 10px; border-top: 1px solid #e5e7eb; }
    .wtd-banner { font-size: 14px; font-weight: 600; text-align: center; color: #6b7280; margin-top: -2px; margin-bottom: 6px; }
    .page-spacer { height: 560px; }
    </style>
    """,
    unsafe_allow_html=True,
)

finance = load_csv(DATA_DIR / "finance_weekly.csv")
net_worth = load_csv(DATA_DIR / "net_worth.csv")
sleep = load_csv(DATA_DIR / "sleep_daily.csv")
weight = load_csv(DATA_DIR / "weight_daily.csv")
gym = load_csv(DATA_DIR / "gym_daily.csv")
study = load_csv(DATA_DIR / "study_daily.csv")
dreaming = load_csv(DATA_DIR / "dreaming_spanish_daily.csv")
weather = load_csv(DATA_DIR / "weather_daily.csv")
calories = load_csv(DATA_DIR / "calories_daily.csv")
expenses_eat = load_csv(DATA_DIR / "expenses_eating_out.csv")
expenses_ent = load_csv(DATA_DIR / "expenses_entertainment.csv")
net_alloc = load_csv(DATA_DIR / "net_worth_allocations.csv")
birthdays = load_csv(DATA_DIR / "birthdays.csv")
weekly_goals = load_csv(DATA_DIR / "weekly_goals.csv")
profile = load_csv(DATA_DIR / "profile.csv")
reminders_path = DATA_DIR / "reminders.csv"
if reminders_path.exists():
    reminders = load_csv(reminders_path)
else:
    reminders = pd.DataFrame(columns=["item"])
body_comp_path = DATA_DIR / "body_comp_daily.csv"
if body_comp_path.exists():
    body_comp = load_csv(body_comp_path)
else:
    body_comp = pd.DataFrame(columns=["date", "body_fat", "muscle"])

st.title(APP_TITLE)
today = dt.date.today()
name = profile["name"].iloc[0] if "name" in profile.columns else ""
if not name:
    st.error("Missing name in profile.csv")
    st.stop()
st.markdown(
    f'<div class="welcome">Welcome {name}, it&#39;s {today.strftime("%A")} - {today.strftime("%B %d, %Y")}</div>',
    unsafe_allow_html=True,
)
st.caption("One-page dashboard. Replace CSVs in the data folder with real data anytime.")

data_ref_date = today - dt.timedelta(days=1)
start_wtd, end_wtd, _, _ = week_to_date_bounds(data_ref_date)
st.markdown(
    f'<div class="wtd-banner">{start_wtd.strftime("%A %b %d, %Y")} - {end_wtd.strftime("%A %b %d, %Y")} (data through {data_ref_date.strftime("%A %b %d, %Y")})</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="section-title">Drag & Drop Overview</div>', unsafe_allow_html=True)
st.caption("Drag cards by their titles to rearrange.")

finance["week_start"] = pd.to_datetime(finance["week_start"])
finance_sorted = finance.sort_values("week_start")
last_week = finance_sorted.iloc[-1]
prev_week = finance_sorted.iloc[-2] if len(finance_sorted) > 1 else last_week
spend_delta = last_week["actual"] - prev_week["actual"]
spend_pct = (spend_delta / prev_week["actual"] * 100) if prev_week["actual"] else 0
spend_change = f"{spend_pct:+.2f}% vs last week"
spend_color = "#dc2626" if spend_delta > 0 else "#16a34a"

net_worth["date"] = pd.to_datetime(net_worth["date"])
net_sorted = net_worth.sort_values("date")
net_week = net_sorted.set_index("date")["value"].resample("W").mean()
net_last = net_week.iloc[-1]
net_prev = net_week.iloc[-2] if len(net_week) > 1 else net_last
net_delta = net_last - net_prev
net_pct = (net_delta / net_prev * 100) if net_prev else 0
net_change = f"{fmt_money(net_delta)} ({net_pct:+.2f}%)"
net_color = "#16a34a" if net_delta >= 0 else "#dc2626"

sleep["date"] = pd.to_datetime(sleep["date"])
weight["date"] = pd.to_datetime(weight["date"])
gym["date"] = pd.to_datetime(gym["date"])
sleep_avg, sleep_prev = week_to_date_values(
    sleep, "date", "hours", agg="mean", reference_date=data_ref_date
)
sleep_delta = sleep_avg - sleep_prev
sleep_pct = (sleep_delta / sleep_prev * 100) if sleep_prev else 0
sleep_change = f"{sleep_delta:+.1f} ({sleep_pct:+.2f}%)"
sleep_color = "#16a34a" if sleep_delta >= 0 else "#dc2626"

weight_avg, weight_prev = week_to_date_values(
    weight, "date", "weight", agg="mean", reference_date=data_ref_date
)
weight_delta = weight_avg - weight_prev
weight_pct = (weight_delta / weight_prev * 100) if weight_prev else 0
weight_change = f"{weight_delta:+.1f} ({weight_pct:+.2f}%)"
weight_color = "#dc2626" if weight_delta > 0 else "#16a34a"

if (DATA_DIR / "bjj_daily.csv").exists():
    bjj = load_csv(DATA_DIR / "bjj_daily.csv")
    bjj["date"] = pd.to_datetime(bjj["date"])
else:
    bjj = pd.DataFrame(columns=["date", "sessions"])

gym_sessions, _ = week_to_date_values(
    gym, "date", "minutes", agg="count_positive", reference_date=data_ref_date
)
bjj_sessions, _ = (
    week_to_date_values(
        bjj, "date", "sessions", agg="count_positive", reference_date=data_ref_date
    )
    if not bjj.empty
    else (0, 0)
)
g_goal = get_goal(weekly_goals, "gym_sessions")
b_goal = get_goal(weekly_goals, "bjj_sessions")

overview_layout = [
    dashboard.Item("weekly_spend", 0, 0, 3, 2),
    dashboard.Item("net_worth", 3, 0, 3, 2),
    dashboard.Item("sleep_avg", 6, 0, 3, 2),
    dashboard.Item("weight_avg", 9, 0, 3, 2),
    dashboard.Item("gym_sessions", 0, 2, 6, 3),
    dashboard.Item("bjj_sessions", 6, 2, 6, 3),
]

with elements("overview"):
    with dashboard.Grid(
        overview_layout,
        cols=12,
        rowHeight=70,
        margin=[8, 8],
        draggableHandle=".drag-handle",
    ):
        render_drag_card(
            "weekly_spend",
            "Weekly Spend",
            f"{fmt_money(last_week['actual'])} / {fmt_money(last_week['budget'])}",
            "This week",
            spend_change,
            spend_color,
        )
        render_drag_card(
            "net_worth",
            "Net Worth",
            fmt_money(net_last),
            "vs last week",
            net_change,
            net_color,
        )
        render_drag_card(
            "sleep_avg",
            "Sleep Avg (WTD)",
            f"{sleep_avg:.1f} hrs",
            "Week to date",
            sleep_change,
            sleep_color,
        )
        render_drag_card(
            "weight_avg",
            "Weight (WTD Avg)",
            f"{weight_avg:.1f} kg",
            "Week to date",
            weight_change,
            weight_color,
        )
        render_drag_donut_card(
            "gym_sessions",
            "Gym Sessions",
            gym_sessions,
            g_goal,
            "#10b981",
            height=200,
        )
        render_drag_donut_card(
            "bjj_sessions",
            "BJJ Sessions",
            bjj_sessions,
            b_goal,
            "#22c55e",
            height=200,
        )

birthdays_reminders_section(birthdays, reminders)

st.markdown('<div class="section-title">Weather</div>', unsafe_allow_html=True)
weather["date"] = pd.to_datetime(weather["date"])
weather_sorted = weather.sort_values("date").tail(7)
cols = st.columns(7)
for idx, (_, row) in enumerate(weather_sorted.iterrows()):
    high_c = int(round(row["high"]))
    low_c = int(round(row["low"]))
    with cols[idx]:
        st.markdown(
            f"""
            <div class="card tone-weather weather-mini">
              <div class="weather-day">{row['date'].strftime('%a')}</div>
              <div class="weather-icon">{weather_icon(row['summary'])}</div>
              <div class="weather-temp">{high_c} C / {low_c} C</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown('<div class="section-title">Finance</div>', unsafe_allow_html=True)
finance["week_start"] = pd.to_datetime(finance["week_start"])
finance["delta"] = finance["actual"] - finance["budget"]
finance_sorted = finance.sort_values("week_start")
last_week = finance_sorted.iloc[-1]
prev_week = finance_sorted.iloc[-2] if len(finance_sorted) > 1 else last_week
net_delta = last_week["actual"] - prev_week["actual"]
net_pct = (net_delta / prev_week["actual"] * 100) if prev_week["actual"] else 0

col1, col2 = st.columns(2)
with col1:
    delta = last_week["actual"] - prev_week["actual"]
    pct = (delta / prev_week["actual"] * 100) if prev_week["actual"] else 0
    change = f"{pct:+.2f}% vs last week"
    change_class = "change-neg" if delta > 0 else "change-pos"
    card(
        "Weekly Spend",
        f"{fmt_money(last_week['actual'])} / {fmt_money(last_week['budget'])}",
        "This week",
        change,
        change_class,
        "tone-finance",
    )
with col2:
    net_worth["date"] = pd.to_datetime(net_worth["date"])
    net_sorted = net_worth.sort_values("date")
    net_week = net_sorted.set_index("date")["value"].resample("W").mean()
    net_last = net_week.iloc[-1]
    net_prev = net_week.iloc[-2] if len(net_week) > 1 else net_last
    net_delta = net_last - net_prev
    net_pct = (net_delta / net_prev * 100) if net_prev else 0
    change = f"{fmt_money(net_delta)} ({net_pct:+.2f}%)"
    change_class = "change-pos" if net_delta >= 0 else "change-neg"
    card(
        "Net Worth",
        fmt_money(net_last),
        "vs last week",
        change,
        change_class,
        "tone-finance",
    )

PIE_HEIGHT = 160
net_pie = go.Figure(
    data=[
        go.Pie(
            labels=net_alloc["asset"],
            values=net_alloc["amount"],
            hole=0.55,
            marker=dict(colors=distinct_colors(len(net_alloc))),
            hovertemplate="%{label}: %{value:$,.0f}<extra></extra>",
            textinfo="none",
        )
    ]
)
net_pie.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    height=PIE_HEIGHT,
    showlegend=False,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)

eat_total = float(expenses_eat["amount"].sum())
ent_total = float(expenses_ent["amount"].sum())
weekly_budget = float(last_week["budget"])
net_total = float(net_alloc["amount"].sum())
eat_footer = f"{fmt_money(eat_total)} / {fmt_money(weekly_budget)}"
ent_footer = f"{fmt_money(ent_total)} / {fmt_money(weekly_budget)}"
net_footer = f"Total {fmt_money(net_total)}"

eat_pie = expense_pie(expenses_eat, height=PIE_HEIGHT)
ent_pie = expense_pie(expenses_ent, height=PIE_HEIGHT)

p1, p2, p3 = st.columns(3)
with p1:
    chart_card("Net Worth Allocation", net_pie, net_footer, key="net_worth_pie")
with p2:
    chart_card("Eating / Drinking Out", eat_pie, eat_footer, key="eat_pie")
with p3:
    chart_card("Entertainment", ent_pie, ent_footer, key="ent_pie")

st.markdown('<div class="section-title">Health</div>', unsafe_allow_html=True)
sleep["date"] = pd.to_datetime(sleep["date"])
weight["date"] = pd.to_datetime(weight["date"])
gym["date"] = pd.to_datetime(gym["date"])
calories["date"] = pd.to_datetime(calories["date"])
if not body_comp.empty:
    body_comp["date"] = pd.to_datetime(body_comp["date"])
weight_weekly = weight.set_index("date")["weight"].resample("W").mean()
gym_weekly = gym.set_index("date")[["minutes", "volume"]].resample("W").sum()

col1, col2, col3, col4 = st.columns(4)
with col1:
    last7, prev7 = week_to_date_values(
        sleep, "date", "hours", agg="mean", reference_date=data_ref_date
    )
    delta = last7 - prev7
    pct = (delta / prev7 * 100) if prev7 else 0
    change = f"{delta:+.1f} ({pct:+.2f}%)"
    change_class = "change-pos" if delta >= 0 else "change-neg"
    card(
        "Sleep Avg (WTD)",
        f"{last7:.1f} hrs",
        "Week to date",
        change,
        change_class,
        "tone-health",
    )
with col2:
    last, prev = week_to_date_values(
        weight, "date", "weight", agg="mean", reference_date=data_ref_date
    )
    delta = last - prev
    pct = (delta / prev * 100) if prev else 0
    change = f"{delta:+.1f} ({pct:+.2f}%)"
    change_class = "change-neg" if delta > 0 else "change-pos"
    card(
        "Weight (WTD Avg)",
        f"{last:.1f} kg",
        "Week to date",
        change,
        change_class,
        "tone-health",
    )
with col3:
    cal_sorted = calories.sort_values("date")
    cal_last = cal_sorted.iloc[-1]
    cal_prev = cal_sorted.iloc[-2] if len(cal_sorted) > 1 else cal_last
    surplus = cal_last["intake"] - cal_last["goal"]
    prev_surplus = cal_prev["intake"] - cal_prev["goal"]
    delta = surplus - prev_surplus
    pct = (delta / prev_surplus * 100) if prev_surplus else 0
    change = f"{delta:+.0f} ({pct:+.2f}%)"
    change_class = "change-pos" if delta >= 0 else "change-neg"
    status = "Surplus" if surplus >= 0 else "Deficit"
    card(
        f"Calories ({status})",
        f"{surplus:+.0f} kcal",
        "Yesterday",
        change,
        change_class,
        "tone-health",
    )
with col4:
    last, prev = week_to_date_values(
        gym, "date", "volume", agg="sum", reference_date=data_ref_date
    )
    delta = last - prev
    pct = (delta / prev * 100) if prev else 0
    change = f"{delta:+,} ({pct:+.2f}%)"
    change_class = "change-pos" if delta >= 0 else "change-neg"
    card(
        "Gym Volume (WTD)",
        f"{int(last):,}",
        "Week to date",
        change,
        change_class,
        "tone-health",
    )

st.markdown('<div class="section-title">Exercise</div>', unsafe_allow_html=True)
gym_sessions, prev_gym_sessions = week_to_date_values(
    gym, "date", "minutes", agg="count_positive", reference_date=data_ref_date
)
bjj_sessions, prev_bjj_sessions = (
    week_to_date_values(
        bjj, "date", "sessions", agg="count_positive", reference_date=data_ref_date
    )
    if not bjj.empty
    else (0, 0)
)
g_goal = get_goal(weekly_goals, "gym_sessions")
b_goal = get_goal(weekly_goals, "bjj_sessions")

g1, g2 = st.columns(2)
with g1:
    chart_card(
        "Gym Sessions",
        donut_progress(
            gym_sessions,
            g_goal,
            "#10b981",
            height=200,
            hole=0.55,
            center_font_size=22,
        ),
        key="gym_donut",
    )
with g2:
    chart_card(
        "BJJ Sessions",
        donut_progress(
            bjj_sessions,
            b_goal,
            "#22c55e",
            height=200,
            hole=0.55,
            center_font_size=22,
        ),
        key="bjj_donut",
    )

st.markdown('<div class="section-title">Body Composition (Weekly Avg)</div>', unsafe_allow_html=True)
body_cols = st.columns(3)
with body_cols[0]:
    with st.container(border=True):
        st.markdown('<div class="chart-card-title">Weight</div>', unsafe_allow_html=True)
        st.line_chart(weight_weekly.tail(26))
with body_cols[1]:
    with st.container(border=True):
        st.markdown('<div class="chart-card-title">Body Fat %</div>', unsafe_allow_html=True)
        if body_comp.empty or "body_fat" not in body_comp.columns:
            st.info("Add data/body_comp_daily.csv with columns: date, body_fat, muscle")
        else:
            body_fat_weekly = (
                body_comp.set_index("date")["body_fat"].resample("W").mean()
            )
            st.line_chart(body_fat_weekly.tail(26))
with body_cols[2]:
    with st.container(border=True):
        st.markdown('<div class="chart-card-title">Muscle %</div>', unsafe_allow_html=True)
        if body_comp.empty or "muscle" not in body_comp.columns:
            st.info("Add data/body_comp_daily.csv with columns: date, body_fat, muscle")
        else:
            muscle_weekly = (
                body_comp.set_index("date")["muscle"].resample("W").mean()
            )
            st.line_chart(muscle_weekly.tail(26))


st.markdown('<div class="section-title">Study</div>', unsafe_allow_html=True)
study["date"] = pd.to_datetime(study["date"])
study_recent = study[study["date"].dt.date <= data_ref_date].copy()
study_year_start = dt.date(data_ref_date.year, 1, 1)
study_year_total = float(
    study_recent.loc[study_recent["date"].dt.date >= study_year_start, "hours"].sum()
)
study_week, study_prev_week = week_to_date_values(
    study_recent, "date", "hours", agg="sum", reference_date=data_ref_date
)
study_goal_match = weekly_goals.loc[weekly_goals["metric"] == "study_hours", "weekly_goal"]
study_goal = float(study_goal_match.iloc[0]) if not study_goal_match.empty else 20.0
study_goal_met = study_week >= study_goal
study_goal_text = "Yes 🙂" if study_goal_met else "No 😞"
study_week_delta = study_week - study_prev_week
study_week_class = "change-pos" if study_week_delta >= 0 else "change-neg"

with st.container(border=True):
    st.markdown('<div class="study-title">Study Weekly</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        stat_bubble(
            "Total Hours (YTD)",
            f"{study_year_total:.1f} hrs",
            "This year",
            f"+{study_week:.1f} hrs week to date",
            "change-pos",
            "study",
        )
    with c2:
        stat_bubble(
            "Weekly Hours",
            f"{study_week:.1f} hrs",
            "Week to date",
            f"{study_week_delta:+.1f} hrs vs prior week",
            study_week_class,
            "study",
        )
    with c3:
        stat_bubble(
            "Goal Met?",
            study_goal_text,
            f"Goal {study_goal:.0f} hrs",
            tone_class="study",
        )

study_days = study_recent.tail(7).copy()
study_days["dow"] = study_days["date"].dt.day_name().str[:3]
day_cols = st.columns(7)
for idx, (_, row) in enumerate(study_days.iterrows()):
    with day_cols[idx]:
        with st.container(border=True):
            st.markdown(
                f'<div class="chart-card-title">{row["dow"]}</div>',
                unsafe_allow_html=True,
            )
            studied = row["hours"] > 0
            center_label = format_hours_minutes(row["hours"])
            st.plotly_chart(
                donut_progress(
                    1 if studied else 0,
                    1,
                    "#8b5cf6",
                    height=130,
                    hole=0.5,
                    center_text=center_label,
                    center_font_size=16,
                ),
                use_container_width=True,
                key=f"study_day_{idx}",
                config={"displayModeBar": False},
            )

dreaming["date"] = pd.to_datetime(dreaming["date"])
spanish_total = dreaming["hours"].sum()
spanish_week, spanish_prev_week = week_to_date_values(
    dreaming, "date", "hours", agg="sum", reference_date=data_ref_date
)
spanish_goal = get_goal(weekly_goals, "spanish_hours")
goal_met = spanish_week >= spanish_goal
goal_text = "Yes 🙂" if goal_met else "No 😞"
total_added = spanish_week
week_delta = spanish_week - spanish_prev_week
week_change_class = "change-pos" if week_delta >= 0 else "change-neg"

with st.container(border=True):
    st.markdown('<div class="spanish-title">Dreaming Spanish Weekly</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        stat_bubble(
            "Total Hours",
            f"{spanish_total:.1f} hrs",
            "All time",
            f"+{total_added:.1f} hrs week to date",
            "change-pos",
            "spanish",
        )
    with c2:
        stat_bubble(
            "Weekly Hours",
            f"{spanish_week:.1f} hrs",
            "Week to date",
            f"{week_delta:+.1f} hrs vs prior week",
            week_change_class,
            "spanish",
        )
with c3:
        stat_bubble("Goal Met?", goal_text, f"Goal {spanish_goal:.1f} hrs", tone_class="spanish")

dreaming_recent = dreaming[dreaming["date"].dt.date <= data_ref_date]
week_days = dreaming_recent.tail(7).copy()
week_days["dow"] = week_days["date"].dt.day_name().str[:3]
daily_goal = spanish_goal / 7 if spanish_goal else 1

day_cols = st.columns(7)
for idx, (_, row) in enumerate(week_days.iterrows()):
    with day_cols[idx]:
        with st.container(border=True):
            st.markdown(
                f'<div class="chart-card-title">{row["dow"]}</div>',
                unsafe_allow_html=True,
            )
            pct = (row["hours"] / daily_goal * 100) if daily_goal else 0
            pct = max(0, min(pct, 100))
            st.plotly_chart(
                donut_progress(
                    pct,
                    100,
                    "#f59e0b",
                    height=120,
                    hole=0.45,
                    center_text=f"{pct:.0f}%",
                    center_font_size=16,
                ),
                use_container_width=True,
                key=f"spanish_day_{idx}",
                config={"displayModeBar": False},
            )

st.markdown('<div class="page-spacer"></div>', unsafe_allow_html=True)
