# Plan: Apple Health Module (Module 1)

**Created:** 2026-02-20
**Status:** Implemented
**Request:** Build the Apple Health module -- data parsing pipeline and dashboard views for body composition, sleep, and study hours.

---

## Overview

### What This Plan Accomplishes

Creates `modules/apple_health.py` (inside `2. Dashboard/`) to parse Health Auto Export JSON
files and expose clean DataFrames for each metric. Updates three dashboard layout files
(`health.py`, `sleep.py`, and the study-hours panel in `learning.py`) with real Plotly
charts. Also converts `app.layout` to a function so fresh data is loaded on every browser
refresh.

### Why This Matters

This is the first live data module. After it's complete, the dashboard shows real body
composition trends, nightly sleep, and study hour tracking -- answering three of the
weekly review questions (weight/BF progress, sleep quality, study target).

---

## Current State

### Relevant Existing Structure

- `2. Dashboard/app.py` — webhook `/api/health-export` already implemented; saves raw
  JSON to `3. Data/apple-health/`. Layout is set once at startup (static).
- `2. Dashboard/layouts/health.py` — placeholder card, no charts.
- `2. Dashboard/layouts/sleep.py` — placeholder card, no charts.
- `2. Dashboard/layouts/learning.py` — two-column card; left panel is placeholder for
  study hours, right panel is DS placeholder.
- `3. Data/apple-health/` — directory exists, empty (no exports yet).
- `modules/` at project root — exists but is empty; NOT inside the Docker build context.

### Gaps or Problems Being Addressed

1. **No data parsing module** — nothing reads the saved JSON files yet.
2. **Module location issue** — `modules/` at project root is outside the Docker build
   context (`./2. Dashboard`). Python modules that layouts import must live inside
   `2. Dashboard/`.
3. **Static layout** — `app.layout` is built once at startup; webhook data arriving
   later won't appear until restart.
4. **No sample data** — can't develop or verify charts without data.

---

## Proposed Changes

### Summary of Changes

- Create `2. Dashboard/modules/` package with `apple_health.py` data parsing module
- Update `2. Dashboard/layouts/health.py` with body composition stats + charts
- Update `2. Dashboard/layouts/sleep.py` with sleep stats + chart
- Update left panel of `2. Dashboard/layouts/learning.py` with study hours + progress bar
- Update `2. Dashboard/app.py` to use `serve_layout()` function (fresh data on page load)
- Create sample data file `3. Data/apple-health/export_sample.json` for development
- Update `CLAUDE.md` and `context/tech-stack.md` to document modules-in-Dashboard location
- Update `context/module-roadmap.md` to mark Module 1 as Done

### New Files to Create

| File Path | Purpose |
|-----------|---------|
| `2. Dashboard/modules/__init__.py` | Makes modules a package |
| `2. Dashboard/modules/apple_health.py` | Parse Health Auto Export JSON → DataFrames |
| `3. Data/apple-health/export_sample.json` | Sample data for local development/testing |

### Files to Modify

| File Path | Changes |
|-----------|---------|
| `2. Dashboard/app.py` | Wrap layout in `serve_layout()` function; add modules import path note |
| `2. Dashboard/layouts/health.py` | Full chart layout: stats row + weight trend + calories |
| `2. Dashboard/layouts/sleep.py` | Sleep stats + nightly bar chart |
| `2. Dashboard/layouts/learning.py` | Left panel: study hours stat + progress bar + daily chart |
| `CLAUDE.md` | Update workspace structure: `modules/` is inside `2. Dashboard/` |
| `context/tech-stack.md` | Clarify modules location in project structure |
| `context/module-roadmap.md` | Mark Module 1 as Done, add plan file link |

---

## Design Decisions

### Key Decisions Made

1. **Modules inside `2. Dashboard/`**: The Docker build context is `./2. Dashboard`, so
   all Python code imported by the app must live there. `2. Dashboard/modules/` is the
   correct location. The top-level `modules/` folder at project root is not usable by
   the live app (kept for reference scripts only).

