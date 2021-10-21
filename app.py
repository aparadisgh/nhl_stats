import requests
import json
import pandas as pd
import dash
import dash_table
import dash_html_components as html
import dash_bootstrap_components as dbc

startDate = '2021-10-18'
endDate = '2021-10-25'

r = requests.get(f'https://statsapi.web.nhl.com/api/v1/schedule?startDate={startDate}&endDate={endDate}')

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
                    html.H1(f"Matchs du {startDate} au {endDate}"),
                    dash_table.DataTable(
                        id='table',
                        columns=[{"name": i, "id": i} for i in df.columns],
                        data=sorted_df.to_dict('records'),
                        sort_action='native',
                        filter_action="native",
                        style_data_conditional=[
                            {
                                'if': {
                                    'filter_query': '{Nombre de matchs} > 3',
                                    'column_id': ['Team', 'Nombre de matchs']
                                },
                                'backgroundColor': 'green',
                                'color': 'white'
                            }]
                    )]
            )

if __name__ == '__main__':
    app.run_server()