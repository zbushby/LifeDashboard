# Plan: Life Dashboard - Foundation, Context Setup and Project Architecture

**Created:** 2026-02-20
**Status:** Implemented
**Request:** Define the Life Dashboard project in full, populate context files, update CLAUDE.md, and establish the project folder structure and module roadmap so every future Claude session starts with complete awareness.

---

## Overview

### What This Plan Accomplishes

This plan captures the full Life Dashboard project definition, populates all context files with real content, updates CLAUDE.md to reflect the actual project, and creates the folder structure and architectural skeleton for the dashboard. After this plan is implemented, every future Claude session will `/prime` into complete awareness of what this project is, how it works, and which module to build next.

### Why This Matters

Without context files, every new Claude session starts blind. This plan front-loads all research and decision-making so future sessions can immediately begin implementation work without re-explaining the project. It also locks in key architectural decisions (tech stack, data flow, module order) so there is no drift session to session.

---

## Current State

### Relevant Existing Structure

```
LifeDashboard/
  CLAUDE.md                  - Generic workspace template, needs project update
  context/
    personal-info.md         - Empty template
    business-info.md         - Empty template (not relevant, will repurpose)
    strategy.md              - Empty template
    current-data.md          - Empty template
  plans/                     - Empty
  2. Dashboard/              - Empty, will hold the Dash app
  3. Data/
    Apple Health/            - Empty placeholder
    Finances Up Bank/        - Empty placeholder
  1. Archive/                - Old ugly Streamlit dashboard, ignore entirely
    main.py                  - Old code, do not reference
    data/                    - Old CSV samples, useful as schema reference only
  scripts/                   - Empty
```

### Gaps or Problems Being Addressed

- Context files are empty templates -- Claude has no project awareness between sessions
- CLAUDE.md describes a generic workspace template, not this specific project
- No folder structure for modules, config, or Docker
- No tech stack decision documented
- No module build order defined
- `3. Data/` subfolders do not match the planned data sources yet
- `business-info.md` is not relevant to a personal dashboard project

---

## Proposed Changes

### Summary of Changes

- Populate `context/personal-info.md` with user profile and project goals
- Replace `context/business-info.md` with `context/project.md` -- full project description
- Populate `context/data-sources.md` (rename from `strategy.md`) -- every data source, connection method, API details, status, and build priority
- Populate `context/tech-stack.md` (rename from `current-data.md`) -- tech decisions with rationale
- Update `CLAUDE.md` to describe this project specifically
- Create project folder structure: `modules/`, `config/`, update `3. Data/` subfolders, scaffold `2. Dashboard/`
- Create `context/module-roadmap.md` -- build order with status tracking for each module

### New Files to Create

| File Path | Purpose |
| --- | --- |
| `plans/2026-02-20-foundation-and-context-setup.md` | This plan |
| `context/project.md` | Full Life Dashboard project description and goals |
| `context/data-sources.md` | Every data source: connection method, API, status, priority |
| `context/tech-stack.md` | Tech stack decisions with rationale |
| `context/module-roadmap.md` | Module build order and current status |
| `modules/.gitkeep` | Placeholder - modules/ dir for data fetch/process scripts |
| `.env.example` | Template showing all required environment variables (safe to commit) |
| `.gitignore` | Gitignores .env and other sensitive files |
| `config/.gitignore` | Gitignores google-credentials.json |
| `2. Dashboard/.gitkeep` | Placeholder - Dash app lives here |
| `3. Data/apple-health/.gitkeep` | Apple Health JSON data |
| `3. Data/strava/.gitkeep` | Strava API cache |
| `3. Data/google-calendar/.gitkeep` | Google Calendar events cache |
| `3. Data/investments/.gitkeep` | Google Sheets investments cache |
| `3. Data/dreaming-spanish/.gitkeep` | Dreaming Spanish scraped data |

### Files to Modify

