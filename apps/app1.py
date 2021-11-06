"""Team Ranking Page Layout

This module defines the pages content for the 'apps/teams' route.

To Do:
    - When a team is selected of clicked on, display weelky matchup details
      (Cannot be a tooltip, see https://github.com/plotly/dash-table/issues/872)
    - Add a Winning Index for each team based on upcoming matchups
"""

import datetime

import pandas as pd
from dash import dash_table
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from pkg_resources import add_activation_listener

from app import app

from utils import league_param
from utils import nhl_api

layout = html.Div(
    id='app-container',
    className='my-4',
    children=[
        html.H5('Team Stats'),
        html.P('Select time span to update upcoming games count'),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Matchups")),
                dbc.ModalBody(
                    html.Div(
                        id='modal-content',
                        children=[]
                    )
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close", id="close", className="ms-auto", n_clicks=0
                    )
                ),
            ],
            id="modal",
            is_open=False,
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
    start_date = league_param.get_next_monday()
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
    [Output("modal", "is_open"),
    Output("modal-content", "children")],
    [Input("close", "n_clicks"),
    Input('table', 'active_cell')],
    [State("modal", "is_open"),
    State('my-date-picker-range','start_date'),
    State('my-date-picker-range','end_date'),
    State('table','data')],
    prevent_initial_call=True
)
def toggle_modal(n1, active_cell, is_open, start_date, end_date, tbl):
    """Display (pop-up) MatchUp Schedule

    """
    if not active_cell:
        raise PreventUpdate

    if start_date and end_date:
        teams = pd.DataFrame(tbl) #Replace with a constant TEAM_INDEX_DF

    selected_team = active_cell['row']
    content = [
        html.Div(
            children=[
                html.Span(game['date']),
                html.Span(' - '),
                html.Span(teams[teams['Index'] == game['against']]['Team']),
                html.Span(" - W(%): "),
                html.Span(teams[teams['Index'] == game['against']]['W (%)'])
            ]
        )
        for game in tbl[selected_team]['Upcoming Games']
    ]

    if (active_cell['column_id'] == 'Count'):
        return [not is_open, content] 
    return [is_open, content]

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
        df1 = nhl_api.get_records()
        df2 = nhl_api.get_next_week(start_date, end_date)
        df = df1.merge(df2, left_index=True, right_index=True)
        df['GP'] = df['W'] + df['L'] + df['OTL']
        df['W (%)'] = df['W']/df['GP'] * 100
        df['W (%)'] = df['W (%)'].round(1)
        df['Index'] = df.index
        df = df[['Index','Team', 'Count','W (%)','GP','W','L','OTL','Upcoming Games']]
        sorted_df = df.sort_values(by=['Count'], ascending=False)

        hidden_columns = ['Index','Upcoming Games']

        children = [
            dash_table.DataTable(
                id='table',
                columns=[{'name': i, 'id': i} for i in df.columns if i not in hidden_columns],
                data=sorted_df.to_dict('records'),
                sort_action='native',
                style_data_conditional=[
                    {
                        'if': {'column_id': 'Count'},
                        'fontWeight': 'bold'
                    },
                    {
                        'if': {
                            'filter_query': 
                                f"{{Count}} = {df['Count'].max()}",
                            'column_id': 'Count'
                        },
                        'backgroundColor': 'rgb(204, 255, 204)',
                        'color': 'rgb(64, 64, 64)',
                    },
                    {
                        'if': {
                            'filter_query': 
                                f"{{Count}} = {df['Count'].min()}",
                                'column_id': 'Count'
                        },
                        'backgroundColor': 'rgb(255, 229, 204)',
                        'color': 'rgb(64, 64, 64)',
                    },
                ]
            )
        ]

    else:
        children = []

    return children
