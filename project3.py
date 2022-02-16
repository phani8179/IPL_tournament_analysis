import pymongo
import datetime
import pprint
import operator
import pandas as pd
import seaborn
import matplotlib.pyplot as plt
from pymongo import MongoClient
client = MongoClient('localhost', 27017) #localhost database connection
db = client["test"]
collection=db["ipl_matches"]
def venues():
    venue_list=collection.distinct('venue')
    venue_data=[{venue_list[i]:{'bat_first':0,'field_first':0}} for i in range(len(venue_list))]
    for match in collection.find():
        for venue in range(len(venue_list)):
            if venue_list[venue]==match['venue']:
                if match['win_by_runs']!=0:
                    venue_data[venue][match['venue']]['bat_first']+=1
                if match['win_by_wickets']!=0:
                    venue_data[venue][match['venue']]['field_first']+=1
    for j in range(len(venue_list)):
        print(str(j) + ". " + venue_list[j])
    venue_option=int(input("select a venue\n"))
    print("matches won batting first: " + str(venue_data[venue_option][venue_list[venue_option]]['bat_first']))
    print("matches won batting second: " + str(venue_data[venue_option][venue_list[venue_option]]['field_first']))
    if venue_data[venue_option][venue_list[venue_option]]['bat_first']>venue_data[venue_option][venue_list[venue_option]]['field_first']:
        print("venue suitable to opt batting first\n")
    else:
        print("venue suitable to opt fielding first\n")
    return

def successful_team():
    season_list=collection.distinct('Season')
    season_data=[{season:{}} for season in season_list]
    for season in range(len(season_list)):
        team_list=collection.find({'Season':season_list[season]}).distinct('winner')
        for team in team_list:
            season_data[season][season_list[season]][team]=0
    for season in range(len(season_list)):
        for match in collection.find():
            if match['winner']:
                if match['Season']==season_list[season]:
                    season_data[season][season_list[season]][match['winner']]+=1
    for k in range(len(season_list)):
        print(str(k) + ". " + season_list[k])
    season_option=int(input("select a season\n"))
    season_val=season_list[season_option]
    season_data_df=pd.DataFrame(season_data[season_option][season_val].items(),columns=['team','count'])
    season_data_df=season_data_df.sort_values(by=['count'],ascending=False)
    titl='No. of wins of teams for the season ' + str(season_list[season_option])
    plt.title(titl)
    season_data_df.plot.bar(x='team',y='count')
    plt_file='successful_team_'+season_val
    plt.savefig(plt_file)
    team_keys=list(season_data[season_option][season_list[season_option]].keys())
    max_wins=season_data[season_option][season_list[season_option]][team_keys[0]]
    max_wins_team=team_keys[0]
    for m in list(season_data[season_option][season_list[season_option]].keys()):
        if season_data[season_option][season_list[season_option]][m]>max_wins:
            max_wins=season_data[season_option][season_list[season_option]][m]
            max_wins_team=m
    print("Most successful team of the season " + str(season_list[season_option]) + " is " + str(max_wins_team) + " with " + str(max_wins) + " wins.")
    return

def toss_impact():
    season_list=collection.distinct('Season')
    toss_data=[{season_list[i]:{'won_toss':0,'lost_toss':0}} for i in range(len(season_list))]
    for k in range(len(season_list)):
        print(str(k) + ". " + season_list[k])
    season_option=int(input("select a season\n"))
    won_toss=0
    lost_toss=0
    for match in collection.find():
        if match['Season']==season_list[season_option]:
            if match['winner'] and match['toss_winner']:
                if match['winner']==match['toss_winner']:
                    won_toss+=1
                else:
                    lost_toss+=1
    if won_toss<lost_toss:
        print("Teams that won the toss had won " + str(won_toss) + " matches that is less than " + str(lost_toss) + " matches won by teams that lost the toss.")
        print("There is no impact of toss in the season " + str(season_list[season_option]) + ".")
    if won_toss>lost_toss:
        if won_toss-lost_toss>=7:
            print("Teams that won the toss had won " + str(won_toss) + " matches which is comparatively more than " + str(lost_toss) + " matches won by teams that lost the toss.")
            print("There is a considerable impact of toss in the season " + str(season_list[season_option]) + ".")
        if won_toss-lost_toss<7:
            print("Teams that won the toss had won " + str(won_toss) + " matches which is not that more than " + str(lost_toss) + " matches won by teams that lost the toss.")
            print("There is no considerable impact of toss in the season " + str(season_list[season_option]) + ".")
        if won_toss-lost_toss>15:
            print("Teams that won the toss had won " + str(won_toss) + " matches which is highly more than " + str(lost_toss) + " matches won by teams that lost the toss.")
            print("There is a heavy impact of toss in the season " + str(season_list[season_option]) + ".")
    if won_toss==lost_toss:
        print("Teams that won the toss had won " + str(won_toss) + " matches which is equal to " + str(lost_toss) + " matches won by teams that lost the toss.")
        print("There is no impact of toss in the season " + str(season_list[season_option]) + ".")
    return