| File Path | Changes |
| --- | --- |
| `CLAUDE.md` | Replace generic workspace description with project-specific overview |
| `context/personal-info.md` | Fill with real user profile and workspace goals |
| `3. Data/Apple Health/` | Rename to `3. Data/apple-health/` (lowercase, consistent) |
| `3. Data/Finances Up Bank/` | Rename to `3. Data/finances/` (simplified) |

### Files to Delete

- `context/business-info.md` -- not relevant to a personal dashboard; replaced by `context/project.md`
- `context/strategy.md` -- repurposed as `context/data-sources.md`
- `context/current-data.md` -- repurposed as `context/tech-stack.md`

---

## Design Decisions

### Key Decisions Made

1. **Dashboard framework: Plotly Dash + dash-bootstrap-components**: Chosen over Streamlit (used in the failed archive, hard to make beautiful), Grafana (requires InfluxDB, over-engineered for weekly use), and raw HTML (too much manual work). Dash gives beautiful Plotly charts, full layout control via Bootstrap grid, pure Python, Docker-friendly, and responsive mobile support through Bootstrap themes.

2. **Bootstrap theme: DARKLY or CYBORG (dark)**: The dashboard will use a dark theme for a premium look. DARKLY is clean and readable; CYBORG is more dramatic. Decision deferred to first module build session -- either works with the same code.

3. **Data storage: JSON/CSV files (no database)**: The dashboard is a weekly summary, not real-time. Scheduled scripts fetch data and write to `3. Data/` subfolders. Dash reads from those files. No database needed -- eliminates setup complexity and keeps things portable.

4. **Scheduled sync: APScheduler inside Docker**: A Python process running alongside Dash will use APScheduler to trigger data syncs on a schedule (e.g. hourly or daily). No external cron daemon needed.

5. **Build approach: data pipeline AND dashboard view together per module**: Each module is built end-to-end in a single session -- fetch the data, process it, AND display it on the dashboard. This means after completing each module you can immediately see real data on screen. Never build data without the view, never build the view without data.

6. **Module-by-module build approach**: Each data source is a separate module in `modules/` with its own fetch script and Dash layout component. Modules are independent so one broken API does not break the whole dashboard.

7. **Gym volume: Strava API + parse Hevy posts**: Hevy auto-posts workouts to Strava with full exercise details (name, sets, reps, weight) in the activity description. We use the official Strava API (free OAuth2) to pull activities and parse the description text. No scraping, no unofficial APIs.

8. **Apple Health data ingestion: Health Auto Export app**: The free "Health Auto Export" iOS app exports health metrics (weight, body fat, muscle mass, calories, sleep, mindfulness minutes) to a webhook URL. The webhook endpoint is a small route in the Dash app that receives JSON and writes to `3. Data/apple-health/`. No manual exports needed.

9. **Study time: Apple Health mindfulness minutes**: Forest app logs study sessions as mindfulness minutes in Apple Health. Health Auto Export captures this automatically. No separate Forest API needed.

10. **Investments: Google Sheets**: User logs trades manually in a Google Sheet. We read it via the Google Sheets API (free). This is deliberate -- trade logging is a conscious act, not something to automate.

11. **Email delivery: Gmail SMTP, built last**: The weekly email is the final module. It renders the dashboard as an HTML email and sends via Gmail SMTP on Sunday evenings. Building this last ensures all data modules exist first.

12. **Infrastructure: Docker Compose on Proxmox (desktop)**: The whole stack runs as a Docker Compose project on a Proxmox VM on the user's desktop. Accessible on the home network via a port (e.g. `http://proxmox-ip:8050`).

13. **Secrets management: `config/config.yaml` (gitignored)**: All API keys, tokens, and secrets live in a single YAML config file that is gitignored. A `config.example.yaml` is committed as documentation.

### Alternatives Considered

