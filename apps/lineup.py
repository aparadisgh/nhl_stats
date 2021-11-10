import pandas as pd
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_daq as daq

from app import app

from utils import rotowire
from utils import nhl_api
from utils import rotowire
from utils import general

from apps.aparadis import ROSTERS

layout = html.Div(
    id='app-container',
    className='my-0',
    children=[
        html.Div(
            className='row',
            children=[
                html.Div(
                    className='col-9',
                    children=[
                        html.H3('Roster'),
                        html.Div(
                            className='row',
                            children=[
                                html.Div(
                                    id='player-cards',
                                    className='row',
                                    children=[]
                                )
                            ]
                        )
                    ]
                ),

                html.Div(
                    className='col-3',
                    children=[
                        html.H3('Options'),
                        daq.BooleanSwitch(
                            id='my-boolean-switch', 
                            on=False,
                        ),
                        html.H3('Alerts'),
                        html.P(
                            id='expected-games',
                            children=[]
                        )
                    ]
                )

            ]
        )
    ]
)


@app.callback(
    Output('player-cards', 'children'),
    Input('app-container', 'id')
)
def update_cards(input_value):  # pylint: disable=unused-argument

    players = [{
        'info': nhl_api.get_player_info(player['id']),
        'stats': nhl_api.get_player_stats(player['id'])
    }
        for player in ROSTERS['aparadis']['team']
    ]

    records = [
        general.convert_to_flat_dict(player, {})
        for player in players
    ]

    df = pd.DataFrame(records)
    df = df.set_index('info_id')

    df['PPG'] = (
        df['stats_goals'] * 3 +
        df['stats_assists'] * 2 +
        df['stats_plusMinus'] * 1 +
        df['stats_powerPlayPoints'] * 1 +
        df['stats_hits'] * 0.25 +
        df['stats_blocked'] * 0.5
    )/df['stats_games']

    df['Goalie_PPG'] = (
        df['stats_wins'] * 3 +
        df['stats_goalsAgainst'] * -1 +
        df['stats_saves'] * 0.2 +
        df['stats_shutouts']
    )/df['stats_games']

    df = df.sort_values(by=['PPG'], ascending=False)
    df = df.sort_values(by=['Goalie_PPG'], ascending=False)

    children = [
        html.Div(
            className='col-4',
            children=[
                html.H5('Forwards'),
                html.Div(
                    children=[
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5(row['info_fullName']),
                                    html.Span(
                                        style={
                                            'font-size': '200%'},
                                        className= "text-success fw-bold" if row['PPG'] > 5 else "text-danger" if row['PPG'] < 3 else '',
                                        children=[
                                            f"{round(row['PPG'], 1):.1f}"
                                        ]
                                    ) if row['info_rosterStatus'] == "Y" else
                                    html.Span(
                                        style={
                                            'font-size': '200%'},
                                        children=['-,-']
                                    ),
                                    html.Span(' PPG')
                                ]
                            ),
                            className='mb-3 shadow-sm' if row['info_rosterStatus'] == "Y" else 'mb-3 shadow-sm bg-light'
                        )
                        for index, row in df.iterrows() if row['info_primaryPosition_type'] == 'Forward'
                    ]
                )
            ]

        ),
        html.Div(
            className='col-4',
            children=[
                html.H5('Defensemans'),
                html.Div(
                    children=[
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5(row['info_fullName']),
                                    html.Span(
                                        style={
                                            'font-size': '200%'},
                                        className= "text-success fw-bold" if row['PPG'] > 5 else "text-danger" if row['PPG'] < 3 else '',
                                        children=[
                                            f"{round(row['PPG'], 1):.1f}"
                                        ]
                                    ) if row['info_rosterStatus'] == "Y" else
                                    html.Span(
                                        style={
                                            'font-size': '200%'},
                                        children=['-,-']
                                    ),
                                    html.Span(' PPG')
                                ]
                            ),
                            className='mb-3 shadow-sm' if row['info_rosterStatus'] == "Y" else 'mb-3 shadow-sm bg-light'
                        )
                        for index, row in df.iterrows() if row['info_primaryPosition_type'] == 'Defenseman'
                    ]
                )
            ]
        ),
        html.Div(
            className='col-4',
            children=[
                html.H5('Goalies'),
                html.Div(
                    children=[
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5(row['info_fullName']),
                                    html.Span(
                                        style={
                                            'font-size': '200%'},
                                        className= "text-success fw-bold" if row['Goalie_PPG'] > 5 else "text-danger" if row['Goalie_PPG'] < 3 else '',
                                        children=[
                                            f"{round(row['Goalie_PPG'], 1):.1f}"
                                        ]
                                    ) if row['info_rosterStatus'] == "Y" else
                                    html.Span(
                                        style={
                                            'font-size': '200%'},
                                        children=['-,-']
                                    ),
                                    html.Span(' PPG')
                                ]
                            ),
                            className='mb-3 shadow-sm' if row['info_rosterStatus'] == "Y" else 'mb-3 shadow-sm bg-light'
                        )
                        for index, row in df.iterrows() if row['info_primaryPosition_type'] == 'Goalie'
                    ]
                )
            ]
        )
    ]

    return children


@app.callback(
    Output('expected-games', 'children'),
    Input('app-container', 'id')
)
def update_goalie(input_value):  # pylint: disable=unused-argument
    expected_goalies = rotowire.get_expected_goalies()
    selected_team = 'STL'
    selected_goalie = 'Jordan Binnington'

    start_count = 0
    confirmed_count = 0
    for game in expected_goalies[selected_team]:
        if game['goalie'] == selected_goalie:
            start_count = start_count + 1
        if game['status'] == 'Confirmed':
            confirmed_count = confirmed_count + 1
    confirmed = confirmed_count / len(expected_goalies[selected_team]) * 100
    number_of_games = len(expected_goalies[selected_team])
    text = f'Upcoming week: {selected_goalie} starts {start_count} out of {number_of_games} games ({confirmed}% confirmed)'

    children = [
        html.H5(' '),
        html.Div(
            className="alert alert-success",
            children=text
        )
    ]

    return children
