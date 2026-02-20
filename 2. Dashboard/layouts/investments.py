"""Investments module layout - portfolio overview.

Placeholder. Replace with real content when building the Investments module.
"""
import dash_bootstrap_components as dbc
from dash import html


def layout(data_dir):
    return dbc.Card([
        dbc.CardHeader(html.H5("Investments")),
        dbc.CardBody(
            html.P(
                "Portfolio -- Google Sheets module not yet connected.",
                className="placeholder-msg",
            )
        ),
    ])
