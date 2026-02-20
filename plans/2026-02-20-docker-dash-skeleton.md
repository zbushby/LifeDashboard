# Plan: Docker and Dash App Skeleton

**Created:** 2026-02-20
**Status:** Implemented
**Request:** Create the Docker Compose file and bare Plotly Dash app shell with dark theme, placeholder cards for each module, and the Apple Health webhook endpoint.

---

## Overview

### What This Plan Accomplishes

Creates the runnable foundation of the Life Dashboard: a Plotly Dash app with a dark Bootstrap theme, one placeholder card per module, and a working Apple Health webhook endpoint -- all containerised with Docker Compose. After implementation, `docker compose up --build` starts the dashboard at port 8050, and every placeholder card is visible in the browser.

### Why This Matters

Every subsequent module plan builds on this skeleton. Module plans simply replace their placeholder layout file with real charts and data. Without the skeleton there is nothing to run, nothing to see, and nothing to test against. This is the first thing Zach sees in a browser.

---

## Current State

### Relevant Existing Structure

```
2. Dashboard/       - contains only .gitkeep
modules/            - contains only .gitkeep
3. Data/            - all 6 subfolders exist with .gitkeep
.env.example        - exists, missing DATA_DIR variable
docker-compose.yml  - does not exist
context/tech-stack.md      - documents the intended structure
context/module-roadmap.md  - skeleton listed as Not started
```

### Gaps or Problems Being Addressed

- No runnable app exists -- nothing to open in a browser
- No Docker Compose configuration exists
- No layout structure for modules to plug into
- Apple Health webhook not yet created
- DATA_DIR not documented in .env.example

---

## Proposed Changes

### Summary of Changes

- Create `2. Dashboard/requirements.txt`
- Create `2. Dashboard/Dockerfile`
- Create `docker-compose.yml` at project root
- Create `2. Dashboard/app.py` -- main Dash app with layout, webhook, scheduler
- Create `2. Dashboard/assets/custom.css` -- dark theme polish
- Create `2. Dashboard/layouts/__init__.py`
- Create 7 placeholder layout files in `2. Dashboard/layouts/`
- Update `.env.example` -- add DATA_DIR variable
- Update `context/module-roadmap.md` -- mark skeleton as Done, fix .env.example status
- Delete `2. Dashboard/.gitkeep`

### New Files to Create

| File Path | Purpose |
| --- | --- |
| `2. Dashboard/requirements.txt` | Python package dependencies |
| `2. Dashboard/Dockerfile` | Docker image definition |
| `docker-compose.yml` | Docker Compose stack definition |
| `2. Dashboard/app.py` | Main Dash app entry point |
| `2. Dashboard/assets/custom.css` | CSS overrides for dark theme polish |
| `2. Dashboard/layouts/__init__.py` | Makes layouts a Python package |
| `2. Dashboard/layouts/health.py` | Placeholder card: body composition and calories |
| `2. Dashboard/layouts/sleep.py` | Placeholder card: sleep |
| `2. Dashboard/layouts/fitness.py` | Placeholder card: BJJ and gym volume |
| `2. Dashboard/layouts/finances.py` | Placeholder card: weekly spending |
| `2. Dashboard/layouts/investments.py` | Placeholder card: investment portfolio |
| `2. Dashboard/layouts/learning.py` | Placeholder card: study hours and Dreaming Spanish |
| `2. Dashboard/layouts/birthdays.py` | Placeholder card: upcoming birthdays |

### Files to Modify

| File Path | Changes |
| --- | --- |
| `.env.example` | Add DATA_DIR variable to Dashboard section |
| `context/module-roadmap.md` | Mark skeleton tasks as Done |

### Files to Delete

- `2. Dashboard/.gitkeep` -- replaced by real files

---

## Design Decisions

### Key Decisions Made

1. **Theme: DARKLY**: Cleaner and more readable than CYBORG for a weekly review dashboard. Professional dark look without being overly dramatic. Custom CSS overrides in `assets/custom.css` add depth and polish.

2. **Layout grid structure**: Health takes 8/12 columns (most data), Sleep takes 4/12. Fitness spans full width (two columns inside the card). Finances and Investments split 6/6. Learning takes 8/12 (two panels), Birthdays 4/12. Creates visual hierarchy.

