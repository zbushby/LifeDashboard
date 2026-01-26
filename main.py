import datetime as dt
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

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


def stat_bubble(title: str, value: str, sub: str = "") -> None:
    st.markdown(
        f"""
        <div class="stat-bubble">
          <div class="stat-title">{title}</div>
          <div class="stat-value">{value}</div>
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


def donut_progress(value: float, goal: float, color: str, height: int = 140) -> go.Figure:
    if not goal or goal <= 0:
        st.error("Invalid goal value in CSV.")
        st.stop()
    value = max(min(value, goal), 0)
    fig = go.Figure(
        data=[
            go.Pie(
                values=[value, max(goal - value, 0)],
                hole=0.75,
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
        annotations=[
            dict(
                text=f"{int(value)} / {int(goal)}",
                x=0.5,
                y=0.5,
                font_size=16,
                showarrow=False,
            )
        ],
    )
    return fig


def expense_pie(df: pd.DataFrame, colors: list[str]) -> go.Figure:
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
        height=120,
        showlegend=False,
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
    .card-title { color: #6b7280; font-size: 10px; text-transform: uppercase; letter-spacing: .08em; }
    .card-value { font-size: 22px; font-weight: 700; color: #111827; margin-top: 3px; }
    .card-sub { font-size: 10px; color: #9ca3af; margin-top: 2px; }
    .section-title { font-size: 15px; font-weight: 700; margin: 6px 0 4px 0; }
    .weather-mini { text-align: center; padding: 6px 4px; border-radius: 10px; }
    .weather-day { font-size: 12px; color: #6b7280; }
    .weather-icon { font-size: 18px; margin: 4px 0; }
    .weather-temp { font-size: 13px; color: #111827; }
    .card-change { font-size: 10px; margin-top: 3px; }
    .change-pos { color: #16a34a; }
    .change-neg { color: #dc2626; }
    .tone-finance { border-top: 3px solid #2563eb; }
    .tone-health { border-top: 3px solid #10b981; background: #f2fbf7; }
    .tone-study { border-top: 3px solid #f59e0b; background: #fff7ed; }
    .tone-spanish { border-top: 3px solid #f59e0b; background: #fff7ed; }
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
    .birthday-list { display: grid; gap: 6px; }
    .birthday-item { display: flex; justify-content: flex-start; gap: 10px; font-size: 12px; padding: 6px 8px; background: #ffffff; border: 1px solid #ededed; border-radius: 10px; }
    .birthday-date { color: #6b7280; }
    .spanish-panel { padding: 12px 14px; }
    .spanish-title { font-size: 16px; font-weight: 700; margin-bottom: 8px; color: #111827; }
    .stat-bubble { background: #ffffff; border: 1px solid #fde68a; border-radius: 14px; padding: 10px; text-align: center; }
    .stat-title { font-size: 10px; text-transform: uppercase; letter-spacing: .08em; color: #92400e; }
    .stat-value { font-size: 20px; font-weight: 700; color: #111827; margin-top: 4px; }
    .stat-sub { font-size: 10px; color: #a16207; margin-top: 2px; }
    .day-bubble { background: #ffffff; border: 1px solid #fde68a; border-radius: 14px; padding: 6px 6px 2px 6px; text-align: center; }
    .day-label { font-size: 11px; font-weight: 600; color: #92400e; margin-bottom: 2px; }
    .bubble-card { padding: 10px; }
    .bubble-title { font-size: 12px; font-weight: 700; color: #111827; margin-bottom: 6px; }
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
last_4 = finance_sorted.tail(4)[["week_start", "budget", "actual", "delta"]].copy()
last_4["week_start"] = last_4["week_start"].dt.strftime("%b %d")
prev_week = finance_sorted.iloc[-2] if len(finance_sorted) > 1 else last_week
net_delta = last_week["actual"] - prev_week["actual"]
net_pct = (net_delta / prev_week["actual"] * 100) if prev_week["actual"] else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    delta = last_week["budget"] - prev_week["budget"]
    pct = (delta / prev_week["budget"] * 100) if prev_week["budget"] else 0
    change = f"{fmt_money(delta)} ({pct:+.2f}%)"
    change_class = "change-pos" if delta >= 0 else "change-neg"
    card(
        "Weekly Budget",
        fmt_money(last_week["budget"]),
        "Last week",
        change,
        change_class,
        "tone-finance",
    )
with col2:
    delta = last_week["actual"] - prev_week["actual"]
    pct = (delta / prev_week["actual"] * 100) if prev_week["actual"] else 0
    change = f"{fmt_money(delta)} ({pct:+.2f}%)"
    change_class = "change-neg" if delta > 0 else "change-pos"
    card(
        "Weekly Spend",
        fmt_money(last_week["actual"]),
        "Last week",
        change,
        change_class,
        "tone-finance",
    )
with col3:
    delta = last_week["delta"] - prev_week["delta"]
    pct = (delta / prev_week["delta"] * 100) if prev_week["delta"] else 0
    change = f"{fmt_money(delta)} ({pct:+.2f}%)"
    change_class = "change-neg" if delta > 0 else "change-pos"
    card(
        "Delta",
        fmt_money(last_week["delta"]),
        "Budget vs actual",
        change,
        change_class,
        "tone-finance",
    )
with col4:
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

net_pie = go.Figure(
    data=[
        go.Pie(
            labels=net_alloc["asset"],
            values=net_alloc["amount"],
            hole=0.55,
            marker=dict(colors=["#1d4ed8", "#10b981", "#f59e0b", "#ef4444"]),
            hovertemplate="%{label}: %{value:$,.0f}<extra></extra>",
            textinfo="none",
        )
    ]
)
net_pie.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=120, showlegend=False)

eat_pie = expense_pie(
    expenses_eat,
    ["#0ea5e9", "#22c55e", "#f97316", "#a855f7"],
)
ent_pie = expense_pie(
    expenses_ent,
    ["#ec4899", "#f43f5e", "#8b5cf6", "#14b8a6"],
)

p1, p2, p3 = st.columns(3)
with p1:
    st.markdown(
        '<div class="card tone-finance bubble-card"><div class="bubble-title">Net Worth Allocation</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(
        net_pie,
        width="stretch",
        key="net_worth_pie",
        config={"displayModeBar": False},
    )
    st.markdown("</div>", unsafe_allow_html=True)
with p2:
    st.markdown(
        '<div class="card tone-finance bubble-card"><div class="bubble-title">Eating / Drinking Out</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(
        eat_pie,
        width="stretch",
        key="eat_pie",
        config={"displayModeBar": False},
    )
    st.markdown("</div>", unsafe_allow_html=True)
with p3:
    st.markdown(
        '<div class="card tone-finance bubble-card"><div class="bubble-title">Entertainment</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(
        ent_pie,
        width="stretch",
        key="ent_pie",
        config={"displayModeBar": False},
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="section-title">Health</div>', unsafe_allow_html=True)
sleep["date"] = pd.to_datetime(sleep["date"])
weight["date"] = pd.to_datetime(weight["date"])
gym["date"] = pd.to_datetime(gym["date"])
if (DATA_DIR / "bjj_daily.csv").exists():
    bjj = load_csv(DATA_DIR / "bjj_daily.csv")
else:
    bjj = pd.DataFrame(columns=["date", "sessions"])
if not bjj.empty:
    bjj["date"] = pd.to_datetime(bjj["date"])
calories["date"] = pd.to_datetime(calories["date"])
weight_weekly = weight.set_index("date")["weight"].resample("W").mean()
gym_weekly = gym.set_index("date")[["minutes", "volume"]].resample("W").sum()

col1, col2, col3, col4 = st.columns(4)
with col1:
    last7 = sleep["hours"].tail(7).mean()
    prev7 = sleep["hours"].tail(14).head(7).mean()
    delta = last7 - prev7
    pct = (delta / prev7 * 100) if prev7 else 0
    change = f"{delta:+.1f} ({pct:+.2f}%)"
    change_class = "change-pos" if delta >= 0 else "change-neg"
    card(
        "Sleep Avg (7d)",
        f"{last7:.1f} hrs",
        "Last 7 days",
        change,
        change_class,
        "tone-health",
    )
with col2:
    last = weight_weekly.iloc[-1]
    prev = weight_weekly.iloc[-2] if len(weight_weekly) > 1 else last
    delta = last - prev
    pct = (delta / prev * 100) if prev else 0
    change = f"{delta:+.1f} ({pct:+.2f}%)"
    change_class = "change-neg" if delta > 0 else "change-pos"
    card(
        "Weight (Weekly Avg)",
        f"{last:.1f} kg",
        "This week",
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
    last = int(gym["volume"].tail(7).sum())
    prev = int(gym["volume"].tail(14).head(7).sum())
    delta = last - prev
    pct = (delta / prev * 100) if prev else 0
    change = f"{delta:+,} ({pct:+.2f}%)"
    change_class = "change-pos" if delta >= 0 else "change-neg"
    card(
        "Gym Volume (7d)",
        f"{last:,}",
        "Last 7 days",
        change,
        change_class,
        "tone-health",
    )

st.markdown('<div class="section-title">Exercise</div>', unsafe_allow_html=True)
gym_sessions = int((gym["minutes"].tail(7) > 0).sum())
bjj_sessions = int((bjj["sessions"].tail(7) > 0).sum()) if not bjj.empty else 0
g_goal = get_goal(weekly_goals, "gym_sessions")
b_goal = get_goal(weekly_goals, "bjj_sessions")

g1, g2 = st.columns(2)
with g1:
    st.markdown('<div class="card tone-health">Gym Sessions</div>', unsafe_allow_html=True)
    st.plotly_chart(
        donut_progress(gym_sessions, g_goal, "#10b981"),
        width="stretch",
        key="gym_donut",
        config={"displayModeBar": False},
    )
with g2:
    st.markdown('<div class="card tone-health">BJJ Sessions</div>', unsafe_allow_html=True)
    st.plotly_chart(
        donut_progress(bjj_sessions, b_goal, "#22c55e"),
        width="stretch",
        key="bjj_donut",
        config={"displayModeBar": False},
    )

st.markdown('<div class="section-title">Weight Trend (Weekly Avg)</div>', unsafe_allow_html=True)
st.line_chart(weight_weekly.tail(26))


st.markdown('<div class="section-title">Study</div>', unsafe_allow_html=True)
study["date"] = pd.to_datetime(study["date"])
col1, col2, col3 = st.columns(3)
with col1:
    last = study["hours"].tail(7).mean()
    prev = study["hours"].tail(14).head(7).mean()
    delta = last - prev
    pct = (delta / prev * 100) if prev else 0
    change = f"{delta:+.1f} ({pct:+.2f}%)"
    change_class = "change-pos" if delta >= 0 else "change-neg"
    card(
        "Study (7d)",
        f"{last:.1f} hrs",
        "Last 7 days",
        change,
        change_class,
        "tone-study",
    )
with col2:
    card(
        "Study (30d)",
        f"{study['hours'].tail(30).mean():.1f} hrs",
        "Last 30 days",
        "",
        "",
        "tone-study",
    )
with col3:
    card("Daily Avg", f"{study['hours'].mean():.1f} hrs", "All time", "", "", "tone-study")

dreaming["date"] = pd.to_datetime(dreaming["date"])
spanish_total = dreaming["hours"].sum()
spanish_week = dreaming["hours"].tail(7).sum()
spanish_goal = get_goal(weekly_goals, "spanish_hours")
goal_met = "Yes" if spanish_week >= spanish_goal else "No"

st.markdown('<div class="card tone-spanish spanish-panel">', unsafe_allow_html=True)
st.markdown('<div class="spanish-title">Dreaming Spanish Weekly</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    stat_bubble("Total Hours", f"{spanish_total:.1f} hrs", "All time")
with c2:
    stat_bubble("Weekly Hours", f"{spanish_week:.1f} hrs", "Last 7 days")
with c3:
    stat_bubble("Goal Met?", goal_met, f"Goal {spanish_goal:.1f} hrs")

week_days = dreaming.tail(7).copy()
week_days["dow"] = week_days["date"].dt.day_name().str[:3]
daily_goal = spanish_goal / 7 if spanish_goal else 0.5

day_cols = st.columns(7)
for idx, (_, row) in enumerate(week_days.iterrows()):
    with day_cols[idx]:
        st.markdown('<div class="day-bubble">', unsafe_allow_html=True)
        st.markdown(f'<div class="day-label">{row["dow"]}</div>', unsafe_allow_html=True)
        st.plotly_chart(
            donut_progress(row["hours"], daily_goal, "#f59e0b", height=110),
            width="stretch",
            key=f"spanish_day_{idx}",
            config={"displayModeBar": False},
        )
        st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="section-title">Upcoming Birthdays</div>', unsafe_allow_html=True)
birthdays["date"] = pd.to_datetime(birthdays["date"])
today_dt = pd.Timestamp.today().normalize()
next_dates = []
for _, row in birthdays.iterrows():
    date = row["date"]
    next_date = date.replace(year=today_dt.year)
    if next_date < today_dt:
        next_date = next_date.replace(year=today_dt.year + 1)
    next_dates.append(next_date)
birthdays["next_date"] = next_dates
birthdays = birthdays.sort_values("next_date").head(10)

items = []
for _, row in birthdays.iterrows():
    date_str = row["next_date"].strftime("%b %d, %Y")
    items.append(
        f'<div class="birthday-item"><span>{row["name"]}</span><span class="birthday-date">{date_str}</span></div>'
    )
list_html = f'<div class="card"><div class="birthday-list">{"".join(items)}</div></div>'
st.markdown(list_html, unsafe_allow_html=True)
