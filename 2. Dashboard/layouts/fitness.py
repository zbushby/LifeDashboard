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
