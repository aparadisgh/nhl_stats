import requests
import json
import pandas as pd

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

df = pd.DataFrame(game_counts.items(), columns=['Team', 'Number of Games'])
print(df.sort_values(by=['Number of Games'], ascending=False))
