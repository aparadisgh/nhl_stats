"""SweetPicks WebApp

This module creates and runs a simple web server using Dash to display relevent NHL stats.
The web app URL routing is define below.
"""

APP_VERSION = 'v1.4.0'

from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from app import app

from apps import app1
from apps import app2
from apps import dashboard

import config

app.layout = html.Div(
    children = [
    html.Div(
        className='container-fluid text-muted py-2',
        children=[
            dcc.Location(id='url', refresh=False),
            html.Div(id='hidden-div', style={'display':'none'}),
            html.Div(
                className="d-flex",
                children=[
                    html.Div(
                        children=[
                            html.H3('The League | Advanced Analytics'),
                        ]
                    ),
                    html.Div(
                        className="ms-auto",
                        children=[
                            html.Div(
                                className="my-auto",
                                children=[
                                    dbc.Button(
                                        "Refresh Data",
                                        id='refresh-btn',
                                        outline=True,
                                        className="my-auto",
                                        size="sm"
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]),
        html.Div(
            className='nav-banner bg-gradient',
            children=[
                html.Div(
                    className='container-fluid text-muted py-1',
                    children=[
                        dbc.Nav(
                            [
                                dbc.NavItem(
                                    dbc.NavLink("My Dashboard", href='/dashboard', class_name="link-light"),
                                ),
                                dbc.NavItem(dbc.NavLink("Team Stats", href='/teams', class_name="link-light")),
                                dbc.NavItem(dbc.NavLink("Player Stats", href='/players', class_name="link-light")),
                            ],
                        )
                    ]
                )
            ]

        ),
        html.Div(
            className='container-fluid text-muted p-4 bg-light',
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

@app.callback(
    Output('hidden-div', 'children'),
    Input('refresh-btn', 'n_clicks'),
    prevent_initial_call=True
)
def update_data(clicks):
    #print("clicked! " +str(clicks))
    exec(open('data/nhl_data_dump.py').read())
    return ""

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('url','search')
)
def display_page(pathname, search):
    """Updates page content based on URL"""

    if pathname == '/teams' or pathname == '/':
        return app1.layout
    elif pathname == '/players':
        return app2.layout
    elif pathname == '/dashboard':
        return dashboard.layout
    else:
        return 'Error 404 - Page Not Found'

if __name__ == '__main__':
    app.run_server(host=config.HOST,port=config.PORT,debug=config.DEBUG)
