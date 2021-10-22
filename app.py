# -*- coding: utf-8 -*-
"""SweetPicks WebApp

This module ...
"""
import datetime
import json

import requests
import pandas as pd

import dash
from dash import dash_table
from dash import html
import dash_bootstrap_components as dbc

from utils import league_dates
import config

startDate = league_dates.get_next_monday()
endDate = startDate + datetime.timedelta(days=6)
startDate_str = startDate.strftime('%Y-%m-%d')
endDate_str = endDate.strftime('%Y-%m-%d')

r = requests.get(f'https://statsapi.web.nhl.com/api/v1/schedule?startDate={startDate_str}&endDate={endDate_str}') # pylint: disable=line-too-long

r_dict = json.loads(r.text)

game_counts = {}
for date in r_dict['dates']:
    for game in date['games']:
        home = game['teams']['home']['team']['name']
        away = game['teams']['away']['team']['name']

        if home in game_counts:
            game_counts[home] = game_counts[home] + 1
        else:
            game_counts[home] = 1

        if away in game_counts:
            game_counts[away] = game_counts[away] + 1
        else:
            game_counts[away] = 1

df = pd.DataFrame(game_counts.items(), columns=['Team', 'Nombre de matchs'])
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