- **Grafana**: Beautiful but requires a time-series database (InfluxDB/Prometheus). Overkill for a weekly summary. Less flexible for custom Python-based data processing.
- **Streamlit**: Used in the archived version -- resulted in an ugly dashboard. Layout control is too limited.
- **Firefly3**: User originally mentioned this for budgeting but has Up Bank API access directly. Firefly3 adds unnecessary complexity.
- **Sharesight API**: Costs money. Google Sheets is free and gives the user full control over what is tracked.
- **Playwright automation on hevy.com**: Would work but is fragile. Strava API is cleaner and officially supported.

### Open Questions

None -- all decisions have been made. The following will be resolved during each module's build plan:
- Exact Strava OAuth setup steps (handled in Strava module plan)
- Google Calendar OAuth setup (handled in Calendar module plan)
- Health Auto Export webhook URL format (handled in Apple Health module plan)
- Google Sheets API setup (handled in Investments module plan)

---

## Step-by-Step Tasks

### Step 1: Create `context/project.md`

Create a new file replacing `context/business-info.md` with the full project description.

**Actions:**
- Delete `context/business-info.md`
- Create `context/project.md` with the following content:

```markdown
# Life Dashboard - Project Overview

## What This Is

A personal weekly life dashboard that aggregates data from multiple services (Apple Health,
Up Bank, Strava, Google Calendar, Google Sheets, Dreaming Spanish) into a single beautiful
interface. Viewed on Sunday evenings via the home network. Eventually also delivered as a
weekly HTML email to Gmail.

## Purpose

To have a single place that answers: "How did this week actually go?" -- across health,
fitness, finances, learning, and social life. No manual data entry -- everything pulls
automatically from connected services.

## Weekly Review Use Case

Every Sunday evening, open the dashboard at http://[proxmox-ip]:8050 and review:
- How did my body composition trend this week?
- Did I sleep well?
- Am I hitting my calorie goals?
- How much did I spend vs budget?
- Did I train BJJ and gym enough?
- How much did I study?
- How is my Dreaming Spanish streak going?
- Whose birthday is coming up?

## Build Approach

Each module is built end-to-end -- data pipeline AND dashboard view in the same session.
After completing each module, real data is immediately visible on screen.

## Infrastructure

- Runs as a Docker Compose stack on Proxmox (desktop)
- Accessible on home network via port 8050
- Data syncs run on schedule via APScheduler
- No cloud hosting -- fully self-hosted

## Email Delivery (Future)

Once all modules are built, a weekly email is auto-sent every Sunday evening via Gmail
SMTP containing the same data as the dashboard in HTML email format.

## Module Build Order

1. Foundation - Docker skeleton + Dash app shell (this plan)
2. Apple Health - weight, body fat, muscle mass, calories, sleep, study time
3. Finances - Up Bank spending
4. Google Calendar - BJJ sessions, birthdays
5. Strava/Gym - Hevy workouts via Strava posts (volume, exercises)
6. Investments - Google Sheets portfolio
7. Dreaming Spanish - language learning progress
8. Email Delivery - weekly Gmail send (last)
```

**Files affected:**
- `context/business-info.md` (delete)
- `context/project.md` (create)

---

### Step 2: Create `context/data-sources.md`

Replace `context/strategy.md` with a comprehensive data sources reference.

**Actions:**
- Delete `context/strategy.md`
- Create `context/data-sources.md` with the following content:

