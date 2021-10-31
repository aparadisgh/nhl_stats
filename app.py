"""App Server Definition

It is worth noting that the Dash instance is defined in this separate app.py,
while the entry point for running the app is index.py.
This separation is required to avoid circular imports
"""

import dash
import dash_bootstrap_components as dbc

app = dash.Dash(
                __name__, 
                suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server