2. **`serve_layout()` for fresh data**: Wrapping `app.layout` in a function causes Dash
   to call it on every browser request, reading fresh data from disk. This is the standard
   Dash pattern for data that updates while the app is running (via webhook). No callbacks
   or `dcc.Interval` needed for a weekly review use case.

3. **Load data at render time**: Each layout function calls `apple_health` module directly.
   No caching layer -- the files are small JSON/DataFrames and the dashboard is loaded
   infrequently. KISS.

4. **Deduplicate exports by full datetime**: Multiple export files will contain overlapping
   data. Deduplicate by (metric, full datetime string) so each unique reading appears once.
   Multiple sessions per day (e.g., mindfulness) are preserved because they have different
   timestamps.

5. **Graceful empty-state**: If no export files exist yet, all `get_*` functions return
   empty DataFrames. Layout functions detect empty DataFrames and render a "waiting for
   data" message styled like the existing `.placeholder-msg` class.

6. **28-day weight trend**: Body composition chart shows 4 weeks of data to reveal a
   meaningful trend. Other charts show 7 days (current week).

7. **No scheduler job for Apple Health**: Data arrives via iOS webhook push, not a pull.
   No APScheduler job needed. The webhook handler in `app.py` already saves raw JSON.

8. **Dark chart theme**: All Plotly figures use transparent backgrounds, muted grey axes
   and gridlines, and colours from the GitHub dark palette
   (`#58a6ff` blue, `#3fb950` green) to blend with the DARKLY Bootstrap theme.

### Alternatives Considered

- **Top-level `modules/`**: Would require changing the Docker build context to the project
  root, adding complexity to the Dockerfile. Rejected in favour of keeping modules inside
  the Dashboard folder.
- **Database for data storage**: Overkill for a weekly review dashboard reading small
  JSON files. Flat files are simpler and sufficient.
- **`dcc.Interval` auto-refresh**: More complex and unnecessary -- the user opens the
  browser once on Sunday evening.

### Open Questions

None -- all design decisions are made. Proceed with implementation.

---

## Step-by-Step Tasks

### Step 1: Create sample data file

Create `3. Data/apple-health/export_sample.json` with 30 days of realistic sample data.
This lets us develop and verify charts locally before the iPhone app is configured.

**Data to include (Health Auto Export format):**

```json
{
  "data": {
    "metrics": [
      {
        "name": "body_mass",
        "units": "kg",
        "data": [
          {"date": "YYYY-MM-DD 07:30:00 +1100", "qty": <weight>},
          ...
        ]
      },
      {
        "name": "body_fat_percentage",
        "units": "%",
        "data": [...]
      },
      {
        "name": "lean_body_mass",
        "units": "kg",
        "data": [...]
      },
      {
        "name": "dietary_energy_consumed",
        "units": "kcal",
        "data": [...]
      },
      {
        "name": "sleep_analysis",
        "units": "hr",
        "data": [
          {"date": "YYYY-MM-DD 07:00:00 +1100", "qty": 7.5, "asleep": 7.2},
          ...
        ]
      },
      {
        "name": "mindful_session",
        "units": "min",
        "data": [
          {"date": "YYYY-MM-DD 09:00:00 +1100", "qty": 45.0},
          {"date": "YYYY-MM-DD 14:30:00 +1100", "qty": 60.0},
          ...
        ]
      }
    ],
    "workouts": []
  }
}
```

**Sample values (cover today-30 days to today, use relative dates):**
- Weight: start 72.5 kg, end 71.2 kg (gentle downward trend, daily noise ±0.3 kg)
- Body fat: start 14.5%, end 13.8% (downward trend, 3 decimal precision)
- Lean mass: ~60.5 kg (relatively stable ±0.3 kg)
- Calories: 1800–2300 kcal/day (varies, skip ~4 days to simulate missing data)
- Sleep: 6.2–8.1 hrs/night (`asleep` field; `qty` = same or slightly higher for in-bed)
- Mindfulness: 2–4 sessions/day Mon–Fri, 0–1 on weekends; 30–90 min each session
  Approximate weekly totals: ~10–15 hrs study time