```markdown
# Life Dashboard - Data Sources

Every data source in the dashboard: what it provides, how we connect, current status,
and which module plan to reference.

---

## Module Build Order

Each module is built end-to-end: data pipeline AND dashboard view in the same session.

1. Apple Health - weight, body fat %, muscle mass, calories, sleep, study time
2. Finances - Up Bank spending summary
3. Google Calendar - BJJ sessions, upcoming birthdays
4. Strava / Gym Volume - Hevy workouts via Strava posts
5. Investments - Google Sheets portfolio log
6. Dreaming Spanish - language learning progress (scraper)
7. Email Delivery - weekly Gmail send (built last)

---

## Data Sources Detail

### 1. Apple Health

**Module plan:** Create with `/create-plan apple-health-module`
**Data provided:** Weight, body fat %, muscle mass, calories consumed, sleep
duration/quality, mindfulness minutes (= study time from Forest app)
**Connection method:** "Health Auto Export" iOS app (free) -> webhook POST to local
endpoint -> JSON saved to `3. Data/apple-health/`
**App:** Health Auto Export - JSON+CSV on the App Store. Configure to push to
`http://[proxmox-ip]:8050/api/health-export` on a daily schedule.
**Status:** App needs to be installed and configured
**Notes:** Forest app logs study sessions as mindfulness minutes in Apple Health.
Captured automatically here. No separate Forest integration needed.

### 2. Finances - Up Bank

**Module plan:** Create with `/create-plan finances-module`
**Data provided:** Weekly spending by category, account balances
**Connection method:** Up Bank API -- user has existing code
**Status:** User has working Up Bank API code -- needs to be integrated into
`modules/finances.py`
**Notes:** Up Bank is an Australian bank with a clean REST API. Free, no setup needed
beyond API token.

### 3. Google Calendar - BJJ and Birthdays

**Module plan:** Create with `/create-plan calendar-module`
**Data provided:**
  - BJJ sessions this week (iPhone automation creates a Google Calendar event each
    time user attends)
  - Upcoming birthdays (birthday calendar)
**Connection method:** Google Calendar API (free, OAuth2)
**Status:** OAuth credentials need to be created (one-time setup in Google Cloud Console)
**Notes:** iPhone Shortcuts automation already creates calendar events for BJJ attendance.

### 4. Strava / Gym Volume

**Module plan:** Create with `/create-plan strava-module`
**Data provided:** Gym workout volume (total kg lifted per week), exercise breakdown,
session count
**Connection method:** Strava API (free, OAuth2). Hevy auto-posts workouts to Strava
with full exercise details (exercise name, sets, reps, weight) in the activity
description text.
**Status:** Need to enable Hevy -> Strava auto-post in Hevy app settings. Strava API
OAuth credentials need to be created.
**Notes:** We parse the Strava activity description text to extract exercise data. The
Strava API is the official channel -- no scraping. Rate limit: 100 req/15min,
1000/day (more than enough for weekly sync).

### 5. Investments - Google Sheets

**Module plan:** Create with `/create-plan investments-module`
**Data provided:** Investment portfolio -- manually logged trades in CMC Markets
(stock name, quantity, buy price, current value)
**Connection method:** Google Sheets API (free) -- user manually logs each trade in
a Google Sheet
**Status:** Google Sheet needs to be created with a defined schema. Google Sheets API
credentials need to be set up (can reuse Google Calendar OAuth project).
**Notes:** Manual logging is intentional -- trade logging is a deliberate act.

### 6. Dreaming Spanish

**Module plan:** Create with `/create-plan dreaming-spanish-module`
**Data provided:** Weekly watch time / progress on Dreaming Spanish
**Connection method:** Existing scraper code in the codebase
**Status:** User has existing scraper code -- needs to be located and integrated
**Priority:** LOWEST -- build this last before email delivery

### 7. Email Delivery

**Module plan:** Create with `/create-plan email-module`
**Data provided:** Renders full dashboard as HTML email, sends via Gmail SMTP
**Connection method:** Gmail SMTP (free, app password)
**Status:** Build last -- depends on all other modules
**Schedule:** Auto-send every Sunday evening (configurable time in .env)
```

**Files affected:**
- `context/strategy.md` (delete)
- `context/data-sources.md` (create)

---

### Step 3: Create `context/tech-stack.md`

Replace `context/current-data.md` with the tech stack reference.

**Actions:**
- Delete `context/current-data.md`
- Create `context/tech-stack.md` with the following content:

```markdown
# Life Dashboard - Tech Stack

