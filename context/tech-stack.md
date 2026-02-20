# Life Dashboard - Tech Stack

## Dashboard Framework: Plotly Dash

**Package:** `dash` + `dash-bootstrap-components`
**Why chosen:** Beautiful Plotly charts, full Bootstrap grid layout (mobile-responsive),
pure Python, Docker-friendly, more layout control than Streamlit (used in the failed
archive attempt).
**Theme:** Dark Bootstrap theme -- DARKLY or CYBORG. Decide during first module build.
**Port:** 8050
**Entry point:** `2. Dashboard/app.py`

---

## Charts: Plotly

Built into Dash. Used for all visualisations -- line charts, bar charts, gauges,
heatmaps etc.

---

## Scheduling: APScheduler

**Package:** `apscheduler`
**Purpose:** Runs data sync jobs on a schedule inside the Docker container.
No external cron needed.
**Pattern:** Background scheduler started alongside the Dash server in `app.py`.

---

## Data Storage: JSON / CSV Files (no database)

The dashboard is a weekly summary, not real-time. Sync scripts write JSON/CSV to
`3. Data/[source]/` directories. Dash reads from those files at render time.
No database needed -- keeps the stack simple and portable.

---

## Apple Health Webhook: Flask Route in Dash

Dash is built on Flask. A custom Flask route `/api/health-export` receives POST requests
from the Health Auto Export iOS app and writes the JSON payload to `3. Data/apple-health/`.
No separate web server needed.

---

## Secrets: .env File

**Pattern:** All API keys, tokens, and credentials live in a `.env` file at the project root.
**Gitignore:** `.env` is gitignored -- never committed.
**Template:** `.env.example` is committed -- shows all required variables with placeholder values.
**Loading:** `python-dotenv` loads the `.env` file in all Python scripts.

### Required .env variables

```
# Up Bank
UP_BANK_API_TOKEN=

# Google (Calendar + Sheets -- shared OAuth project)
GOOGLE_CREDENTIALS_FILE=config/google-credentials.json
GOOGLE_BJJ_CALENDAR_ID=
GOOGLE_BIRTHDAYS_CALENDAR_ID=
GOOGLE_INVESTMENTS_SHEET_ID=

# Strava
STRAVA_CLIENT_ID=
STRAVA_CLIENT_SECRET=
STRAVA_REFRESH_TOKEN=

# Email
GMAIL_ADDRESS=
GMAIL_APP_PASSWORD=
EMAIL_SEND_TO=
EMAIL_SEND_DAY=sunday
EMAIL_SEND_TIME=19:00

# Dashboard
DASHBOARD_PORT=8050
DASHBOARD_HOST=0.0.0.0
```

Google OAuth credentials (JSON file) are stored as `config/google-credentials.json`
which is also gitignored via `config/.gitignore`.

---

## Infrastructure: Docker Compose on Proxmox

- Single `docker-compose.yml` at the project root
- One container: Python + Dash + APScheduler
- Volume mounts: `3. Data/` and `config/` mounted for persistence
- Exposed port: 8050
- Accessible on home network at `http://[proxmox-ip]:8050`
- Proxmox VM runs on Zach's desktop

---

## Language: Python 3.11+

All code is Python. `requirements.txt` in `2. Dashboard/`.

## Core Dependencies

```
dash
dash-bootstrap-components
plotly
apscheduler
python-dotenv
pyyaml
requests
pandas
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

---

## Project Structure

```
LifeDashboard/
  .env                        - Secrets (gitignored)
  .env.example                - Template showing all required variables
  docker-compose.yml          - Docker Compose stack definition
  2. Dashboard/
    app.py                    - Main Dash app, Flask routes, APScheduler
    requirements.txt
    Dockerfile
    assets/
      custom.css              - Styling overrides
    layouts/
      health.py               - Apple Health dashboard section
      finances.py             - Finances dashboard section
      fitness.py              - BJJ + Gym dashboard section
      calendar_events.py      - Birthdays dashboard section
      learning.py             - Study + Dreaming Spanish section
      investments.py          - Investments dashboard section
  modules/
    apple_health.py           - Parse Health Auto Export JSON -> dataframes
    finances.py               - Up Bank API -> spending data
    calendar_sync.py          - Google Calendar API -> events
    strava.py                 - Strava API -> parse Hevy posts -> gym volume
    investments.py            - Google Sheets API -> portfolio data
    dreaming_spanish.py       - Scraper -> DS progress
  3. Data/
    apple-health/             - JSON files from Health Auto Export
    finances/                 - Up Bank transaction cache
    investments/              - Google Sheets data cache
    strava/                   - Strava activity cache
    google-calendar/          - Calendar events cache
    dreaming-spanish/         - DS scraped data
  config/
    google-credentials.json   - Google OAuth2 credentials (gitignored)
    .gitignore                - Gitignores google-credentials.json
  context/                    - Claude session context files
  plans/                      - One plan per module
  1. Archive/                 - Old code, ignore entirely
```
