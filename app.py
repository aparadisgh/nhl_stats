# -*- coding: utf-8 -*-
"""SweetPicks WebApp

This module creates a simple web server using Dash to display relevent NHL stats. The web app layout is define below.
"""
import datetime
import json

import requests
import pandas as pd

import dash
from dash import dash_table
from dash import html
import dash_bootstrap_components as dbc

from utils import the_league
from utils import nhl_stats
import config

startDate = the_league.get_next_monday()
endDate = startDate + datetime.timedelta(days=6)
startDate_str = startDate.strftime('%Y-%m-%d')
endDate_str = endDate.strftime('%Y-%m-%d')

df = nhl_stats.get_next_week(startDate_str, endDate_str)
sorted_df = df.sort_values(by=['Nombre de matchs'], ascending=False)

external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
                className="container-sm text-muted p-4",
                children=[
                    html.H1("SweetPicks.com"),
                    html.P(f"Du {startDate_str} au {endDate_str}"),
                    dash_table.DataTable(
                        id='table',
                        columns=[{"name": i, "id": i} for i in df.columns],
                        data=sorted_df.to_dict('records'),
                        sort_action='native',
                        filter_action="native",
                        style_data_conditional=[
                            {
                                'if': {'column_id': 'Nombre de matchs'},
                                'textAlign': 'left'
                            },
                            {
                                'if': {
                                    'filter_query': f"{{Nombre de matchs}} = {df['Nombre de matchs'].max()}",
                                },
                                'backgroundColor': 'rgb(102, 255, 102)',
                                'color': 'rgb(64, 64, 64)',
                                'fontWeight': 'bold'
                            }]
                    )]
            )

if __name__ == '__main__':
    app.run_server(host=config.HOST,port=config.PORT,debug=config.DEBUG)