def valuable_player():
    player_list=collection.distinct('player_of_match')
    player_data={}
    winner_data={}
    for i in range(len(player_list)):
        player_data[player_list[i]]=0
    for a in range(len(player_list)):
        for match in collection.find():
            if match['player_of_match']:
                if match['player_of_match']==player_list[a]:
                    player_data[player_list[a]]+=1
    valuable_data=dict(sorted(player_data.items(), key=operator.itemgetter(1), reverse=True)[:20])
    for player in valuable_data.keys():
        print(str(player) + " : " + str(valuable_data[player]))
    mvp_data_df=pd.DataFrame(valuable_data.items(),columns=['player','count'])
    mvp_data_df=mvp_data_df.sort_values(by=['count'],ascending=False)
    plt.title('Most valuable players')
    mvp_data_df.plot.bar(x='player',y='count')
    #plt.bar(range(len(valuable_data)), list(valuable_data.values()), align='center')
    #plt.xticks(range(len(valuable_data)), list(valuable_data.keys()), align='center')
    plt.savefig('MVP.png')
    for player in valuable_data.keys():
        winner_data[player]=True
    winner_data['CH Gayle']=False
    winner_data['AB de Villiers']=False
    winner_data['AM Rahane']=False
    winner_data['V Kohli']=False
    winner_data[ 'A Mishra']=False
    winner_data['V Sehwag']=False
    winner_data['SE Marsh']=False
    win_percent=0
    for player in valuable_data.keys():
        if winner_data[player]==True:
            win_percent+=1
    win_percentage=(win_percent/20)*100
    if win_percentage>60:
        print(str(win_percentage) + " percent of top 20 most valuable players have won the IPL. So, having most valuable player in team can impact tournament win.")
    return

def popular_city():
    city_list=collection.distinct('city')
    city_data={}
    for city in city_list:
        if city:
            city_data[city]=0
    for match in collection.find():
        for city in city_list:
            if match['city']:
                if match['city']==city:
                    city_data[city]+=1
    city_data_df=pd.DataFrame(city_data.items(),columns=['city','count'])
    city_data_df=city_data_df.sort_values(by=['count'],ascending=False)
    print("The most popular city with maximum number of matches hosted is " + city_data_df.iloc[0]['city'] + " with " + str(city_data_df.iloc[0]['count']) + " matches.")
    plt.title('Most popular cities')
    city_data_df.plot.bar(x='city',y='count')
    plt.show()
    plt.savefig('city.png')
    return

def best_win_each_season():
    season_list=collection.distinct('Season')
    win_data={}
    matches=collection.find()
    for season in season_list:
        win_data[season]={'runs':{},'wickets':{}}
    for season in season_list:
        max_runs=0
        max_wickets=0
        runs_id=0
        wickets_id=0
        for match in collection.find():
            if match['Season']==season:
                if match['win_by_runs']>max_runs:
                    max_runs=match['win_by_runs']
                    runs_id=match['id']
                if match['win_by_wickets']>max_wickets:
                    max_wickets=match['win_by_wickets']
                    wickets_id=match['id']
        for match in collection.find():
            if match['winner']:
                if match['id'] == runs_id:
                    win_data[season]['runs']['win_by']=max_runs
                    win_data[season]['runs']['winner']=match['winner']
                    if match['team1']==match['winner']:
                        win_data[season]['runs']['opponent']=match['team2']
                    else:
                        win_data[season]['runs']['opponent']=match['team1']
                if match['id'] == wickets_id:
                    win_data[season]['wickets']['win_by']=max_wickets
                    win_data[season]['wickets']['winner']=match['winner']
                    if match['team1']==match['winner']:
                        win_data[season]['wickets']['opponent']=match['team2']
                    else:
                        win_data[season]['wickets']['opponent']=match['team1']
    for p in range(len(season_list)):
        print(str(p) + ". " + season_list[p])
    season_option=int(input("select a season\n"))
    season_value=season_list[season_option]
    print("The win with highest runs of the season " + str(season_value) + " is by " + str(win_data[season_value]['runs']['win_by']) + " runs by " + str(win_data[season_value]['runs']['winner']) + " against " + str(win_data[season_value]['runs']['opponent']) + ".")
    print("The win with highest wickets of the season " + str(season_value) + " is by " + str(win_data[season_value]['wickets']['win_by']) + " wickets by " + str(win_data[season_value]['wickets']['winner']) + " against " + str(win_data[season_value]['wickets']['opponent']) + ".")
    return   

def umpires():
    umpire_list1=collection.distinct('umpire1')
    umpire_list2=collection.distinct('umpire2')
    umpire_list=umpire_list1+umpire_list2
    umpire_list=list(set(umpire_list))
    umpire_data={}
    for umpire in umpire_list:
        umpire_data[umpire]=0
    for umpire in umpire_list:
        if umpire:
            for match in collection.find():
                if match['winner']:
                    if match['umpire1'] == umpire or match['umpire2'] == umpire:
                        umpire_data[umpire]+=1
    umpire_data_df=pd.DataFrame(umpire_data.items(),columns=['umpire','count'])
    umpire_data_df=umpire_data_df.sort_values(by=['count'],ascending=False)
    print(umpire_data_df)
    print("The most experienced umpire with maximum number of matches is " + umpire_data_df.iloc[0]['umpire'] + " with " + str(umpire_data_df.iloc[0]['count']) + " matches.")
    return

if __name__ == "__main__":
    while True:
        print("\tMENU\t")
        print("press 0 to exit")
        print("1. venue condition")
        print("2. Most successful team of season")
        print("3. Toss impact for a season")
        print("4. Most valuable player")
        print("5. Popular host city for a season")
        print("6. Best win of the season")
        print("7. Most experienced umpire")
        opt=int(input("select an option from above menu\n"))
        if opt==1:
            venues()
        elif opt==2:
            successful_team()
        elif opt==3:
            toss_impact()
        elif opt==4:
            valuable_player()
        elif opt==5:
            popular_city()
        elif opt==6:
            best_win_each_season()
        elif opt==7:
            umpires()
        elif opt==0:
            exit()
        else:
            print("Please enter a valid option to continue")
