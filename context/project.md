# Life Dashboard - Project Overview

## What This Is

A personal weekly life dashboard that aggregates data from multiple services (Apple Health,
Up Bank, Strava, Google Calendar, Google Sheets, Dreaming Spanish) into a single beautiful
Plotly Dash interface. Viewed on Sunday evenings via the home network.
Eventually also delivered as a weekly HTML email to Gmail.

## Purpose

To have a single place that answers: "How did this week actually go?" -- across health,
fitness, finances, learning, and social life. No manual data entry (except investments) --
everything else pulls automatically from connected services.

## Weekly Review Use Case

Every Sunday evening, open the dashboard at http://[proxmox-ip]:8050 and review:

**Health**
- Did my weight trend toward 70kg?
- Is body fat moving toward sub-12%?
- How were sleep duration and quality?
- Did I hit my calorie targets?

**Fitness**
- Did I get to BJJ 3 times this week?
- How much gym volume did I lift?

**Finances**
- How much did I spend vs income?
- How is the investment portfolio tracking?

**Learning**
- Did I hit 14 hours of study this week?
- How is Dreaming Spanish progress?

**Social**
- Whose birthday is coming up in the next 2 weeks?

## Build Approach

Modules are built one at a time, end-to-end. Each module session delivers:
1. The data pipeline (fetching, processing, writing to 3. Data/)
2. The dashboard view (Dash layout component, wired into app.py)

Real data appears on screen at the end of every module session.

## Infrastructure

- Plotly Dash app running in Docker Compose on Proxmox (desktop)
- Accessible on home network via port 8050
- Data syncs run on schedule via APScheduler inside Docker
- Secrets stored in .env file (gitignored), loaded via python-dotenv
- No cloud hosting -- fully self-hosted

## Email Delivery (Future - built last)

Once all modules are built, a weekly email is auto-sent every Sunday evening via Gmail
SMTP containing the same data as the dashboard in HTML email format.

## Module Build Order

| # | Module | Status |
|---|--------|--------|
| 0 | Docker + Dash skeleton | Not started |
| 1 | Apple Health | Not started |
| 2 | Finances (Up Bank) | Not started |
| 3 | Google Calendar (BJJ + birthdays) | Not started |
| 4 | Gym Volume (Strava / Hevy posts) | Not started |
| 5 | Investments (Google Sheets) | Not started |
| 6 | Dreaming Spanish | Not started |
| 7 | Email Delivery | Not started |

See `context/module-roadmap.md` for detailed status and plan file links.