Generate exact dates relative to 2026-02-20 (today). Cover 2026-01-21 through 2026-02-20.

**Actions:**
- Generate the full JSON with ~30 data points per metric (skip a few days realistically)
- Write to `3. Data/apple-health/export_sample.json`

**Files affected:**
- `3. Data/apple-health/export_sample.json` (new)

---

### Step 2: Create the `modules` package inside `2. Dashboard/`

**Actions:**
- Create `2. Dashboard/modules/__init__.py` (empty file)

**Files affected:**
- `2. Dashboard/modules/__init__.py` (new, empty)

---

### Step 3: Create `2. Dashboard/modules/apple_health.py`

Full content of the module:

```python
"""Apple Health data parsing module.

Reads JSON files exported by the Health Auto Export iOS app from the
apple-health/ subdirectory of data_dir. Each file is a POST payload saved by the
/api/health-export webhook in app.py.

Health Auto Export JSON structure:
    {
        "data": {
            "metrics": [
                {
                    "name": "body_mass",
                    "units": "kg",
                    "data": [
                        {"date": "2026-01-15 08:30:00 +1100", "qty": 71.2},
                        ...
                    ]
                },
                ...
            ]
        }
    }

Metric names used by Health Auto Export:
    body_mass                  - weight in kg
    body_fat_percentage        - body fat %
    lean_body_mass             - lean body mass in kg
    dietary_energy_consumed    - daily food intake in kcal
    sleep_analysis             - sleep; "asleep" field for sleep hours, "qty" for in-bed
    mindful_session            - mindfulness session duration in minutes (Forest app)
"""

import json
import os
from datetime import datetime, timedelta

import pandas as pd


# Map friendly names to Health Auto Export metric names
_METRIC = {
    "weight":    "body_mass",
    "body_fat":  "body_fat_percentage",
    "lean_mass": "lean_body_mass",
    "calories":  "dietary_energy_consumed",
    "sleep":     "sleep_analysis",
    "study":     "mindful_session",
}


def _parse_date(date_str):
    """Parse Health Auto Export date string to datetime, stripping tz offset."""
    s = str(date_str).strip()
    # Drop trailing timezone offset like "+1100" or "-0500"
    parts = s.rsplit(" ", 1)
    if len(parts) == 2 and len(parts[1]) == 5 and parts[1][0] in ("+", "-"):
        s = parts[0]
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def load_all_exports(data_dir):
    """Load and merge all export JSON files from apple-health/.

    Returns:
        dict: {metric_name: [entry_dict, ...]} where each entry_dict contains
              the original fields plus "_date" (datetime). Sorted ascending by _date.
              Entries are deduplicated by (metric, datetime) across multiple files.
    """
    ah_dir = os.path.join(data_dir, "apple-health")
    if not os.path.isdir(ah_dir):
        return {}

    # Load files newest-first so first-seen wins in deduplication
    files = sorted(
        [f for f in os.listdir(ah_dir) if f.endswith(".json")],
        reverse=True,
    )

    metrics: dict = {}

    for filename in files:
        filepath = os.path.join(ah_dir, filename)
        try:
            with open(filepath) as fh:
                raw = json.load(fh)
        except Exception:
            continue

        # Handle both {"data": {"metrics": [...]}} and {"metrics": [...]}
        block = raw.get("data", raw)
        metric_list = block.get("metrics", [])

        for metric in metric_list:
            name = metric.get("name")
            if not name:
                continue
            if name not in metrics:
                metrics[name] = {}  # key: full datetime ISO string

            for entry in metric.get("data", []):
                dt = _parse_date(entry.get("date", ""))
                if dt is None:
                    continue
                key = dt.isoformat()
                if key not in metrics[name]:  # newest file wins
                    metrics[name][key] = {**entry, "_date": dt}

    # Convert to sorted lists
    return {
        name: sorted(entries.values(), key=lambda e: e["_date"])
        for name, entries in metrics.items()
    }


def _date_range_df(days):
    """Return a DataFrame with a 'date' column covering today-days to today."""
    dates = pd.date_range(
        start=(datetime.now() - timedelta(days=days)).date(),
        end=datetime.now().date(),
        freq="D",
    )
    return pd.DataFrame({"date": pd.to_datetime(dates)})


def get_body_composition(data_dir, days=28):
    """Daily body composition over the last `days` days.

    Returns:
        DataFrame columns: date, weight_kg, body_fat_pct, lean_mass_kg
        Rows with no reading have NaN. Sorted ascending by date.
    """
    exports = load_all_exports(data_dir)
    cutoff = datetime.now() - timedelta(days=days)

    df = _date_range_df(days)
    df["weight_kg"] = float("nan")
    df["body_fat_pct"] = float("nan")
    df["lean_mass_kg"] = float("nan")

    def _fill(col, metric_key):
        for entry in exports.get(_METRIC[metric_key], []):
            if entry["_date"] < cutoff:
                continue
            d = pd.Timestamp(entry["_date"].date())
            mask = df["date"] == d
            # Last reading of the day wins (entries are sorted ascending)
            if mask.any():
                df.loc[mask, col] = entry.get("qty", float("nan"))

    _fill("weight_kg", "weight")
    _fill("body_fat_pct", "body_fat")
    _fill("lean_mass_kg", "lean_mass")
    return df


def get_calories(data_dir, days=7):
    """Daily calorie intake for the last `days` days.

    Returns:
        DataFrame columns: date, calories
    """
    exports = load_all_exports(data_dir)
    cutoff = datetime.now() - timedelta(days=days)

    df = _date_range_df(days)
    df["calories"] = float("nan")

    for entry in exports.get(_METRIC["calories"], []):
        if entry["_date"] < cutoff:
            continue
        d = pd.Timestamp(entry["_date"].date())
        mask = df["date"] == d
        if mask.any():
            df.loc[mask, "calories"] = entry.get("qty", float("nan"))

    return df


def get_sleep(data_dir, days=7):
    """Nightly sleep hours for the last `days` days.

    Uses the 'asleep' field if present (actual sleep), falls back to 'qty' (in-bed).

    Returns:
        DataFrame columns: date, sleep_hours
        'date' is the morning wake-up date.
    """
    exports = load_all_exports(data_dir)
    cutoff = datetime.now() - timedelta(days=days + 1)

    df = _date_range_df(days)
    df["sleep_hours"] = float("nan")

    for entry in exports.get(_METRIC["sleep"], []):
        if entry["_date"] < cutoff:
            continue
        hours = entry.get("asleep", entry.get("qty", float("nan")))
        d = pd.Timestamp(entry["_date"].date())
        mask = df["date"] == d
        if mask.any():
            # Keep the longest sleep record for the day (handles nap entries)
            existing = df.loc[mask, "sleep_hours"].values[0]
            if pd.isna(existing) or hours > existing:
                df.loc[mask, "sleep_hours"] = hours

    return df


def get_study_hours(data_dir, days=7):
    """Daily study time (mindfulness minutes) for the last `days` days.

    Sums all mindful sessions per day and converts to hours.

    Returns:
        DataFrame columns: date, study_hours
    """
    exports = load_all_exports(data_dir)
    cutoff = datetime.now() - timedelta(days=days)

    df = _date_range_df(days)
    df["study_hours"] = 0.0

    for entry in exports.get(_METRIC["study"], []):
        if entry["_date"] < cutoff:
            continue
        minutes = entry.get("qty", 0.0) or 0.0
        d = pd.Timestamp(entry["_date"].date())
        mask = df["date"] == d
        if mask.any():
            df.loc[mask, "study_hours"] += minutes / 60.0

    return df
```

