# -*- coding: utf-8 -*-
"""Function libray to retreive important Fantasy Hockey dates

This module ...

To Do:
    - Look into using orjson instead of json
"""
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

    games_per_team = {}
    for date in r_dict['dates']:
        for game in date['games']:
            home = game['teams']['home']['team']['id']
            away = game['teams']['away']['team']['id']

            if home in games_per_team:
                games_per_team[home] = games_per_team[home]+[{
                    'date': date['date'],
                    'against': away,
                    'location': 'home'
                }]
            else:
                games_per_team[home] = [{
                    'date': date['date'],
                    'against': away,
                    'location': 'home'
                }]

            if away in games_per_team:
                games_per_team[away] = games_per_team[away]+[{
                    'date': date['date'],
                    'against': home,
                    'location': 'away'
                }]
            else:
                games_per_team[away] = [{
                    'date': date['date'],
                    'against': home,
                    'location': 'away'
                }]

    df_temp = pd.DataFrame(games_per_team.items(), columns=['ID', 'Upcoming Games'])

    df_temp = df_temp.set_index('ID')
    df_temp['Count'] = df_temp['Upcoming Games'].str.len()
    return df_temp
