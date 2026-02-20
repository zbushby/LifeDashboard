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