**Actions:**
- Create `2. Dashboard/modules/apple_health.py` with the exact content above.

**Files affected:**
- `2. Dashboard/modules/apple_health.py` (new)

---

### Step 4: Update `2. Dashboard/layouts/health.py`

Full replacement content:

```python
"""Health module layout - body composition and calories (Apple Health).

Shows:
  - Stats row: current weight, body fat %, lean mass
  - Weight trend line chart (28 days) with 70 kg target line
  - Daily calories bar chart (7 days)

Calls modules/apple_health.py at render time (data read from disk).
Returns placeholder content if no data files exist yet.
"""

import pandas as pd
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
COLOR_RED = "#f85149"


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
```

**Actions:**
- Replace the full contents of `2. Dashboard/layouts/health.py` with the code above.

**Files affected:**
- `2. Dashboard/layouts/health.py`

---

### Step 5: Update `2. Dashboard/layouts/sleep.py`

Full replacement content:

```python
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
```

**Actions:**
- Replace full contents of `2. Dashboard/layouts/sleep.py`.

**Files affected:**
- `2. Dashboard/layouts/sleep.py`

---

### Step 6: Update left panel of `2. Dashboard/layouts/learning.py`

The left panel switches from placeholder to real study hours data.
The right panel (Dreaming Spanish) remains as a placeholder.