3. **Layout functions take `data_dir` parameter**: Each layout file exports `layout(data_dir)`. The data directory is passed in at render time. When a module is built, only its layout file is replaced -- `app.py` stays unchanged.

4. **DATA_DIR environment variable**: Resolves host vs container path difference. In Docker: `/data`. In local development: `../3. Data` (relative to `2. Dashboard/`). Set via `.env` or the docker-compose environment block.

5. **APScheduler timezone: Australia/Melbourne**: The scheduler fires jobs at Melbourne local time so Sunday evening emails trigger correctly.

6. **Apple Health webhook implemented now**: The `/api/health-export` endpoint is infrastructure, not module logic. Creating it in the skeleton means the Health Auto Export app can be configured on the iPhone as soon as Docker is running on Proxmox -- before the Apple Health module is fully built.

7. **No Dash callbacks in skeleton**: Callbacks are added per module. The skeleton is purely static layout -- simpler and less error-prone.

8. **gunicorn not used yet**: Dash's built-in server is used for development and the initial Docker container. Can be swapped to gunicorn later if needed.

### Alternatives Considered

- **CYBORG theme**: More dramatic. Rejected -- harder to read for a weekly data review.
- **Separate Flask + Dash servers**: Overcomplicated. Dash's Flask server handles the webhook cleanly.
- **Gunicorn from the start**: Adds complexity for no gain at this stage.

### Open Questions

None -- all decisions made.

---

## Step-by-Step Tasks

### Step 1: Create `2. Dashboard/requirements.txt`

**Actions:**
- Create the file with minimum version pins for each dependency

**File content:**
```
dash>=2.18
dash-bootstrap-components>=1.6
plotly>=5.24
apscheduler>=3.10
python-dotenv>=1.0
requests>=2.31
pandas>=2.2
google-api-python-client>=2.100
google-auth-httplib2>=0.2
google-auth-oauthlib>=1.2
flask>=3.0
```

**Files affected:**
- `2. Dashboard/requirements.txt` (create)

---

### Step 2: Create `2. Dashboard/Dockerfile`

**Actions:**
- Create the Dockerfile using the Python 3.11-slim base image
- Dependencies are installed first (separate layer) for faster rebuilds when only code changes

**File content:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data

EXPOSE 8050

CMD ["python", "app.py"]
```

**Files affected:**
- `2. Dashboard/Dockerfile` (create)

---

### Step 3: Create `docker-compose.yml` at project root

Creates the orchestration file at the project root (not inside `2. Dashboard/`).

**Actions:**
- Create `docker-compose.yml` with a single `dashboard` service
- Mount `./3. Data` as `/data` inside the container
- Mount `./config` as `/config` for Google credentials
- Pass `.env` as the env file
- Override DATA_DIR to `/data` in the container environment

**File content:**
```yaml
services:
  dashboard:
    build:
      context: "./2. Dashboard"
      dockerfile: Dockerfile
    ports:
      - "8050:8050"
    volumes:
      - "./3. Data:/data"
      - "./config:/config"
    env_file:
      - .env
    environment:
      - DATA_DIR=/data
    restart: unless-stopped
```

**Files affected:**
- `docker-compose.yml` (create at project root)

---

### Step 4: Create `2. Dashboard/assets/custom.css`

Dash automatically serves everything in the `assets/` directory. This CSS applies on top of the DARKLY theme to give the cards a GitHub-dark-style depth and polish.

**Actions:**
- Create the `2. Dashboard/assets/` directory
- Create `custom.css` with the styles below

**File content:**
```css
/* Life Dashboard - Custom Styles */
/* Applied on top of DARKLY Bootstrap theme */

body {
    background-color: #0d1117;
}

.card {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}

.card-header {
    background-color: #21262d;
    border-bottom: 1px solid #30363d;
    border-radius: 12px 12px 0 0 !important;
    padding: 0.75rem 1.25rem;
}

.card-header h5 {
    margin: 0;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #8b949e;
}

.placeholder-msg {
    color: #484f58;
    text-align: center;
    padding: 2.5rem 1rem;
    font-size: 0.9rem;
    font-style: italic;
}

