'''Instructions
Go to lineup you wish to enter and click on 'Download Players List'
'''


#import webbrowser
import shutil
import datetime
import os
import errno
import csv
import pandas as pd
today = datetime.date.today()
hour = datetime.datetime.now().hour

if hour >= 19:
    today = datetime.date.today() + datetime.timedelta(days=1)
the_date = datetime.datetime.now().hour
#print(today)
fanduel = ''
filename = 'FanDuel-NBA-{}'.format(today)
def fd_players_list_mover(filename):
    for file in os.listdir('/Users/jordanlevy/Downloads'):

        if filename in file:
            fanduel_filename = file

            print(fanduel)
            try:
                os.makedirs('Data/{}'.format(today))    #checks if directory already exists

            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
            shutil.move("/Users/jordanlevy/Downloads/{}".format(file), "/Users/jordanlevy/Desktop/TheAlmightySpreadsheet/Data/{}/{}".format(today, file))    # Change this to your own directory
            break
    for file in os.listdir('/Users/jordanlevy/Desktop/TheAlmightySpreadsheet/Data/{}'.format(today)):
        if filename in file:
            fanduel_filename = file
            print(fanduel_filename)
            break

    print('FanDuel File Not Found (ignore if already in directory)')
    return fanduel_filename

def fd_csv_edit(lineup, filename):

    f = pd.read_csv("Data/{}/{}".format(today, fanduel))
    #f = f.drop(list(range(10)), axis=1)
    #print(f)
    lineups = []
    #lineup = ['Stephen Curry', 'George Hill', 'Gary Harris', 'Damion Lee', 'Paul George', 'Taurean Prince', 'Draymond Green', 'Paul Millsap', 'Miles Plumlee']
    position_id = {'PG':1, 'SG':2, 'SF':3, 'PF':4, 'C':5}
    players = f[f['Nickname'].isin(lineup)]
    players.index = range(len(players)) #updates the index values of dataframe
    #print(players)
    for i in range(len(players)):

        players.loc[i, 'Position'] = position_id[players.loc[i, 'Position']]
    players = players.sort_values(by='Position')
    #print(players)
    players_id = players['Id'].tolist()
    lineups.append(players_id)
    #print(lineups)

    with open('Data/{}/FD_lineups.csv'.format(today), mode='w') as FD_file:
        FD_writer = csv.writer(FD_file)
        for i in lineups:
            FD_writer.writerow(i)


#webbrowser.open("https://rotogrinders.com/projected-stats/nba-player.csv?site=fanduel")
'''try:
    shutil.move("/Users/jordanlevy/Downloads/nba-player.csv", "/Users/jordanlevy/TheAlmightySpreadsheet/Data/{}/nba-player.csv".format(today))    # Change this to your own directory
except FileNotFoundError:
    print('File Not Found')
    pass'''

#/Users/jordanlevy/Downloads/nba-player.csv
