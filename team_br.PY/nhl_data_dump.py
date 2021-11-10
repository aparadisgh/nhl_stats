from datetime import date
import pandas as pd
import requests
import json


#when launching app, load a list of all current active NHL players
dropdown_players=[] #list of dictionaries to be used by dropdown
teams_list=[1,2,3,4,5,6,7,8,9,10,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,28,29,30,52,53,54,55]#team IDs are hardcoded
players_dict={} #dictionary containing player full name at its playerID key
player_team={} #dictionary containing player ID and team ID for each player
stats={} #dictionary used to contain data frames, one for each player in the dropdown, containing his stats
player_pos={} #dictoinary containing position for each player selected in dropdown
team_abr={} #dictionary of all teams id -> abbreviation (ie 1 -> NJD)

stats_ranged={}

#player fantasy points
fp_goal=3
fp_assist=2
fp_pm=1
fp_PP=1
fp_hits=0.25
fp_block=0.5

#goalies fantasy points
fp_win=3
fp_goal_against=-1
fp_saves=0.2
fp_shutout=2

#for each team, gets the roster, then appends to get a list of each player in the NHL with their team - only players currently on roster appear (ie Crosby not there because injured)
for team_id in teams_list:
    request_url='https://statsapi.web.nhl.com/api/v1/teams/'+str(team_id)+'?expand=team.roster'
    r=requests.get(url=request_url)
    data=r.json()
    team_roster=data['teams'][0]['roster']['roster']

    #get team abbreaviation for display purposes
    team_abr[team_id]=data['teams'][0]['abbreviation']   

    #once roster for a team is loaded, get each player's name and ID and append them to their respective entry in the dropdown dictionary    
    for index in range(len(team_roster)):

        #creates a dictionary containing each player's ID and their team ID {'playerID', 'teamID'} for future reference
        player_team[team_roster[index]['person']['id']]=team_id
        player_pos[team_roster[index]['person']['id']]=team_roster[index]['position']['code'] #assigns position (G/D/L/C/R) to all players 

        dropdown_player={}
        fullName=team_roster[index]['person']['fullName']
        person_playerID=team_roster[index]['person']['id']
        dropdown_player['label']=fullName
        dropdown_player['value']=person_playerID
        dropdown_players.append(dropdown_player)
        #dropdown list of dictionaries {'Name', 'ID'} contains all players in the league after the last iteration of this loop

        players_dict[person_playerID]=fullName


#print('fetching players done')
#print(range(len(dropdown_players))) #prints number of players currently in rosters