h1 {
    font-weight: 700;
    letter-spacing: -1px;
}

hr {
    border-color: #30363d;
    opacity: 1;
}
```

**Files affected:**
- `2. Dashboard/assets/custom.css` (create)

---

### Step 5: Create `2. Dashboard/layouts/__init__.py`

**Actions:**
- Create an empty `__init__.py` to make `layouts/` a Python package

**File content:** (empty file)

**Files affected:**
- `2. Dashboard/layouts/__init__.py` (create)

---

### Step 6: Create all 7 placeholder layout files

Each file exports a single `layout(data_dir)` function returning a `dbc.Card`.
These placeholder cards will be replaced with real content when each module is built.

**File: `2. Dashboard/layouts/health.py`**
```python
"""Health module layout - body composition and calories.

Placeholder. Replace with real content when building the Apple Health module.
"""
import dash_bootstrap_components as dbc
from dash import html


def layout(data_dir):
    return dbc.Card([
        dbc.CardHeader(html.H5("Health")),
        dbc.CardBody(
            html.P(
                "Body composition and calories -- Apple Health module not yet connected.",
                className="placeholder-msg",
            )
        ),
    ])
```

**File: `2. Dashboard/layouts/sleep.py`**
```python
"""Sleep module layout.

Placeholder. Replace with real content when building the Apple Health module.
"""
import dash_bootstrap_components as dbc
from dash import html


def layout(data_dir):
    return dbc.Card([
        dbc.CardHeader(html.H5("Sleep")),
        dbc.CardBody(
            html.P(
                "Sleep data -- Apple Health module not yet connected.",
                className="placeholder-msg",
            )
        ),
    ])
```

**File: `2. Dashboard/layouts/fitness.py`**
```python
"""Fitness module layout - BJJ sessions and gym volume.

Placeholder. Replace with real content when building the Calendar and Strava modules.
The card is split into two panels: BJJ (left) and Gym Volume (right).
"""
import dash_bootstrap_components as dbc
from dash import html


def layout(data_dir):
    return dbc.Card([
        dbc.CardHeader(html.H5("Fitness")),
        dbc.CardBody(
            dbc.Row([
                dbc.Col(
                    html.P(
                        "BJJ sessions -- Google Calendar module not yet connected.",
                        className="placeholder-msg",
                    ),
                    md=4,
                ),
                dbc.Col(
                    html.P(
                        "Gym volume -- Strava module not yet connected.",
                        className="placeholder-msg",
                    ),
                    md=8,
                ),
            ])
        ),
    ])
```

**File: `2. Dashboard/layouts/finances.py`**
```python
"""Finances module layout - weekly spending.

Placeholder. Replace with real content when building the Finances module.
"""
import dash_bootstrap_components as dbc
from dash import html


def layout(data_dir):
    return dbc.Card([
        dbc.CardHeader(html.H5("Finances")),
        dbc.CardBody(
            html.P(
                "Weekly spending -- Up Bank module not yet connected.",
                className="placeholder-msg",
            )
        ),
    ])
```

**File: `2. Dashboard/layouts/investments.py`**
```python
"""Investments module layout - portfolio overview.

Placeholder. Replace with real content when building the Investments module.
"""
import dash_bootstrap_components as dbc
from dash import html


def layout(data_dir):
    return dbc.Card([
        dbc.CardHeader(html.H5("Investments")),
        dbc.CardBody(
            html.P(
                "Portfolio -- Google Sheets module not yet connected.",
                className="placeholder-msg",
            )
        ),
    ])
```

**File: `2. Dashboard/layouts/learning.py`**
```python
"""Learning module layout - study hours and Dreaming Spanish.

Placeholder. Replace with real content when building the Apple Health and DS modules.
Split into two panels: Study Hours (left) and Dreaming Spanish (right).
"""
import dash_bootstrap_components as dbc
from dash import html