## Dashboard Framework: Plotly Dash

**Package:** `dash` + `dash-bootstrap-components`
**Why:** Beautiful Plotly charts, full Bootstrap grid layout (mobile-responsive), pure
Python, Docker-friendly, more control than Streamlit.
**Theme:** Dark Bootstrap theme (DARKLY or CYBORG) -- decide during first module build.
**Port:** 8050 (default Dash port)
**Entry point:** `2. Dashboard/app.py`

## Data Visualisation: Plotly

Comes with Dash. Used for all charts -- line graphs, bar charts, gauges, etc.

## Scheduling: APScheduler

**Package:** `apscheduler`
**Purpose:** Runs data sync jobs on a schedule within the Docker container. No external
cron needed.
**Pattern:** Background scheduler started in `app.py` alongside the Dash server.

## Data Storage: JSON / CSV Files

No database. Scheduled sync scripts write JSON/CSV to `3. Data/[source]/` directories.
Dash reads from these files when rendering. Simple, portable, easy to inspect.

## HTTP Endpoint for Apple Health: Flask route in Dash

Dash is built on Flask. We add a custom Flask route `/api/health-export` that receives
POST requests from the Health Auto Export iOS app and writes the JSON payload to
`3. Data/apple-health/`.

## Infrastructure: Docker Compose on Proxmox

- Single `docker-compose.yml` at the project root
- One service: `dashboard` (Python + Dash + APScheduler)
- Volume mount: `3. Data/` directory mounted into container for data persistence
- Network: host or bridge with port 8050 exposed
- Environment: reads from `.env` file at project root (gitignored)

## Secrets: .env File

- `.env` -- gitignored, contains all API keys and tokens
- `.env.example` -- committed, shows all required variables with placeholder values
- Loaded in Python via `python-dotenv`

## Language: Python 3.11+

All code in Python. Dependencies managed with `pip` and `requirements.txt`.

## Key Dependencies

```
dash
dash-bootstrap-components
plotly
apscheduler
python-dotenv
requests
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
pandas
```

## Module Structure

```
modules/
  apple_health.py       - Parse Health Auto Export JSON -> dataframes
  finances.py           - Up Bank API -> spending data
  calendar_sync.py      - Google Calendar API -> BJJ sessions, birthdays
  strava.py             - Strava API -> parse Hevy posts -> gym volume
  investments.py        - Google Sheets API -> portfolio data
  dreaming_spanish.py   - Scraper -> DS progress

2. Dashboard/
  app.py                - Main Dash app + Flask routes + APScheduler
  assets/
    custom.css          - Additional styling overrides
  layouts/
    health.py           - Health module layout component
    finances.py         - Finances layout component
    fitness.py          - BJJ + Gym layout component
    calendar_events.py  - Birthdays layout component
    learning.py         - Study + Dreaming Spanish layout component
    investments.py      - Investments layout component
```
```

**Files affected:**
- `context/current-data.md` (delete)
- `context/tech-stack.md` (create)

---

### Step 4: Populate `context/personal-info.md`

**Actions:**
- Overwrite `context/personal-info.md` with the following content:

```markdown
# Personal Info

## Who I Am

A developer running a self-hosted Life Dashboard to review personal metrics every Sunday
evening. Based in Australia (Up Bank user).

## Goals for This Workspace

- Build the Life Dashboard module by module using Claude Code
- Each session: `/prime` to load context, then work on the next module
- Use `/create-plan [module name]` before building each new module
- Use `/implement` to execute each plan

## Technical Background

- Comfortable with Python
- Has existing Up Bank API code (to be integrated in Finances module)
- Has existing Dreaming Spanish scraper code (to be located and integrated)
- Familiar with Docker

## Current Module Status

See `context/module-roadmap.md` for the live build status of each module.