#playerIDit is just to see the progress when loading stats, will go from 1 to # of players
#for each player, load all their games and for all their games load their stats
teams={}
for playerIDit in range(len(dropdown_players)):
    playerID=dropdown_players[playerIDit]['value']
    print('Progress: '+ str(playerIDit)+'/'+str(len(dropdown_players))+' | '+str(round((playerIDit/len(dropdown_players)*100),2))+'%')
    team_id=player_team[playerID]
    date_start= str(date(2021, 10, 13))
    date_end= str(date.today()) 
    url='https://statsapi.web.nhl.com/api/v1/schedule?teamId='+str(team_id)+'&startDate='+date_start+'&endDate='+date_end
    r=requests.get(url=url)
    data=r.json()
    teams[player_team[playerID]]=data['totalItems']

    game_dates={} #dictionary linking gameID with the date of the game
    player_games={}
    game_ids=[]
    homeaway=[]
    games=data['totalItems']


    for y in range(games):
        gamid=data['dates'][y]['games'][0]['gamePk'] #fetching game ID for each game for each player
        game_dates[gamid]=data['dates'][y]['date'] #using game ID to generate dictionary with corresponding date
        game_ids.append(gamid) #creating a list of all game IDs to fetch stats
        ha=data['dates'][y]['games'][0]['teams']['home']['team']['id']
        ha_st = 'home' if ha == team_id else 'away' #creating list of home/away status for each player to fetch stats properly
        homeaway.append(ha_st)


    player_games[playerID]=game_ids
    #player stats
    dates=[]
    goals=[]        
    assists=[]  
    plusMinus=[]  
    powerPlayGoals=[]  
    powerPlayAssists=[]  
    hits=[]  
    blocked=[]  

    #goalie stats
    wins=[]
    goals_against=[]
    saves=[]
    shutouts=[]

    for games in range(len(player_games[playerID])):

        game_id=player_games[playerID][games]
        url='https://statsapi.web.nhl.com/api/v1/game/'+str(game_id)+'/boxscore'
        r=requests.get(url=url)
        data=r.json()
        
        #for goalies sometimes they don't play, avoid fetching keys that don't exist when it's the case
        if player_pos[playerID] == 'G':

            stat_check=data['teams'][homeaway[games]]['players'].get('ID'+str(playerID))
            if stat_check == None:
                nogame=1

            else:
                stat_check2=data['teams'][homeaway[games]]['players']['ID'+str(playerID)]['stats'].get('goalieStats')
                if stat_check2 == None:
                    nogame=1

                else:
                    dates.append(game_dates[game_id])
                    wins.append(1) if data['teams'][homeaway[games]]['players']['ID'+str(playerID)]['stats']['goalieStats']['decision']=='W' else wins.append(0)
                    goal_against=data['teams'][homeaway[games]]['players']['ID'+str(playerID)]['stats']['goalieStats']['shots']-data['teams'][homeaway[games]]['players']['ID'+str(playerID)]['stats']['goalieStats']['saves']
                    goals_against.append(goal_against)
                    saves.append(data['teams'][homeaway[games]]['players']['ID'+str(playerID)]['stats']['goalieStats']['saves'])
                    save_pct=data['teams'][homeaway[games]]['players']['ID'+str(playerID)]['stats']['goalieStats']['savePercentage']
                    shutouts.append(1) if save_pct == 100.0 else shutouts.append(0)
                    # add both goalie and player stats in frame so plotting works with cross player/goalie, but populate with None (plot will show name but no values for goalie/player specific stuff)
                    goals.append(None)
                    assists.append(None)
                    plusMinus.append(None)
                    powerPlayGoals.append(None)
                    powerPlayAssists.append(None)
                    hits.append(None)
                    blocked.append(None)

                    tmp_stats=pd.DataFrame()
                    tmp_stats['Date'] = dates
#                    tmp_stats = tmp_stats.set_index('Date')
                    tmp_stats['Goals'] = goals
                    tmp_stats['Assists'] = assists
                    tmp_stats['+-'] = plusMinus
                    tmp_stats['PPG'] = powerPlayGoals
                    tmp_stats['PPA'] = powerPlayAssists
                    tmp_stats['Hits'] = hits
                    tmp_stats['Blocked'] = blocked
                    #goalie stuff filled in						
                    tmp_stats['Wins'] = wins
                    tmp_stats['Goals Against'] = goals_against
                    tmp_stats['Saves'] = saves        
                    tmp_stats['Shutouts'] = shutouts

                    stats[playerID]=tmp_stats


        else:
            stat_check=data['teams'][homeaway[games]]['players'].get('ID'+str(playerID))
            if stat_check == None:
                nogame=1

            else:
                stat_check2=data['teams'][homeaway[games]]['players']['ID'+str(playerID)]['stats'].get('skaterStats')
                if stat_check2 == None:
                    nogame=1

                else:
                    dates.append(game_dates[game_id])
                    goals.append(data['teams'][homeaway[games]]['players']['ID'+str(playerID)]['stats']['skaterStats']['goals'])
                    assists.append(data['teams'][homeaway[games]]['players']['ID'+str(playerID)]['stats']['skaterStats']['assists'])
                    plusMinus.append(data['teams'][homeaway[games]]['players']['ID'+str(playerID)]['stats']['skaterStats']['plusMinus'])
                    powerPlayGoals.append(data['teams'][homeaway[games]]['players']['ID'+str(playerID)]['stats']['skaterStats']['powerPlayGoals'])
                    powerPlayAssists.append(data['teams'][homeaway[games]]['players']['ID'+str(playerID)]['stats']['skaterStats']['powerPlayAssists'])
                    hits.append(data['teams'][homeaway[games]]['players']['ID'+str(playerID)]['stats']['skaterStats']['hits'])
                    blocked.append(data['teams'][homeaway[games]]['players']['ID'+str(playerID)]['stats']['skaterStats']['blocked'])
     
                    wins.append(None)
                    goals_against.append(None)
                    saves.append(None)
                    shutouts.append(None)
        
                    #generates stats in dataframe for each player before putting in dictionary   
                    tmp_stats=pd.DataFrame()
                    tmp_stats['Date'] = dates