def layout(data_dir):
    return dbc.Card([
        dbc.CardHeader(html.H5("Learning")),
        dbc.CardBody(
            dbc.Row([
                dbc.Col(
                    html.P(
                        "Study hours (target: 14 hrs/week) -- Apple Health module not yet connected.",
                        className="placeholder-msg",
                    ),
                    md=6,
                ),
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

**File: `2. Dashboard/layouts/birthdays.py`**
```python
"""Birthdays module layout - upcoming birthdays in the next 14 days.

Placeholder. Replace with real content when building the Google Calendar module.
"""
import dash_bootstrap_components as dbc
from dash import html


def layout(data_dir):
    return dbc.Card([
        dbc.CardHeader(html.H5("Upcoming Birthdays")),
        dbc.CardBody(
            html.P(
                "Birthdays -- Google Calendar module not yet connected.",
                className="placeholder-msg",
            )
        ),
    ])
```

**Files affected:**
- `2. Dashboard/layouts/health.py` (create)
- `2. Dashboard/layouts/sleep.py` (create)
- `2. Dashboard/layouts/fitness.py` (create)
- `2. Dashboard/layouts/finances.py` (create)
- `2. Dashboard/layouts/investments.py` (create)
- `2. Dashboard/layouts/learning.py` (create)
- `2. Dashboard/layouts/birthdays.py` (create)

---

### Step 7: Create `2. Dashboard/app.py`

The main entry point. Imports all layout modules, assembles the grid, registers the Apple Health webhook route on the Flask server, and starts APScheduler.

**File content:**
```python
"""Life Dashboard - main application entry point."""

import json
import os
from datetime import datetime, timedelta

import dash
import dash_bootstrap_components as dbc
import flask
from apscheduler.schedulers.background import BackgroundScheduler
from dash import html
from dotenv import load_dotenv

from layouts import birthdays, finances, fitness, health, investments, learning, sleep

load_dotenv()

# Data directory: /data in Docker, ../3. Data for local dev
DATA_DIR = os.getenv("DATA_DIR", "../3. Data")


# --- App ---

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title="Life Dashboard",
    update_title=None,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
)
server = app.server  # Expose Flask server for webhook routes


# --- Helpers ---

def week_label():
    """Return a human-readable week range string for the dashboard header."""
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return f"{monday.strftime('%-d %b')} - {sunday.strftime('%-d %b %Y')}"


# --- Layout ---

app.layout = dbc.Container(
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

        # Row 2: Fitness - full width (BJJ + Gym split inside the card)
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


# --- Apple Health Webhook ---

@server.route("/api/health-export", methods=["POST"])
def health_export():
    """Receives JSON POST from Health Auto Export iOS app and saves to disk."""
    data = flask.request.get_json(force=True, silent=True)
    if data is None:
        return flask.jsonify({"status": "error", "message": "no JSON body"}), 400

    out_dir = os.path.join(DATA_DIR, "apple-health")
    os.makedirs(out_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    out_path = os.path.join(out_dir, f"export_{timestamp}.json")

    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)

    return flask.jsonify({"status": "ok", "saved": out_path}), 200


# --- Scheduler ---
# Timezone: Australia/Melbourne (Zach's local timezone)
# Data sync jobs are added here as each module is built.

scheduler = BackgroundScheduler(timezone="Australia/Melbourne")
scheduler.start()


# --- Run ---

if __name__ == "__main__":
    port = int(os.getenv("DASHBOARD_PORT", 8050))
    host = os.getenv("DASHBOARD_HOST", "0.0.0.0")
    app.run(host=host, port=port, debug=False)
```

**Files affected:**
- `2. Dashboard/app.py` (create)

---

### Step 8: Update `.env.example`

Add `DATA_DIR` to the Dashboard section so it is documented for local development.

**Actions:**
- Append `DATA_DIR=../3. Data` to the `# Dashboard` section

The Dashboard section should read:
```
# Dashboard
DASHBOARD_PORT=8050
DASHBOARD_HOST=0.0.0.0
DATA_DIR=../3. Data
```

**Files affected:**
- `.env.example`

---

### Step 9: Delete `2. Dashboard/.gitkeep`

Real files now exist in `2. Dashboard/` so the placeholder is no longer needed.

**Actions:**
- Delete `2. Dashboard/.gitkeep`

**Files affected:**
- `2. Dashboard/.gitkeep` (delete)

---

### Step 10: Update `context/module-roadmap.md`

Mark the Docker + Dash skeleton tasks as Done.

**Actions:**
- Change Foundation Status table entries to Done:
  - `.env.example created` -> Done (was already created in foundation plan)
  - `Docker Compose file created` -> Done
  - `Dash app shell created (app.py)` -> Done
  - `Dark theme applied and dashboard loads` -> Done (verified in validation step)
- Update Module 0 row Status from "Not started" to "Done"
- Update Module 0 Plan File to reference this plan
- Update the Next Steps section

**Files affected:**
- `context/module-roadmap.md`

---

### Step 11: Validate

**Actions:**

Local run test:
```
cd "2. Dashboard"
pip install -r requirements.txt
DATA_DIR="../3. Data" python app.py
```
Then open http://localhost:8050 and confirm:
- Dark background loads correctly
- Week header shows correct date range
- All 7 placeholder cards are visible
- No Python errors in the terminal

Docker build test (no need to run, just confirm it builds):
```
docker compose build
```
Confirm the build completes without errors.

---

## Connections and Dependencies

### Files That Reference This Area

- `context/tech-stack.md` -- documents the structure this plan implements
- `context/module-roadmap.md` -- tracks skeleton status
- All future module plans -- will modify `2. Dashboard/layouts/*.py` files

### Updates Needed for Consistency

- `context/module-roadmap.md` -- updated in Step 10

### Impact on Existing Workflows

- This is the foundation every module builds on
- The DATA_DIR pattern must be followed consistently: read all data from `os.path.join(DATA_DIR, "source-name/")`
- `app.py` should not need changes when adding modules -- only the layout files change

---

## Validation Checklist

- [ ] `2. Dashboard/requirements.txt` exists with all dependencies
- [ ] `2. Dashboard/Dockerfile` exists
- [ ] `docker-compose.yml` exists at project root
- [ ] `2. Dashboard/app.py` exists
- [ ] `2. Dashboard/assets/custom.css` exists
- [ ] `2. Dashboard/layouts/__init__.py` exists
- [ ] All 7 layout files exist in `2. Dashboard/layouts/`
- [ ] `.env.example` contains `DATA_DIR` in the Dashboard section
- [ ] `2. Dashboard/.gitkeep` deleted
- [ ] `context/module-roadmap.md` shows skeleton as Done
- [ ] `python app.py` starts without errors (run from `2. Dashboard/` with DATA_DIR set)
- [ ] Dashboard loads in browser at localhost:8050 with dark theme and 7 placeholder cards
- [ ] `docker compose build` completes without errors

---

## Success Criteria

The implementation is complete when:

1. `DATA_DIR="../3. Data" python app.py` (run from inside `2. Dashboard/`) starts without errors and the dashboard is visible at localhost:8050.
2. The dashboard shows the correct dark theme, the current week header, and all 7 placeholder cards with their module names.
3. `docker compose build` completes without errors.

---

## Notes

- The `%-d` and `%-I` strftime codes (no leading zero padding) work on Linux and macOS. On the Proxmox VM (Linux) they work fine. If there are ever display issues, replace with `%d` and strip the leading zero in Python.
- The Apple Health webhook is live immediately after `docker compose up`. Configure the Health Auto Export iOS app to POST to `http://[proxmox-ip]:8050/api/health-export` as soon as Docker is running on Proxmox -- before the Apple Health module is even built.
- The `modules/` directory stays empty until Module 1 (Apple Health). The layout files in `2. Dashboard/layouts/` are the only per-module code in the skeleton.
- When each module is built, only its `2. Dashboard/layouts/*.py` file is replaced. `app.py` does not change between modules.
- For local development without Docker: copy `.env.example` to `.env`, set `DATA_DIR=../3. Data`, and run `python app.py` from inside `2. Dashboard/`.

---

## Implementation Notes

**Implemented:** 2026-02-20

### Summary

All 13 files created as specified. Dependencies installed into project venv. Validation
confirmed: app.py imports cleanly, all 7 layout modules load, week_label() returns correct
date range, Apple Health webhook route is registered, APScheduler is running.

### Deviations from Plan

None.

### Issues Encountered

- System `python3` does not have packages installed -- used project `.venv` instead.
  This is expected; packages are installed in the project virtualenv.
