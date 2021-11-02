# -*- coding: utf-8 -*-
"""Function libray to retreive important Fantasy Hockey dates

This module ...
"""

#import datetime
import json

import requests
import pandas as pd

def get_records():
    r = requests.get("https://statsapi.web.nhl.com/api/v1/standings")
    r_dict = json.loads(r.text)

    df = pd.DataFrame(columns=['Team'])
    for record in r_dict["records"]:
        for team in record["teamRecords"]:
            df = df.append({
                'ID': team['team']['id'],
                'Team': team['team']['name'],
                'W': team['leagueRecord']['wins'],
                'L': team['leagueRecord']['losses'],
                'OTL': team['leagueRecord']['ot']},
                ignore_index=True)

    df = df.set_index('ID')
    return df

def get_next_week(startDate_str,endDate_str):
    r = requests.get(f'https://statsapi.web.nhl.com/api/v1/schedule?startDate={startDate_str}&endDate={endDate_str}') # pylint: disable=line-too-long

    r_dict = json.loads(r.text)

    game_counts = {}
    games_per_team = {}
    for date in r_dict['dates']:
        for game in date['games']:
            home = game['teams']['home']['team']['id']
            away = game['teams']['away']['team']['id']

            if home in games_per_team:
                #game_counts[home] = game_counts[home] + 1
                games_per_team[home] = games_per_team[home]+[{
                    'date': date['date'],
                    'against': away,
                    'location': 'home'
                }]
            else:
                #game_counts[home] = 1
                games_per_team[home] = [{
                    'date': date['date'],
                    'against': away,
                    'location': 'home'
                }]

            if away in games_per_team:
                #game_counts[away] = game_counts[away] + 1
                games_per_team[away] = games_per_team[away]+[{
                    'date': date['date'],
                    'against': home,
                    'location': 'away'
                }]
            else:
                #game_counts[away] = 1
                games_per_team[away] = [{
                    'date': date['date'],
                    'against': home,
                    'location': 'away'
                }]

    #df = pd.DataFrame(game_counts.items(), columns=['ID', 'Upcoming Games'])
    df_temp = pd.DataFrame(games_per_team.items(), columns=['ID', 'Upcoming Games'])
    #df = df.set_index('ID')

    df_temp = df_temp.set_index('ID')
    df_temp['Count'] = df_temp['Upcoming Games'].str.len()
    #print(df_temp)
    return df_temp