#                    tmp_stats = tmp_stats.set_index('Date')
                    tmp_stats['Goals'] = goals
                    tmp_stats['Assists'] = assists
                    tmp_stats['+-'] = plusMinus
                    tmp_stats['PPG'] = powerPlayGoals
                    tmp_stats['PPA'] = powerPlayAssists
                    tmp_stats['Hits'] = hits
                    tmp_stats['Blocked'] = blocked
                    # add both goalie and player stats in frame so plotting works with cross player/goalie, but populate with None (plot will show name but no values for goalie/player specific stuff)
                    tmp_stats['Wins'] = wins
                    tmp_stats['Goals Against'] = goals_against
                    tmp_stats['Saves'] = saves        
                    tmp_stats['Shutouts'] = shutouts
        
                    stats[playerID]=tmp_stats #dictionary populated by each player's data frame of stats


       #compute cumulative stats and fantasy points (adds to player stats dataframe in dictionary)
        if playerID in stats:

            stats[playerID]['Goals Cumul'] = stats[playerID]['Goals'].cumsum()
            stats[playerID]['Assists Cumul'] = stats[playerID]['Assists'].cumsum()
            stats[playerID]['+- Cumul'] = stats[playerID]['+-'].cumsum()
            stats[playerID]['PPG Cumul'] = stats[playerID]['PPG'].cumsum()
            stats[playerID]['PPA Cumul'] = stats[playerID]['PPA'].cumsum()
            stats[playerID]['Hits Cumul'] = stats[playerID]['Hits'].cumsum()
            stats[playerID]['Blocked Cumul'] = stats[playerID]['Blocked'].cumsum()
            stats[playerID]['Wins Cumul'] = stats[playerID]['Wins'].cumsum()
            stats[playerID]['Goals Against Cumul'] = stats[playerID]['Goals Against'].cumsum()
            stats[playerID]['Saves Cumul'] = stats[playerID]['Saves'].cumsum()
            stats[playerID]['Shutouts Cumul'] = stats[playerID]['Shutouts'].cumsum()
            if player_pos[playerID] == 'G':
                stats[playerID]['Fantasy Points'] = stats[playerID]['Wins']*fp_win+stats[playerID]['Goals Against']*fp_goal_against+stats[playerID]['Saves']*fp_saves+stats[playerID]['Shutouts']*fp_shutout
            else:
                stats[playerID]['Fantasy Points'] = stats[playerID]['Goals']*fp_goal+stats[playerID]['Assists']*fp_assist+stats[playerID]['+-']*fp_pm+(stats[playerID]['PPG']+stats[playerID]['PPA'])*fp_PP+stats[playerID]['Hits']*fp_hits+stats[playerID]['Blocked']*fp_block
            stats[playerID]['Fantasy Points Cumul'] = stats[playerID]['Fantasy Points'].cumsum()

print('Fetching stats completed')

# convert dataframes into dictionaries
data_dict = {
    key: stats[key].to_dict(orient='records') 
    for key in stats.keys()
}

# write stats to disk (converts df to dict first)
with open('player_stats.json', 'w') as fp:
    json.dump(
        data_dict, 
        fp, 
        indent=4, 
#        sort_keys=True
    )

#write assorted dicts to disk
with open('player_names.json', 'w') as fp:
    json.dump(players_dict, fp)
with open('player_team.json', 'w') as fp:
    json.dump(player_team, fp)
with open('player_pos.json', 'w') as fp:
    json.dump(player_pos, fp)
with open('team_abr.json', 'w') as fp:
    json.dump(team_abr, fp)
	
print('Writing stats to disk completed')