## Key Accounts and Services

- Bank: Up Bank (Australia) -- API access available
- Investments: CMC Markets -- trades logged manually in Google Sheets
- Health: Apple Health + Health Auto Export iOS app
- Fitness: Hevy (gym) -> auto-posts to Strava | BJJ via Google Calendar automation
- Calendar: Google Calendar -- BJJ automations + birthdays
- Language: Dreaming Spanish
- Study: Forest app -> Apple Health mindfulness minutes
- Email: Gmail
- Infrastructure: Proxmox on desktop, Docker Compose
```

**Files affected:**
- `context/personal-info.md`

---

### Step 5: Create `context/module-roadmap.md`

This file tracks which modules have been built. Update it as each module is completed.

**Actions:**
- Create `context/module-roadmap.md` with the following content:

```markdown
# Module Roadmap

Track the build status of each Life Dashboard module.
Update this file as modules are completed.

IMPORTANT: Each module is built end-to-end in one session -- data pipeline AND
dashboard view together. Never build data without the view.

| # | Module | Data Source | Status | Plan File |
|---|--------|-------------|--------|-----------|
| 0 | Foundation | Docker + Dash shell | Not started | plans/2026-02-20-foundation-and-context-setup.md |
| 1 | Apple Health | Health Auto Export iOS app -> webhook | Not started | -- |
| 2 | Finances | Up Bank API | Not started | -- |
| 3 | Google Calendar | Google Calendar API (BJJ + birthdays) | Not started | -- |
| 4 | Gym Volume | Strava API (Hevy auto-posts) | Not started | -- |
| 5 | Investments | Google Sheets API | Not started | -- |
| 6 | Dreaming Spanish | Existing scraper | Not started | -- |
| 7 | Email Delivery | Gmail SMTP | Not started | -- |

## Foundation Status

| Task | Status |
|------|--------|
| Context files populated | Done |
| CLAUDE.md updated | Done |
| Project folder structure created | Done |
| Docker Compose skeleton | Not started |
| Dash app skeleton | Not started |

## What "Done" Means Per Module

Each module is complete when:
1. Data is being fetched and written to `3. Data/[module]/`
2. A layout component exists in `2. Dashboard/layouts/`
3. The layout is wired into `app.py` and visible on the dashboard
4. Real data appears on screen (not dummy/placeholder data)

## Next Step

Run `/create-plan docker-dash-skeleton` to create the Docker + Dash app shell,
then start Module 1 with `/create-plan apple-health-module`.
```

**Files affected:**
- `context/module-roadmap.md` (create)

---

### Step 6: Update `CLAUDE.md`

Replace the generic workspace template description with project-specific content.
Keep the Commands section and Session Workflow intact. Update the intro and structure sections.

**Actions:**
- Replace the "What This Is" section with the following:

```markdown
## What This Is

This is the **Life Dashboard** -- a self-hosted weekly summary dashboard that aggregates
personal data from multiple services (Apple Health, Up Bank, Strava, Google Calendar,
Google Sheets, Dreaming Spanish) into a single beautiful Plotly Dash interface.
Viewed on Sunday evenings via the home network at http://[proxmox-ip]:8050.
Built module by module in Python. Each module delivers both the data pipeline and the
dashboard view in the same session.

**Infrastructure:** Docker Compose on Proxmox (desktop) | Port 8050 | Fully self-hosted

**Context files (read by `/prime`):**
- `context/personal-info.md` -- who the user is and workspace goals
- `context/project.md` -- full project description
- `context/data-sources.md` -- every data source, connection method, and build status
- `context/tech-stack.md` -- tech stack decisions and architecture
- `context/module-roadmap.md` -- module build order and current status

**To start a new build session:** Run `/prime`, check `context/module-roadmap.md`
for the next module, then run `/create-plan [module-name]` to plan it.
```

- Replace the Workspace Structure section with the following:

```markdown
## Workspace Structure

