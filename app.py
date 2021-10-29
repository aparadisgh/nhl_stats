# -*- coding: utf-8 -*-
"""SweetPicks WebApp

This module creates a simple web server using Dash to display relevent NHL stats.
The web app layout is define below.
"""

APP_VERSION = "v1.2.2"

import datetime

import dash
from dash import dash_table
from dash_table import FormatTemplate
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from utils import the_league
from utils import nhl_stats
import config

external_stylesheets = [dbc.themes.SPACELAB]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
                id='container',
                className='container-sm text-muted p-4',
                children=[
                    html.H3('The League | Advanced Analytics'),
                    html.Div(
                        children=[
                        dbc.Button(
                            "Team Stats", outline=False, 
                            color="light", className="me-1",
                        ),
                        dbc.Button(
                            "Player Stats", outline=False, 
                            color="light", className="me-1",
                             disabled=True
                        )]
                    ),
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
                                html.P(f'{APP_VERSION}')
                    ])
                ]
                
            )

@app.callback(
    Output('date-picker-div', 'children'),
    Input('container','id')
)
def update_output_div(input_value): # pylint: disable=unused-argument
    """Update date picker on page load

    This callback sets the date picker for the following week (Monday to Sunday)
    It is meant to be executed on page load only.
    """
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
    Input('my-date-picker-range','end_date'), # One can probably be a state to avoid triggering callback twice
)
def update_output_div(start_date, end_date):
    """Update data-table based on date pickers

    This callback function generates a datatable based on the selected dates
    Two HTTP requests are performed to fetch info from the NHL API.
    """

    if start_date and end_date:
        df1 = nhl_stats.get_records()
        df2 = nhl_stats.get_next_week(start_date, end_date)
        df = df1.merge(df2, left_index=True, right_index=True)
        df['GP'] = df['W'] + df['L'] + df['OTL']
        df['W (%)'] = df['W']/df['GP'] * 100
        df['W (%)'] = df['W (%)'].round(1)
        df = df[['Team', 'Upcoming Games','W (%)','GP','W','L','OTL']]
        sorted_df = df.sort_values(by=['Upcoming Games'], ascending=False)

        percentage = FormatTemplate.percentage(2)

        children = [
            dash_table.DataTable(
                id='table',
                columns=[{'name': i, 'id': i} for i in df.columns],
                data=sorted_df.to_dict('records'),
                sort_action='native',
                style_data_conditional=[
                    {
                        'if': {'column_id': 'Upcoming Games'},
                        'fontWeight': 'bold'
                    },
                    {
                        'if': {
                            'filter_query': 
                                f"{{Upcoming Games}} = {df['Upcoming Games'].max()}",
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
