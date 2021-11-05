# -*- coding: utf-8 -*-
"""Function libray to retreive important Fantasy Hockey dates

This module ...

To Do:
    - ...
"""

import requests
import bs4 
import html_to_json

def get_expected_goalies():
    URL = "https://www.rotowire.com/hockey/starting-goalies.php?view=teams"
    page = requests.get(URL)

    soup = bs4.BeautifulSoup(page.content, "html.parser")
    results = soup.find_all("div", {"class": "flex-row myleagues__proteam"})
    r = html_to_json.convert(str(results))

    teams = r['div']
    expected_goalies = {}
    for team in teams:
        team_name = team['div'][0]['_value']
        team_week = team['div'][1]['div'][0]['div']
        expected_goalies[team_name] = []

        day_offset = 0
        for day in team_week:
            if 'div' in day:

                starting_goalie = day['div'][0]['div'][0]['a'][0]['_value']
                team_against = day['div'][0]['div'][1]['_value']
                if 'b' in day['div'][0]['div'][2]:
                    status = 'Confirmed'
                else:
                    status = 'Expected'

                expected_goalies[team_name].append(
                    {
                        'goalie': starting_goalie,
                        'against': team_against,
                        'status': status,
                        'day':day_offset
                    }
                )
            
            day_offset = day_offset + 1
    return expected_goalies

"""
selected_team = 'STL'
selected_goalie = 'Jordan Binnington'

start_count = 0
confirmed_count = 0
for game in expected_goalies[selected_team]:
    if game['goalie'] == selected_goalie:
        start_count = start_count + 1
    if game['status'] =='Confirmed':
        confirmed_count = confirmed_count + 1
confirmed = confirmed_count / len(expected_goalies[selected_team]) * 100
number_of_games = len(expected_goalies[selected_team])
print(f'Upcoming week: {selected_goalie} starts {start_count} out of {number_of_games} games ({confirmed}% confirmed)')
"""