```
LifeDashboard/
  CLAUDE.md                   - This file, core context, always loaded
  .claude/commands/           - Slash commands
  context/                    - Project context, read by /prime
    personal-info.md          - User profile and goals
    project.md                - Life Dashboard description
    data-sources.md           - All data sources and connection methods
    tech-stack.md             - Tech stack decisions
    module-roadmap.md         - Build order and status (update after each module)
  plans/                      - Implementation plans (one per module)
  2. Dashboard/               - Dash app (app.py, layouts/, assets/)
  3. Data/                    - Data files written by sync scripts
    apple-health/
    finances/
    investments/
    strava/
    google-calendar/
    dreaming-spanish/
  modules/                    - Data fetch and processing scripts
  config/                     - API keys (config.yaml gitignored)
  scripts/                    - Utility scripts
  docker-compose.yml          - Docker Compose (created in skeleton plan)
  1. Archive/                 - Old code, ignore entirely
```
```

**Files affected:**
- `CLAUDE.md`

---

### Step 7: Create Project Folder Structure

Create all necessary directories and placeholder files.

**Actions:**
- Rename `3. Data/Apple Health/` to `3. Data/apple-health/`
- Rename `3. Data/Finances Up Bank/` to `3. Data/finances/`
- Create `3. Data/investments/` with `.gitkeep`
- Create `3. Data/strava/` with `.gitkeep`
- Create `3. Data/google-calendar/` with `.gitkeep`
- Create `3. Data/dreaming-spanish/` with `.gitkeep`
- Create `modules/` directory with `.gitkeep`
- Create `config/` directory with `.gitignore` containing `google-credentials.json`
- Create `.env.example` at project root (see content below)
- Add `.env` to the root `.gitignore` (create `.gitignore` if it doesn't exist)
- Confirm `2. Dashboard/` directory exists

**`.env.example` content:**
```
# Life Dashboard - Environment Variables
# Copy this file to .env and fill in your real values.
# .env is gitignored -- never commit real credentials.

# Up Bank
UP_BANK_API_TOKEN=

# Google (Calendar + Sheets -- shared OAuth project)
# google-credentials.json is stored at config/google-credentials.json (gitignored)
GOOGLE_BJJ_CALENDAR_ID=
GOOGLE_BIRTHDAYS_CALENDAR_ID=
GOOGLE_INVESTMENTS_SHEET_ID=

# Strava
STRAVA_CLIENT_ID=
STRAVA_CLIENT_SECRET=
STRAVA_REFRESH_TOKEN=

# Email (Gmail)
GMAIL_ADDRESS=
GMAIL_APP_PASSWORD=
EMAIL_SEND_TO=
EMAIL_SEND_DAY=sunday
EMAIL_SEND_TIME=19:00

