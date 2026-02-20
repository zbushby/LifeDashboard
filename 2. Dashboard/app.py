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


app.layout = serve_layout


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
