import math
import json
import datetime

import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from app import app

from utils import rotowire
from utils import nhl_api
from utils.team_abr import ABBREVIATIONS
from utils import league_param

BAD_PLAYER = 3 # threshold for bad average fan pointts

TIME_OPTIONS = {
    'currentSeason': 'Season',
    'last14days': 'Last 14 days',
    'thisWeek': 'This Week'
}

with open('data/player_names.json', 'r') as fp:
    player_names = json.load(fp)

with open('data/player_team.json', 'r') as fp:
    PLAYER_TEAM = json.load(fp)	

player_dd_options = [
    {'label': value, 'value': key}
    for key, value in player_names.items()
]

layout = html.Div(
    id='app-container',
    className='my-0',
    children=[
        html.Div(
            className='row',
            children=[
                html.Div(
                    className='col-xl-2 p-2',
                    children=[
                        html.Div(
                            className='p-3 bg-white borders border-secondary rounded shadow',
                            children=[
                                html.H3('Settings'),
                                html.Div(
                                    className='row',
                                    children=[
                                        html.Div(
                                            className='col',
                                            children=[
                                                html.Hr(),
                                                html.H6('Time'),
                                                html.Div(
                                                    className='mb-3',
                                                    children=[
                                                        
                                                        dcc.Dropdown(
                                                            id='timespan-dd',
                                                            clearable=False,
                                                            options=[
                                                                {'label': 'Season', 'value': 'currentSeason'},
                                                                {'label': 'Last 14 days', 'value': 'last14days'},
                                                                {'label': 'This Week', 'value': 'thisWeek'}
                                                            ],
                                                        )
                                                    ]
                                                ),
                                                html.H6('Players'),
                                                html.Div(
                                                    className='mb-3',
                                                    children=[
                                                        dcc.Dropdown(
                                                            id='player-dd',
                                                            options= player_dd_options,
                                                            multi=True,
                                                            persistence=True,
                                                        ),
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                ),
                html.Div(
                    className='col-xl-7 p-2',
                    children=[
                        html.Div(
                            className='p-3 bg-white borders border-secondary rounded shadow',
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
                        )
                    ]
                ),
                html.Div(
                    className='col-xl-3 p-2',
                    children=[
                        html.Div(
                            className='p-3 bg-white borders border-secondary rounded shadow mb-3 max-vh-50 overflow-auto',
                            children=[
                                html.H3('Predictions'),
                                html.Div(
                                    className='row',
                                    children=[
                                        html.Div(
                                            className='col',
                                            children=[
                                                #html.Hr(),
                                                dcc.Graph(
                                                    id='projection-chart',
                                                    figure={
                                                        'data': [],
                                                        'layout': {
                                                            'title': "Next Week's Predictions",
                                                            'showlegend': False,
                                                            'xaxis': {'fixedrange': True},
                                                            'yaxis': {'fixedrange': True},
                                                            'height': 250,
                                                            'margin': {
                                                                'l': 30,
                                                                'r': 30,
                                                                'b': 60,
                                                                't': 30,
                                                                'pad': 4
                                                            },
                                                            'bargap' : 0.01
                                                        }
                                                        
                                                    },
                                                    config= {'displayModeBar': False}
                                                )
                                            ]                               
                                        )
                                    ]
                                )
                            ]
                        ),
                        html.Div(
                            className='p-3 bg-white borders border-secondary rounded shadow',
                            children=[
                                html.H3('Notifications'),
                                #html.Div(
                                    #className='row',
                                    #children=[
                                        #html.Div(
                                            #className='col',
                                            #children=[
                                                #html.Hr,
                                                html.P(
                                                    id='expected-games',
                                                    children=[]
                                                )
                                            #]
                                        #)
                                    #]
                                #)
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

@app.callback(
    Output('url', 'hash'),
    Input('timespan-dd', 'value')
)
def update_hash(val):  # pylint: disable=unused-argumen

    url_part = ""
    if val:
        url_part = '#' + val

    return url_part

@app.callback(
    Output('url', 'search'),
    Input('player-dd', 'value')
)
def update_search(val):  # pylint: disable=unused-argumen

    url_part = ""
    if val:
        url_part = '?players=' + '&'.join(val)

    return url_part

@app.callback(
    Output('player-cards', 'children'),
    Output('timespan-dd', 'value'),
    Output('player-dd', 'value'),
    Output('projection-chart','figure'),
    Input('timespan-dd', 'value'),
    Input('player-dd', 'value'),
    State('url', 'search'),
    State('url', 'hash'),
    State('projection-chart','figure')
)
def on_app_load(timespan, players, url_search, url_hash,fig):  # pylint: disable=unused-argument
    
    #Prevent Update if no query is made
    if not url_search and not players:
        raise PreventUpdate

    if not url_hash and not timespan:
        raise PreventUpdate

    ctx = dash.callback_context

    # timespan sync (dropdown vs URL)
    hash = url_hash.replace('#','')
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    timespan_return_value = timespan if trigger_id == "timespan-dd" or not hash else hash

    # player query sync (dropdown vs URL)
    player_query = url_search.replace('?players=','').split("&")
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    player_query = players if trigger_id == "player-dd" else player_query

 # read stats from data cache
    with open('data/player_stats.json', 'r') as fp:
        data_dict = json.load(fp)

    # convert stats dictionaries into dataframes
    player_stats = {
        key: pd.DataFrame(data_dict[key]) 
        for key in data_dict
    }

    with open('data/player_names.json', 'r') as fp:
        player_names = json.load(fp)

    with open('data/player_pos.json', 'r') as fp:
        player_pos = json.load(fp)

    next_monday = league_param.get_next_monday()
    last_monday = next_monday + datetime.timedelta(days=-7)
    last_monday_str = last_monday.strftime('%Y-%m-%d')
    today = datetime.date.today()
    today_str = today.strftime('%Y-%m-%d')
    two_weeks_ago = today + datetime.timedelta(days=-14)
    two_weeks_ago_str = two_weeks_ago.strftime('%Y-%m-%d')

    players = [
        {
        'name': player_names[player_id],
        'id': player_id,
        'stats': {
            'df': player_stats[player_id],
            'fan_points':{
                'currentSeason': player_stats[player_id]['Fantasy Points'].mean(),
                'last14days': player_stats[player_id]
                [
                    (player_stats[player_id]['Date'] >= two_weeks_ago_str) 
                    & (player_stats[player_id]['Date'] <= today_str)
                ]['Fantasy Points'].mean(),
                'thisWeek': player_stats[player_id]
                [
                    (player_stats[player_id]['Date'] >= last_monday_str)
                    & (player_stats[player_id]['Date'] <= today_str)
                ]['Fantasy Points'].mean(),
            }
        },
        'position': player_pos[player_id]
        }
        for player_id in player_query
    ]

    players = sorted(players, key=lambda d: d['stats']['fan_points'][timespan_return_value] if not math.isnan(d['stats']['fan_points'][timespan_return_value]) else 0, reverse=True) 

    children = [
        html.Div(
            className='col-md-4',
            children=[
                html.Hr(),
                html.H5('Forwards'),
                html.Div(
                    children=[
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5(player['name']),
                                    html.Span(
                                        style={
                                            'font-size': '200%'},
                                        className= "text-danger" if player['stats']['fan_points'][timespan_return_value] < BAD_PLAYER else '',
                                        children=[
                                            f"{player['stats']['fan_points'][timespan_return_value]:.1f}" if not math.isnan(player['stats']['fan_points'][timespan_return_value]) else "-,-"
                                        ]
                                    ),
                                    html.Span(' PPG')
                                ]
                            ),
                            className='mb-3' 
                        )
                        for player in players if player["position"] != 'G' and player["position"] != 'D'
                    ]
                )
            ]
        ),
        html.Div(
            className='col-md-4',
            children=[
                html.Hr(),
                html.H5('Defensemans'),
                html.Div(
                    children=[
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5(player['name']),
                                    html.Span(
                                        style={
                                            'font-size': '200%'},
                                        className= "text-danger" if player['stats']['fan_points'][timespan_return_value] < BAD_PLAYER else '',
                                        children=[
                                            f"{player['stats']['fan_points'][timespan_return_value]:.1f}" if not math.isnan(player['stats']['fan_points'][timespan_return_value]) else "-,-"
                                        ]
                                    ),
                                    html.Span(' PPG')
                                ]
                            ),
                            className='mb-3' 
                        )
                        for player in players if player["position"] == 'D'
                    ]
                )
            ]
        ),
        html.Div(
            className='col-md-4',
            children=[
                html.Hr(),
                html.H5('Goalies'),
                html.Div(
                    children=[
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5(player['name']),
                                    html.Span(
                                        style={
                                            'font-size': '200%'},
                                        className= "text-danger" if player['stats']['fan_points'][timespan_return_value] < BAD_PLAYER else '',
                                        children=[
                                            f"{player['stats']['fan_points'][timespan_return_value]:.1f}" if not math.isnan(player['stats']['fan_points'][timespan_return_value]) else "-,-"
                                        ]
                                    ),
                                    html.Span(' PPG')
                                ]
                            ),
                            className='mb-3' 
                        )
                        for player in players if player["position"] == 'G'
                    ]
                )
            ]

        )
    ]

    start_date = league_param.get_next_monday()
    end_date = start_date + datetime.timedelta(days=6)
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    df = nhl_api.get_next_week(start_date_str, end_date_str)

    number_of_games = df['Count'].to_dict()

    players = [
        {
            'prediction': player['stats']['fan_points'][timespan_return_value],
            'id': player['id'],
            'position': player['position'],
            'lastName': player['name'].split()[-1],
            'gameCount': number_of_games[PLAYER_TEAM[player['id']]]
        }
        for player in players
    ]

    players = sorted(players, key=lambda d: d['prediction'] * d['gameCount'] if not math.isnan(d['prediction']) else 0, reverse=True) 

    fig['data'] = [
        {
            'name': 'Predictions',
            'x':[
                player['lastName']
                for player in players
            ],
            'y':[
                player['prediction'] * player['gameCount']
                for player in players
            ],
            'text':[
                player['gameCount']
                for player in players
            ],
            'textposition': 'none',
            'hovertemplate':'%{y:.2f} Fantasy Points' +
                            '<br>In %{text} games' +
                            '<br>%{x}',
            'type': 'bar',
            'opacity': 0.8,
            'marker': {
                'color': '#242475'
            }
        }
    ]

    fig['layout']['title'] = {
        'text':'Based off ' + TIME_OPTIONS[timespan_return_value],
        'font': {
            #'family': 'Courier New, monospace',
            #'size': 20
        },
        'xref': 'paper',
        'x': 0,
    }


    return children, timespan_return_value, player_query, fig


@app.callback(
    Output('expected-games', 'children'),
    Input('app-container', 'id'),
    Input('player-dd', 'value'),
    State('url', 'search'),
    State('timespan-dd', 'value'),
)
def update_goalie(unused, players, url_search, timespan):  # pylint: disable=unused-argument

    if not url_search and not players:
        raise PreventUpdate

    if not timespan:
        raise PreventUpdate

    #player_query = url_search.replace('?players=','').split("&")
    player_query = players

    expected_goalies = rotowire.get_expected_goalies()

    with open('data/player_pos.json', 'r') as fp:
        player_pos = json.load(fp)

    with open('data/player_names.json', 'r') as fp:
        player_names = json.load(fp)

    with open('data/player_team.json', 'r') as fp:
        player_teams = json.load(fp)

    children = []
    for player in player_query:
        if player_pos[player] == 'G':
            selected_team = ABBREVIATIONS['rotowire'][str(player_teams[player])]
            selected_goalie = player_names[player].split()[-1]

            start_count = 0
            confirmed_count = 0
            for game in expected_goalies[selected_team]:
                if selected_goalie in game['goalie']:
                    start_count = start_count + 1
                if game['status'] == 'Confirmed':
                    confirmed_count = confirmed_count + 1
            confirmed = confirmed_count / len(expected_goalies[selected_team]) * 100
            number_of_games = len(expected_goalies[selected_team])
            text = f'Starts {start_count} out of {number_of_games} upcoming games ({confirmed:.1f}% confirmed)'

            if number_of_games > 0:
                if (start_count/number_of_games)>0.5:
                    children.append(
                        html.Div(
                            className="alert alert-secondary border-0",
                            children=[
                                
                                html.H6(
                                    [
                                        html.I(
                                            className="bi bi-check-circle me-2",
                                            style={
                                                'color': 'green'
                                            }
                                        ), 
                                        selected_goalie
                                    ]
                                ),
                                html.Span(text),
                                html.Br(),
                                dcc.Link(
                                    "rotowire.com",
                                    className = "link-secondary fst-italic",
                                    href="https://www.rotowire.com/hockey/starting-goalies.php?view=teams",  
                                    target="_blank"
                                )
                            ]
                        )
                    )
                elif (start_count/number_of_games)>0:
                    children.append(
                        html.Div(
                            className="alert alert-warning border-0",
                            children=[
                                
                                html.H6([html.I(className="bi bi-exclamation-triangle me-2"), selected_goalie]),
                                html.Span(text),
                                html.Br(),
                                dcc.Link(
                                    "rotowire.com",
                                    className = "link-secondary fst-italic",
                                    href="https://www.rotowire.com/hockey/starting-goalies.php?view=teams",  
                                    target="_blank"
                                )
                            ]
                        )
                    )
                else:
                    children.append(
                        html.Div(
                            className="alert alert-danger border-0",
                            children=[
                                
                                html.H6([html.I(className="bi bi-exclamation-square me-2"), selected_goalie]),
                                html.Span(text),
                                html.Br(),
                                dcc.Link(
                                    "rotowire.com",
                                    className = "link-secondary fst-italic",
                                    href="https://www.rotowire.com/hockey/starting-goalies.php?view=teams",  
                                    target="_blank"
                                )
                            ]
                        )
                    )

    return children
