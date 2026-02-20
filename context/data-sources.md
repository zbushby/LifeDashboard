# Life Dashboard - Data Sources

Every data source: what it provides, how we connect, API details, current status,
and which module plan to use.

---

## Module Build Order

Each module is built end-to-end -- data pipeline AND dashboard view in the same session.

| Priority | Module | Data Source |
|----------|--------|-------------|
| 1 | Apple Health | Health Auto Export iOS app -> webhook |
| 2 | Finances | Up Bank API |
| 3 | Google Calendar | Google Calendar API |
| 4 | Gym Volume | Strava API (Hevy auto-posts) |
| 5 | Investments | Google Sheets API |
| 6 | Dreaming Spanish | Existing scraper |
| 7 | Email Delivery | Gmail SMTP |

---

## Data Sources

### 1. Apple Health

**Module plan:** Create with `/create-plan apple-health-module`
**Data folder:** `3. Data/apple-health/`

**Metrics provided:**
- Weight (kg)
- Body fat percentage
- Muscle mass
- Calories consumed
- Sleep duration and quality
- Mindfulness minutes (= study time, logged by Forest app)

**Connection method:**
- "Health Auto Export - JSON+CSV" iOS app (free tier)
- Configure to auto-push JSON to `http://[proxmox-ip]:8050/api/health-export` daily
- The Dash app has a Flask route that receives the POST and saves to `3. Data/apple-health/`

**Status:** App needs to be installed and configured on iPhone
**Notes:** Forest app logs study sessions as Apple Health mindfulness minutes automatically.
No separate Forest API needed.

---

### 2. Finances - Up Bank

**Module plan:** Create with `/create-plan finances-module`
**Data folder:** `3. Data/finances/`

**Metrics provided:**
- Weekly spending by category
- Account balances
- Income vs spend summary

**Connection method:**
- Up Bank REST API (free, personal use)
- Zach has existing API code -- integrate into `modules/finances.py`
- API token stored in `.env` as `UP_BANK_API_TOKEN`

**Status:** Existing code available, needs integration
**Docs:** https://developer.up.com.au

---

### 3. Google Calendar - BJJ and Birthdays

**Module plan:** Create with `/create-plan calendar-module`
**Data folder:** `3. Data/google-calendar/`

**Metrics provided:**
- Number of BJJ sessions this week (iPhone Shortcuts automation creates a calendar
  event every time Zach attends BJJ)
- Upcoming birthdays in the next 14 days

**Connection method:**
- Google Calendar API (free, OAuth2)
- One-time OAuth setup in Google Cloud Console
- Credentials stored as `config/google-credentials.json` (gitignored)
- Calendar IDs stored in `.env`

**Status:** OAuth credentials need to be created (one-time setup)
**Notes:** The BJJ automation is already set up on the iPhone -- it creates a calendar
event on attendance. We just read those events via the API.

---

### 4. Strava / Gym Volume

**Module plan:** Create with `/create-plan strava-module`
**Data folder:** `3. Data/strava/`

**Metrics provided:**
- Weekly gym volume (total kg lifted)
- Exercise breakdown (which lifts, sets x reps x weight)
- Number of gym sessions this week

**Connection method:**
- Strava API (free, OAuth2)
- Hevy is configured to auto-post workouts to Strava
- Each Strava activity from Hevy has full exercise details in the description text
- We call the Strava API, filter activities from Hevy, and parse the description to
  extract exercise name, sets, reps, weight
- Client ID/secret and refresh token stored in `.env`

**Status:** Need to enable Hevy -> Strava auto-post in Hevy app settings.
Strava API OAuth credentials need to be created.
**Notes:** Strava API rate limit: 100 req/15min, 1000/day -- more than enough for
a weekly sync. Strava OAuth requires a one-time browser auth flow to get the initial
refresh token. Documented in the Strava module plan.

---

### 5. Investments - Google Sheets

**Module plan:** Create with `/create-plan investments-module`
**Data folder:** `3. Data/investments/`

**Metrics provided:**
- Current portfolio value
- Individual holdings (stock name, quantity, buy price, current value, gain/loss)
- Total return

**Connection method:**
- Zach manually logs each CMC Markets trade in a Google Sheet
- We read the sheet via Google Sheets API (free)
- Can reuse the same Google Cloud project and OAuth credentials as Google Calendar
- Sheet ID stored in `.env`

**Status:** Google Sheet schema needs to be designed. Google Sheets API shares
credentials with Google Calendar -- set both up at the same time.
**Notes:** Manual trade logging is intentional. The sheet does the value calculations;
we display the results.

---

### 6. Dreaming Spanish

**Module plan:** Create with `/create-plan dreaming-spanish-module`
**Data folder:** `3. Data/dreaming-spanish/`

**Metrics provided:**
- Weekly watch time on Dreaming Spanish
- Progress stats

**Connection method:**
- Existing scraper code (to be located in the codebase)
- This is the lowest priority module

**Status:** Locate existing scraper code and integrate
**Priority:** LOWEST -- build after all other modules

---

### 7. Email Delivery

**Module plan:** Create with `/create-plan email-module`
**Depends on:** All other modules being complete

**What it does:**
- Renders the full dashboard data as a beautiful HTML email
- Sends via Gmail SMTP every Sunday evening at a configured time

**Connection method:**
- Gmail SMTP with app password (free)
- Gmail address and app password stored in `.env`
- Send time configured in `.env` (e.g. SEND_TIME=19:00)
- Triggered by APScheduler inside Docker

**Status:** Build last
