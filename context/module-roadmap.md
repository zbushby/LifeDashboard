# Module Roadmap

Track the build status of each Life Dashboard module.
Update this file after completing each module.

IMPORTANT: Each module is built end-to-end in one session -- data pipeline AND
dashboard view together. A module is only "Done" when real data is visible on screen.

---

## Build Status

| # | Module | Data Source | Status | Plan File |
|---|--------|-------------|--------|-----------|
| 0 | Foundation + Dash skeleton | Docker + Dash app shell | Not started | plans/2026-02-20-foundation-and-context-setup.md |
| 1 | Apple Health | Health Auto Export -> webhook | Not started | -- |
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
| .env.example created | Not started |
| Docker Compose file created | Not started |
| Dash app shell created (app.py) | Not started |
| Dark theme applied and dashboard loads | Not started |

---

## Completed Modules

None yet.

---

## Next Steps

1. Run `/implement plans/2026-02-20-foundation-and-context-setup.md` to finish
   the foundation (folder structure, .env.example, etc.)
2. Run `/create-plan docker-dash-skeleton` to plan the Docker + Dash app shell
3. Run `/create-plan apple-health-module` to plan Module 1
