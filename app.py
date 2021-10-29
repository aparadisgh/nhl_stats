# -*- coding: utf-8 -*-
"""SweetPicks WebApp

This module creates a simple web server using Dash to display relevent NHL stats.
The web app layout is define below.
"""

APP_VERSION = "v1.2.0 (Beta)"

import datetime

import dash
from dash import dash_table
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from utils import the_league
from utils import nhl_stats
import config

external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
                id='container',
                className='container-sm text-muted p-4',
                children=[
                    html.H3('The League | Advanced Analytics'),
                    html.Div(
                        id='date-picker-div',
                        className='p-0 my-4',
                        children=[
                            dcc.DatePickerRange(
                                id='my-date-picker-range'
                            )]
                    ),
                    html.Div(
                        id='data-div',
                        children=[]
                    ),
                    html.Div(
                        className='text-center text-muted p-4',
                        children=[
                                html.P(f'Application - {APP_VERSION}')
                    ])
                ]
                
            )

@app.callback(
    Output('date-picker-div', 'children'),
    Input('container','id')
)
def update_output_div(input_value): # pylint: disable=unused-argument
    start_date = the_league.get_next_monday()
    end_date = start_date + datetime.timedelta(days=6)
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    children = [
        dcc.DatePickerRange(
            id='my-date-picker-range',
            min_date_allowed=datetime.date(2021, 10, 12),
            max_date_allowed=datetime.date(2022, 6, 1),
            initial_visible_month=start_date,
            start_date=start_date_str,
            end_date=end_date_str
        )
    ]
    return children

@app.callback(
    Output('data-div', 'children'),
    Input('my-date-picker-range','start_date'),
    Input('my-date-picker-range','end_date'),
)
def update_output_div(start_date, end_date): # pylint: disable=unused-argument
    """Update data-table on page load

    This callback function generates a datatable for next week.
    It is meant to be executed on page load only.
    """

    if start_date and end_date:
        df1 = nhl_stats.get_records()
        df2 = nhl_stats.get_next_week(start_date, end_date)
        df = df1.merge(df2, left_index=True, right_index=True)
        df['GP'] = df['W'] + df['L'] + df['OTL']
        df = df[['Team', 'Nombre de matchs','GP','W','L','OTL']]
        sorted_df = df.sort_values(by=['Nombre de matchs'], ascending=False)

        children = [
            #html.P(f'Du {start_date_str} au {end_date_str}'),
            dash_table.DataTable(
                id='table',
                columns=[{'name': i, 'id': i} for i in df.columns],
                data=sorted_df.to_dict('records'),
                sort_action='native',
                style_data_conditional=[
                    {
                        'if': {'column_id': 'Nombre de matchs'},
                        'fontWeight': 'bold'
                    },
                    {
                        'if': {
                            'filter_query': 
                                f"{{Nombre de matchs}} = {df['Nombre de matchs'].max()}",
                        },
                        'backgroundColor': 'rgb(119, 255, 125)',
                        'color': 'rgb(64, 64, 64)',
                }]
            )
        ]
    else:
        children = []

    return children

if __name__ == '__main__':
    app.run_server(host=config.HOST,port=config.PORT,debug=config.DEBUG)
