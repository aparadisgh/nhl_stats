"""SweetPicks WebApp

This module creates and runs a simple web server using Dash to display relevent NHL stats.
The web app URL routing is define below.
"""

APP_VERSION = 'v1.4.0'

from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from app import app

from apps import app1
from apps import app2
from apps import expected_goalies
from apps import lineup

import config

app.layout = html.Div(
    children = [
    html.Div(
        className='container-fluid text-muted py-2',
        children=[
            dcc.Location(id='url', refresh=False),
            html.H3('The League | Advanced Analytics')
        ]),
        html.Div(
            className='nav-banner',
            children=[
                html.Div(
                    className='container-fluid text-muted py-1',
                    children=[
                        dbc.Nav(
                            [
                                dbc.NavItem(dbc.NavLink("Team Stats", href='/teams', class_name="link-light")),
                                dbc.NavItem(dbc.NavLink("Player Stats", href='/players', class_name="link-light")),
                                dbc.NavItem(dbc.NavLink("Expected Goalies", href='/goalies', class_name="link-light")), #Hidden link
                            ],
                        )
                    ]
                )
            ]

        ),
        html.Div(
            className='container-fluid text-muted p-4',
            children=[
                html.Div(id='page-content'), # Container where apps are displayed
                html.Div(
                    className='text-center text-muted p-4',
                    children=[
                        html.P(f'{APP_VERSION}')
                    ]
                )
            ]
        )
    ]
)

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    """Updates page content based on URL"""

    if pathname == '/teams' or pathname == '/':
        return app1.layout
    elif pathname == '/players':
        return app2.layout
    elif pathname == '/goalies':
        return expected_goalies.layout
    if pathname == '/dashboard':
        return lineup.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(host=config.HOST,port=config.PORT,debug=config.DEBUG)