Full replacement content:

```python
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
```

**Actions:**
- Replace full contents of `2. Dashboard/layouts/learning.py`.

**Files affected:**
- `2. Dashboard/layouts/learning.py`

---

### Step 7: Update `app.py` — wrap layout in `serve_layout()`

Change the layout assignment from a static call to a function.

**Current code (lines 48–96):**
```python
app.layout = dbc.Container(
    [
        ...
    ],
    fluid=True,
)
```

**New code:**
```python
def serve_layout():
    """Called on every page request -- ensures fresh data is read from disk."""
    return dbc.Container(
        [
            # Header
            dbc.Row(
                dbc.Col([
                    html.H1("Life Dashboard", className="text-center mt-4 mb-1"),
                    html.P(
                        f"Week of {week_label()}",
                        className="text-center text-muted mb-3",
                    ),
                    html.Hr(),
                ])
            ),

            # Row 1: Health (8 cols) + Sleep (4 cols)
            dbc.Row([
                dbc.Col(health.layout(DATA_DIR), md=8, className="mb-4"),
                dbc.Col(sleep.layout(DATA_DIR), md=4, className="mb-4"),
            ]),

            # Row 2: Fitness - full width
            dbc.Row([
                dbc.Col(fitness.layout(DATA_DIR), md=12, className="mb-4"),
            ]),

            # Row 3: Finances (6 cols) + Investments (6 cols)
            dbc.Row([
                dbc.Col(finances.layout(DATA_DIR), md=6, className="mb-4"),
                dbc.Col(investments.layout(DATA_DIR), md=6, className="mb-4"),
            ]),

            # Row 4: Learning (8 cols) + Birthdays (4 cols)
            dbc.Row([
                dbc.Col(learning.layout(DATA_DIR), md=8, className="mb-4"),
                dbc.Col(birthdays.layout(DATA_DIR), md=4, className="mb-4"),
            ]),

            # Footer
            dbc.Row(
                dbc.Col(
                    html.P(
                        f"Generated {datetime.now().strftime('%A %-d %B %Y, %-I:%M %p')}",
                        className="text-center text-muted mt-2 mb-4",
                    )
                )
            ),
        ],
        fluid=True,
    )


app.layout = serve_layout
```

**Actions:**
- Replace the `app.layout = dbc.Container(...)` block with the `serve_layout()` function
  and `app.layout = serve_layout` assignment.
- No other changes to `app.py`.

**Files affected:**
- `2. Dashboard/app.py`

---

