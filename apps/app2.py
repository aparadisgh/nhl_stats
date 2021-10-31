"""Wap2-Crack

This app is the wap2-crack
"""

from dash import html
import dash_bootstrap_components as dbc

from app import app #required for app callbacks

layout = html.Div(
    id='app-container',
    children=[
        dbc.Alert("!!! WAPTOO-CRACK !!!", color="danger")
    ]
)