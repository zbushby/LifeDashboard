"""Finances module layout - weekly spending.

Placeholder. Replace with real content when building the Finances module.
"""
import dash_bootstrap_components as dbc
from dash import html


def layout(data_dir):
    return dbc.Card([
        dbc.CardHeader(html.H5("Finances")),
        dbc.CardBody(
            html.P(
                "Weekly spending -- Up Bank module not yet connected.",
                className="placeholder-msg",
            )
        ),
    ])