### Step 8: Test locally

Run the Dash app locally to verify charts render with sample data.

**Actions:**
- `cd "2. Dashboard" && python app.py` (requires `.venv` to be active)
- Open `http://localhost:8050` in browser
- Verify: Health card shows weight/BF/lean mass stats and two charts
- Verify: Sleep card shows avg hrs and 7-day bar chart
- Verify: Learning card left panel shows study hours, progress bar, daily chart
- Verify: Other cards still show placeholder messages (unchanged)
- Verify: Refreshing the browser re-reads data (no server restart needed)

**Files affected:** none (testing only)

---

### Step 9: Update `CLAUDE.md` workspace structure section

Update the `modules/` entry in the workspace structure table to clarify that
live modules live inside `2. Dashboard/modules/`, not at the project root.

**Find this block in CLAUDE.md:**
```
  modules/                    - Data fetch and processing scripts (one per source)
```

**Replace with:**
```
  2. Dashboard/modules/       - Data processing modules (inside Docker build context)
  modules/                    - Reference scripts only (not used by live app)
```

Also update the structure diagram in CLAUDE.md under `2. Dashboard/`:
```
  2. Dashboard/               - Dash app (app.py, layouts/, assets/)
```
becomes:
```
  2. Dashboard/               - Dash app (app.py, layouts/, modules/, assets/)
```

**Files affected:**
- `CLAUDE.md`

---

### Step 10: Update `context/tech-stack.md`

In the Project Structure section, move `modules/` from the top level into `2. Dashboard/`:

Under `2. Dashboard/` add:
```
    modules/
      apple_health.py         - Parse Health Auto Export JSON -> dataframes
      finances.py             - Up Bank API -> spending data (future)
      calendar_sync.py        - Google Calendar API -> events (future)
      strava.py               - Strava API -> gym volume (future)
      investments.py          - Google Sheets API -> portfolio (future)
      dreaming_spanish.py     - Scraper -> DS progress (future)
```

Remove the top-level `modules/` block from the structure diagram.

**Files affected:**
- `context/tech-stack.md`

---

### Step 11: Update `context/module-roadmap.md`

Mark Module 1 as Done and add checklist.

**Actions:**
- Change Module 1 row status from `Not started` to `Done`
- Add plan file link: `plans/2026-02-20-apple-health-module.md`
- Add a Module 1 checklist section (similar to Foundation Checklist)
- Update "Next Steps" to point to Module 2 (Finances)

