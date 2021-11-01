"""SweetPicks WebApp

This module creates and runs a simple web server using Dash to display relevent NHL stats.
The web app URL routing is define below.
"""

APP_VERSION = 'v1.3.1'

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from app import app
from apps import app1, app2

app.layout = html.Div(
    className='container-xl text-muted p-4',
    children=[
        dcc.Location(id='url', refresh=False),
        html.H3('The League | Advanced Analytics'),
        dbc.Nav(
            [
                dbc.NavItem(dbc.NavLink("Team Stats", href='/teams', class_name="link-light")),
                dbc.NavItem(dbc.NavLink("Player Stats", href='/players', class_name="link-light")),
            ],
            class_name= "bg-secondary rounded-1 mt-4"
        ),
        html.Div(id='page-content'), # Container where apps are displayed
        html.Div(
            className='text-center text-muted p-4',
            children=[
                html.P(f'{APP_VERSION}')
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
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)