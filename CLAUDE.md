# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

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

---

## The Claude-User Relationship

Claude operates as an **agent assistant** with access to the workspace folders, context files, commands, and outputs. The relationship is:

- **User (Zach)**: Defines goals, directs work through commands, provides credentials when needed
- **Claude**: Reads context, understands objectives, executes commands, produces outputs, maintains workspace consistency

Claude should always orient itself through `/prime` at session start, then act with full awareness of who the user is, what they're trying to achieve, and how this workspace supports that.

---

## Workspace Structure

```
LifeDashboard/
  CLAUDE.md                   - This file, core context, always loaded
  .env                        - Secrets (gitignored -- never commit)
  .env.example                - Template showing all required env variables
  .gitignore                  - Gitignores .env, data exports, __pycache__ etc
  docker-compose.yml          - Docker Compose stack (created in skeleton plan)
  .claude/commands/           - Slash commands
    prime.md                  - /prime: session initialization
    create-plan.md            - /create-plan: create implementation plans
    implement.md              - /implement: execute plans
  context/                    - Project context, read by /prime
    personal-info.md          - User profile and goals
    project.md                - Life Dashboard description
    data-sources.md           - All data sources and connection methods
    tech-stack.md             - Tech stack decisions
    module-roadmap.md         - Build order and status (update after each module)
  plans/                      - Implementation plans (one per module)
  2. Dashboard/               - Dash app (app.py, layouts/, assets/)
  3. Data/                    - Data files written by sync scripts
    apple-health/             - JSON from Health Auto Export webhook
    finances/                 - Up Bank transaction cache
    investments/              - Google Sheets portfolio cache
    strava/                   - Strava activity cache
    google-calendar/          - Calendar events cache
    dreaming-spanish/         - Dreaming Spanish scraped data
  modules/                    - Data fetch and processing scripts (one per source)
  config/                     - Google OAuth credentials (gitignored)
  scripts/                    - Utility scripts
  1. Archive/                 - Old code, ignore entirely
```

---

## Commands

### /prime

**Purpose:** Initialize a new session with full context awareness.

Run this at the start of every session. Claude will:

1. Read CLAUDE.md and all context/ files
2. Summarize understanding of the project, current module status, and next steps
3. Confirm readiness to assist

### /create-plan [request]

**Purpose:** Create a detailed implementation plan before making changes.

Use before building each module or making structural changes. Produces a thorough plan
document in `plans/` that captures context, rationale, and step-by-step tasks.

Example: `/create-plan apple-health-module`

### /implement [plan-path]

**Purpose:** Execute a plan created by /create-plan.

Reads the plan, executes each step in order, validates the work, and updates the plan status.

Example: `/implement plans/2026-02-20-apple-health-module.md`

---

## Critical Instruction: Maintain This File

**Whenever Claude makes changes to the workspace, Claude MUST consider whether CLAUDE.md needs updating.**

After any change, ask:

1. Does this change modify the workspace structure documented above?
2. Does it add a new command, module, or pattern?
3. Should `context/module-roadmap.md` be updated?

If yes to any, update the relevant sections.

---

## Session Workflow

1. **Start**: Run `/prime` to load context
2. **Check**: Review `context/module-roadmap.md` for next module to build
3. **Plan**: Run `/create-plan [module-name]` to create an implementation plan
4. **Execute**: Run `/implement [plan-path]` to build the module
5. **Update**: Mark the module as Done in `context/module-roadmap.md`
6. **Maintain**: Update CLAUDE.md if workspace structure changed

---

## Notes

- The `1. Archive/` directory contains the old failed Streamlit dashboard -- ignore it entirely
- Each module in `modules/` has a corresponding layout in `2. Dashboard/layouts/`
- Data files in `3. Data/` are gitignored (large JSON exports) but the folders are tracked
- All API credentials go in `.env` -- never hardcode secrets
- Google OAuth credentials file lives at `config/google-credentials.json` (gitignored)