Module 1 checklist to add:
```markdown
## Apple Health Checklist (Module 1)

| Task | Status |
|------|--------|
| modules/apple_health.py created | Done |
| layouts/health.py: weight + BF stats + charts | Done |
| layouts/sleep.py: sleep avg + chart | Done |
| layouts/learning.py: study hours panel | Done |
| serve_layout() function in app.py | Done |
| Sample data tested locally | Done |
| CLAUDE.md updated (modules location) | Done |

### iPhone Setup Required (before real data appears)
1. Install "Health Auto Export - JSON+CSV" from App Store (free)
2. Open app → Configure → add these metrics:
   - Body Mass
   - Body Fat Percentage
   - Lean Body Mass
   - Dietary Energy Consumed
   - Sleep Analysis
   - Mindful Session
3. Set Export Format: JSON
4. Set Auto-Export: Daily
5. Set Webhook URL: `http://[proxmox-ip]:8050/api/health-export`
6. Tap "Export Now" once to send a test payload and verify data appears
```

**Files affected:**
- `context/module-roadmap.md`

---

## Connections & Dependencies

### Files That Reference This Area

- `2. Dashboard/app.py` — imports all layout modules; webhook handler saves to apple-health/
- `2. Dashboard/layouts/health.py` — imports `modules.apple_health`
- `2. Dashboard/layouts/sleep.py` — imports `modules.apple_health`
- `2. Dashboard/layouts/learning.py` — imports `modules.apple_health`

### Updates Needed for Consistency

- `CLAUDE.md` workspace structure (Step 9)
- `context/tech-stack.md` project structure (Step 10)
- `context/module-roadmap.md` build status (Step 11)

### Impact on Existing Workflows

- `serve_layout()` change is backward-compatible -- other layout modules are unaffected
- No new Python packages required (all dependencies already in `requirements.txt`)
- No changes to `Dockerfile` or `docker-compose.yml`

---

## Validation Checklist

- [ ] `3. Data/apple-health/export_sample.json` exists and has 30+ data points per metric
- [ ] `2. Dashboard/modules/__init__.py` exists (empty)
- [ ] `2. Dashboard/modules/apple_health.py` exists with all 5 functions
- [ ] `python app.py` starts without errors
- [ ] Health card renders: 3 stats + weight chart + calories chart
- [ ] Sleep card renders: avg stat + 7-day bar chart
- [ ] Learning card left panel renders: total hrs + progress bar + daily chart
- [ ] Browser refresh reloads fresh data (no server restart)
- [ ] Other placeholder cards (Fitness, Finances, Investments, Birthdays) still render
- [ ] `CLAUDE.md` updated to document modules-in-Dashboard location
- [ ] `context/module-roadmap.md` updated: Module 1 = Done

---

## Success Criteria

The implementation is complete when:

1. `python app.py` runs locally and all three Apple Health sections render with sample data
2. The weight trend chart shows a line with a dashed 70 kg target, and stats display
   weight, BF%, and lean mass with colour coding against targets
3. `context/module-roadmap.md` shows Module 1 as Done

---

## Notes

- **iPhone setup is a post-deployment step**: The dashboard code must be deployed to
  Proxmox (with the webhook endpoint live) before Health Auto Export can be configured
  to send real data. The sample data file allows full local development first.
- **Proxmox deployment**: After this module is complete, run `docker compose up --build`
  on Proxmox to deploy. Then configure the iPhone app with the Proxmox IP.
- **Data accumulation**: Each daily export from Health Auto Export includes all historical
  data. `load_all_exports()` handles deduplication so each reading appears only once.
- **Missing body fat / lean mass**: Some iPhones don't have body fat sensors. If the
  user uses a smart scale that posts to Apple Health, those metrics will appear. If not,
  the stats show "—" gracefully.
- **Module 2 (Finances)**: Next module after this one. Run
  `/create-plan finances-module` to begin.

---

## Implementation Notes

**Implemented:** 2026-02-20

### Summary

- Created `3. Data/apple-health/export_sample.json` with 30 days of realistic data (27 weight/BF/lean mass entries, 21 calorie entries, 31 sleep entries, 54 mindfulness sessions)
- Created `2. Dashboard/modules/__init__.py` and `2. Dashboard/modules/apple_health.py` with 5 parsing functions
- Replaced `layouts/health.py` with full stats row + weight trend chart + calories bar chart
- Replaced `layouts/sleep.py` with avg sleep stat + nightly bar chart
- Replaced `layouts/learning.py` left panel with study hours total, progress bar, daily chart; DS placeholder preserved
- Updated `app.py`: static `app.layout` replaced with `serve_layout()` function
- Updated `CLAUDE.md`, `context/tech-stack.md`, `context/module-roadmap.md`

### Deviations from Plan

- Step 8 (local test): Full HTTP server test was not possible due to disk space constraints in the temp filesystem. Validated instead by: (1) importing all modules and running `serve_layout()` without errors, (2) calling all 4 `apple_health.get_*()` functions and verifying correct values against sample data. All checks passed.

### Issues Encountered

- macOS does not have the `timeout` command; worked around by using background process with `kill` after sleep.
- `.venv` activation via `source activate` did not expose packages correctly in subshell; resolved by using the venv Python binary directly (`/path/to/.venv/bin/python`).
- Disk space issue in Claude Code temp filesystem prevented running a full server process; used direct Python import validation instead.
