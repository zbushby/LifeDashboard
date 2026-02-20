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
# Note: mindful_minutes is the name used by current versions of Health Auto Export
# mindful_session is the legacy name -- both are supported in get_study_hours()
_METRIC = {
    "weight":    "body_mass",
    "body_fat":  "body_fat_percentage",
    "lean_mass": "lean_body_mass",
    "calories":  "dietary_energy_consumed",
    "sleep":     "sleep_analysis",
    "study":     "mindful_minutes",
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
        # Real Apple Watch data uses totalSleep; legacy/manual uses asleep; fallback to qty
        hours = entry.get("totalSleep") or entry.get("asleep") or entry.get("qty", float("nan"))
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

    # Support both mindful_minutes (current) and mindful_session (legacy)
    study_entries = exports.get("mindful_minutes", []) + exports.get("mindful_session", [])
    for entry in study_entries:
        if entry["_date"] < cutoff:
            continue
        minutes = entry.get("qty", 0.0) or 0.0
        d = pd.Timestamp(entry["_date"].date())
        mask = df["date"] == d
        if mask.any():
            df.loc[mask, "study_hours"] += minutes / 60.0

    return df
