# Module Roadmap

Track the build status of each Life Dashboard module.
Update this file after completing each module.

IMPORTANT: Each module is built end-to-end in one session -- data pipeline AND
dashboard view together. A module is only "Done" when real data is visible on screen.

---

## Build Status

| # | Module | Data Source | Status | Plan File |
|---|--------|-------------|--------|-----------|
| 0 | Foundation + Dash skeleton | Docker + Dash app shell | Done | plans/2026-02-20-docker-dash-skeleton.md |
| 1 | Apple Health | Health Auto Export -> webhook | Done | plans/2026-02-20-apple-health-module.md |
| 2 | Finances | Up Bank API | Not started | -- |
| 3 | Google Calendar | Google Calendar API | Not started | -- |
| 4 | Gym Volume | Strava API (Hevy auto-posts) | Not started | -- |
| 5 | Investments | Google Sheets API | Not started | -- |
| 6 | Dreaming Spanish | Existing scraper | Not started | -- |
| 7 | Email Delivery | Gmail SMTP | Not started | -- |

---

## What "Done" Means for Each Module

A module is complete when ALL of the following are true:

1. Data is being fetched/synced and written to `3. Data/[module]/`
2. A layout component exists in `2. Dashboard/layouts/`
3. The layout is wired into `app.py` and shows up on the dashboard
4. Real data (not dummy/placeholder) is visible on screen

---

## Foundation Checklist (Module 0)

| Task | Status |
|------|--------|
| Context files populated | Done |
| CLAUDE.md updated | Done |
| Project folder structure created | Done |
| .env.example created | Done |
| Docker Compose file created | Done |
| Dash app shell created (app.py) | Done |
| Dark theme applied and dashboard loads | Done |

---

## Completed Modules

- **Module 0 (Foundation)**: Context files, folder structure, Docker Compose, Dash skeleton with DARKLY theme and 7 placeholder cards.
- **Module 1 (Apple Health)**: Data parser (`modules/apple_health.py`), Health/Sleep/Learning layouts with real Plotly charts, `serve_layout()` for fresh data on page refresh.

---

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

---

## Next Steps

Deploy skeleton + Apple Health module to Proxmox:
```
docker compose up --build
```
Then configure iPhone app with Proxmox IP.

Run `/create-plan finances-module` to plan Module 2.