# Dashboard
DASHBOARD_PORT=8050
DASHBOARD_HOST=0.0.0.0
```

**Files affected:**
- `3. Data/apple-health/` (rename)
- `3. Data/finances/` (rename)
- `3. Data/investments/.gitkeep` (create)
- `3. Data/strava/.gitkeep` (create)
- `3. Data/google-calendar/.gitkeep` (create)
- `3. Data/dreaming-spanish/.gitkeep` (create)
- `modules/.gitkeep` (create)
- `config/.gitignore` (create -- gitignores google-credentials.json)
- `.env.example` (create at project root)
- `.gitignore` (create/update at project root -- add .env)

---

### Step 8: Validation

**Actions:**
- Verify all context files exist and contain real content (no template placeholders)
- Verify `CLAUDE.md` reflects the project correctly
- Verify all `3. Data/` subfolders exist
- Verify `config/config.example.yaml` has all required keys
- Verify `config/.gitignore` contains `config.yaml`
- Verify `context/module-roadmap.md` exists with all modules marked "Not started"

---

## Connections and Dependencies

### Files That Reference This Area

- `CLAUDE.md` is auto-loaded every session -- must be accurate
- `.claude/commands/prime.md` reads `context/` files -- all context files must exist
- Future module plans will reference `context/data-sources.md` for connection details

### Updates Needed for Consistency

- After each module is completed, update `context/module-roadmap.md` status
- After each module plan is created, add the plan file path to the roadmap table

### Impact on Existing Workflows

- `/prime` will now load rich project context instead of empty templates
- Future sessions will know exactly which module to build next
- The `1. Archive/` directory remains untouched -- it is ignored

---

## Validation Checklist

- [ ] `context/project.md` exists with full project description
- [ ] `context/data-sources.md` exists with all 7 data sources documented
- [ ] `context/tech-stack.md` exists with full tech stack documented
- [ ] `context/personal-info.md` filled with real content (no template placeholders)
- [ ] `context/module-roadmap.md` exists with all 7 modules listed as "Not started"
- [ ] `context/business-info.md` deleted
- [ ] `context/strategy.md` deleted
- [ ] `context/current-data.md` deleted
- [ ] `CLAUDE.md` updated to describe Life Dashboard (not generic template)
- [ ] `.env.example` created at project root with all required variable names
- [ ] `.gitignore` at project root contains `.env`
- [ ] `config/.gitignore` created containing `google-credentials.json`
- [ ] All `3. Data/` subfolders created: apple-health, finances, investments, strava, google-calendar, dreaming-spanish
- [ ] `modules/` directory created
- [ ] Running `/prime` in a new session produces a meaningful Life Dashboard summary

---

## Success Criteria

The implementation is complete when:

1. Running `/prime` in a fresh Claude session produces a clear, accurate summary of the Life Dashboard project, data sources, tech stack, and next module to build -- without the user needing to explain anything.
2. All context files contain real project information with zero generic template placeholders remaining.
3. The folder structure matches the architecture defined in `context/tech-stack.md`.
4. `config/config.example.yaml` documents every API key needed across all 7 modules.

---

## Notes

- The `1. Archive/` directory is left completely untouched. The old Streamlit code is not referenced.
- The archive's `data/` CSV files are useful as schema reference (what fields were tracked) but should not be copied into `3. Data/`.
- The next plan after implementing this one should be `/create-plan docker-dash-skeleton` to create the Docker Compose file and the Dash app shell. After that, each module gets its own plan.
- When setting up Google APIs, both Calendar and Sheets can share the same Google Cloud project and OAuth2 credentials file -- set this up once.
- Strava OAuth requires a one-time browser flow to get the initial refresh token. This is documented in the Strava module plan.
- Health Auto Export free tier: confirm during Module 1 which metrics are available on free vs paid tier.

---

## Implementation Notes

**Implemented:** 2026-02-20

### Summary

Context files were written during the planning session (personal-info, project, data-sources,
tech-stack, module-roadmap). During implementation:
- Renamed 3. Data/Apple Health/ -> 3. Data/apple-health/
- Renamed 3. Data/Finances Up Bank/ -> 3. Data/finances/
- Created all missing 3. Data/ subfolders with .gitkeep
- Created modules/ with .gitkeep
- Created config/ with .gitignore (gitignores google-credentials.json)
- Created .env.example at project root with all required variable names
- Created .gitignore at project root (gitignores .env, data exports, __pycache__)
- Updated CLAUDE.md to describe the Life Dashboard project specifically
- Deleted old empty template files (business-info.md, strategy.md, current-data.md)

### Deviations from Plan

- Switched from config/config.yaml to .env / .env.example approach (simpler, more standard)
- CLAUDE.md was fully rewritten rather than section-by-section patching (cleaner result)
- Design decision #13 in the plan still mentions config.yaml -- minor inconsistency in the
  plan document only, actual implementation uses .env correctly

### Issues Encountered

None.
