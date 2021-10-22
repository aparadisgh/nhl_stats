import requests
import json
import pandas as pd
import dash
from dash import dash_table
from dash import html
import dash_bootstrap_components as dbc
import datetime
import config

today = datetime.datetime.today()
wd = today.weekday()
print(wd)
days_to_monday = 7-wd

if wd == 0:
    startDate = today.strftime('%Y-%m-%d')
else:
    startDate = today + datetime.timedelta(days=days_to_monday)

endDate = startDate + datetime.timedelta(days=6)

startDate_str = startDate.strftime('%Y-%m-%d')
endDate_str = endDate.strftime('%Y-%m-%d')

r = requests.get(f'https://statsapi.web.nhl.com/api/v1/schedule?startDate={startDate_str}&endDate={endDate_str}')

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
                className="container",
                children=[
                    html.H1("SweetPicks.com"),
                    html.H6(f"Du {startDate_str} au {endDate_str}"),
                    dash_table.DataTable(
                        id='table',
                        columns=[{"name": i, "id": i} for i in df.columns],
                        data=sorted_df.to_dict('records'),
                        sort_action='native',
                        filter_action="native",
                        style_data_conditional=[
                            {
                                'if': {
                                    #'filter_query': '{Nombre de matchs} > 3',
                                    'filter_query': '{{Nombre de matchs}} = {}'.format(df['Nombre de matchs'].max()),
                                    'column_id': ['Team', 'Nombre de matchs']
                                },
                                'backgroundColor': 'rgb(102, 255, 102)',
                                'color': 'rgb(64, 64, 64)'
                            }]
                    )]
            )

if __name__ == '__main__':
    app.run_server(host=config.server["host"],port=config.server["port"],debug=config.server["debug"])