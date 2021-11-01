"""Team Ranking Page Layout

This module defines the pages content for the 'apps/teams' route.
"""

import datetime

from dash import dash_table
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from app import app

from utils import the_league
from utils import nhl_stats

layout = html.Div(
    id='app-container',
    className='my-4',
    children=[
        html.H5('Season Team Stats'),
        html.P('Select time span to update "Upcoming games"'),
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
        )
    ]
)

@app.callback(
    Output('date-picker-div', 'children'),
    Input('app-container','id')
)
def update_output_div(input_value): # pylint: disable=unused-argument
    """Update date picker on page load

    This callback sets the date picker for the following week (Monday to Sunday)
    It is meant to be executed on page load only.
    """
    start_date = the_league.get_next_monday()
    print(start_date)
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
                        'backgroundColor': 'rgb(204, 255, 204)',
                        'color': 'rgb(64, 64, 64)',
                    },
                    {
                        'if': {
                            'filter_query': 
                                f"{{Upcoming Games}} = {df['Upcoming Games'].min()}",
                        },
                        'backgroundColor': 'rgb(255, 204, 204)',
                        'color': 'rgb(64, 64, 64)',
                    },
                ]
            )
        ]
    else:
        children = []

    return children
