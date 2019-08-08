'''Instructions
Go to lineup you wish to enter and click on 'Download Players List'
Make One entry and download the CSV Edit template
'''

import time
start_time = time.time()
from pulp import *
import pandas as pd
import re
import warnings
import webbrowser
import shutil
import datetime
import os, errno
import csv

warnings.filterwarnings('ignore')

### TODO
# Generate top 10 lineups by adding a constraint that the maximum of the current lineup must be less than the previous lineup
# Read lineups before generating new ones, if the new would be the same as the old, continue.

def import_data():
    webbrowser.open("https://rotogrinders.com/projected-stats/nba-player.csv?site=fanduel")
    try:
        try:
            os.makedirs('Data/{}'.format(date_getter()))    #checks if directory already exists
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        shutil.move("/Users/jordanlevy/Downloads/nba-player.csv", "/Users/jordanlevy/Documents/GitHub/FanDuel-Optimizer/Data/{}/nba-player.csv".format(date_getter()))    # Change this to your own directory
        print("File Moved")
    except FileNotFoundError:
        print('File Not Found Error')
        return None


    player_data = pd.read_csv('Data/{}/nba-player.csv'.format(date_getter()))

    player_data.columns = list(range(len(player_data.columns)))
    player_data = player_data.drop([2,4], axis=1)
    player_data.columns = ['Player Name', 'Salary', 'Position', 'Ceiling', 'Floor', 'Projection']

    return player_data

#print(player_data)


def fanduel_maximizer(data, i):
    prob = pulp.LpProblem('FanduelSelections', LpMaximize)
    #print(data.loc[0,'Projection'])
    decision_variables = []
    total_projections = ''
    salary_variables = []
    pg_variables = []
    sg_variables = []
    sf_variables = []
    pf_variables = []
    c_variables = []

    for row in range(len(data)):
        variable = str('x' + str(row))
        variable = pulp.LpVariable(str(variable), lowBound=0, upBound=1, cat='Integer')
        decision_variables.append(variable)
        formula = round((data.loc[row, 'Ceiling'] + data.loc[row, 'Floor'] + data.loc[row, 'Projection']) / 3, 3) * variable  # calculates average of ceiling and floor projections
        total_projections += formula
        salary_variables.append(int(data.loc[row, 'Salary']) * variable)
        if data.loc[row, 'Position'] == 'PG':
            pg_variables.append(variable)
            data.loc[row, 'Position #'] = 1
        elif data.loc[row, 'Position'] == 'SG':
            sg_variables.append(variable)
            data.loc[row, 'Position #'] = 2
        elif data.loc[row, 'Position'] == 'SF':
            sf_variables.append(variable)
            data.loc[row, 'Position #'] = 3
        elif data.loc[row, 'Position'] == 'PF':
            pf_variables.append(variable)
            data.loc[row, 'Position #'] = 4
        elif data.loc[row, 'Position'] == 'C':
            c_variables.append(variable)
            data.loc[row, 'Position #'] = 5


    #print(pg_variables)

    prob += total_projections
    prob += lpSum(decision_variables) == 9
    prob += lpSum(pg_variables) == 2
    prob += lpSum(sg_variables) == 2
    prob += lpSum(sf_variables) == 2
    prob += lpSum(pf_variables) == 2
    prob += lpSum(c_variables) == 1

    prob += lpSum(salary_variables) <= 60000


    #prob += lpSum()
    #print(prob)
    prob.writeLP('FanduelSelections.lp')

    optimization_result = prob.solve()

    assert optimization_result == pulp.LpStatusOptimal

    #print('Status: ', LpStatus[prob.status])

    #print("Individual Decision variables: ")
    #for v in prob.variables():
    #    print(v.name, "=", v.varValue)

    #print('Total number of decision varia
    # bles ' + str(len(decision_variables)))
    #print('Array with Decision Variables: ' + str(decision_variables))
    #print("Optimization function: " + str(total_projections))
    variable_name = []
    variable_value = []
    for v in prob.variables():
        variable_name.append(v.name)
        variable_value.append(v.varValue)

    df = pd.DataFrame({'variable' : variable_name, 'value': variable_value})
    for rownum, row in df.iterrows():
        value = re.findall(r'(\d+)', row['variable'])   # this removes the x from the variable name e.g. x10 -> 10
        df.loc[rownum, 'variable'] = int(value[0])

    df = df.sort_values(by='variable')

    for rownum, row in data.iterrows():
        for results_rownum, results_row in df.iterrows():
            if rownum == results_row['variable']:
                data.loc[rownum, 'Play?'] = results_row['value']
    selected_players = data[data['Play?'] == 1].sort_values(by='Position #')
    selected_players = selected_players.loc[:, 'Player Name':'Projection']
    selected_players.to_csv('Data/{}/lineup-{}.csv'.format(date_getter(), i), index=False)   # writes output to csv as lineup # .csv
    print(selected_players)
    print('Total Salary: {}'.format(sum(selected_players['Salary'])))
    print('Total Projection {}'.format((sum(selected_players['Ceiling'])+sum(selected_players['Floor'])+sum(selected_players['Projection'])) / 3))
    end_time = time.time() - start_time
    print('Elapsed Time: {}'.format(round(end_time,3)) + ' seconds')

    return selected_players

def fd_players_list_mover(filename):
    files = []
    for file in os.listdir('/Users/jordanlevy/Downloads'):
        if filename in file:
            files.append(file)
            print(files)
            try:
                os.makedirs('Data/{}'.format(date_getter()))    #checks if directory already exists

            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
            shutil.move("/Users/jordanlevy/Downloads/{}".format(file), "/Users/jordanlevy/Documents/GitHub/FanDuel-Optimizer/Data/{}/{}".format(date_getter(), file))    # Change this to your own directory
            #return files

    for file in os.listdir('/Users/jordanlevy/Documents/GitHub/FanDuel-Optimizer/Data/{}'.format(date_getter())):
        if filename in file:
            files.append(file)
            print(files)
    return files
    #print('FanDuel File Not Found (ignore if already in directory)')

def fd_data_handler(lineup, filename):
    f = pd.read_csv("Data/{}/{}".format(date_getter(), filename))
    #f = f.drop(list(range(10)), axis=1)
    #print(f)
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
    #print(lineups)
    return players_id


def fd_csv_enter(players_id, filemode):

    '''f = pd.read_csv("Data/{}/{}".format(date_getter(), filename))
    #f = f.drop(list(range(10)), axis=1)
    #print(f)
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
    #print(lineups)'''

    with open('Data/{}/FD_lineups.csv'.format(date_getter()), mode=filemode) as FD_file:
        fd_writer = csv.writer(FD_file)
        if filemode == 'w':
            fd_writer.writerow(['PG','PG','SG','SG','SF','SF','PF','PF','C'])
        fd_writer.writerow(players_id)

def fd_csv_edit_reader(filename):
    with open('Data/{}/{}'.format(date_getter(), filename), mode='r') as fd_file:
        fd_reader = csv.reader(fd_file)
        entries = []
        for row in fd_reader:
            if row[0] == '':
                continue
            entries.append(row)
    return entries

def fd_csv_edit(entries, players_id, filemode, i):
    '''
    This currently only works for the first 10 lineups
    :param filename: The fanduel entries csv being passed into this function
    :param players_id: The list of player_ids that will be edited into the file
    :param filemode: Writes or appends to file
    :return:
    '''
    # Reads entries csv into list of entries
    #new_entries =
    '''for i in entries:
        try:
            int(i[0])   # Skips line if it doesn't start with an integer
        except ValueError:
            #print(i)
            del entries[i]
            continue
        #print(len(players_id))
        i[3:12] = players_id    # Sets lineup equal to updated and sorted player IDs
        #print(i)'''
    try:
        entries[i][3:12] = players_id
    except IndexError:
        return None
    with open('Data/{}/FD_csv_edit.csv'.format(date_getter()), mode=filemode) as fd_file:
        fd_writer = csv.writer(fd_file)

        if filemode == 'w':
            fd_writer.writerow(['entry_id', 'contest_id', 'contest_name', 'PG', 'PG', 'SG', 'SG', 'SF', 'SF', 'PF', 'PF', 'C', '', 'Instructions'])

        fd_writer.writerow(entries[i])

    return None



def date_getter():
    today = datetime.date.today()
    hour = datetime.datetime.now().hour
    if hour >= 20:  # time is past 8 pm, make the date tomorrow
        today = datetime.date.today() + datetime.timedelta(days=1)
    return today



def main():
    today = date_getter()

    player_data = import_data()
    #print(player_data)
    #if import_data() == None:
    #    return "oof"
    print('Lineup 1')
    first_lineup = fanduel_maximizer(player_data, 1)
    first_lineup_names = first_lineup['Player Name'].tolist()


    filename = 'FanDuel-NBA-{}'.format(today)
    #print(filename)
    fanduel_filenames = fd_players_list_mover(filename)
    #print('File Moved')
    print(fanduel_filenames)
    if len(fanduel_filenames) == 1:
        players_id = fd_data_handler(first_lineup_names, fanduel_filenames[0])   # handles the player list data, converts player name to player_id

        fd_csv_enter(players_id, 'w')
    elif len(fanduel_filenames) == 2:

        players_id = fd_data_handler(first_lineup_names, fanduel_filenames[0])   # handles the player list data, converts player name to player_id
        entries = fd_csv_edit_reader(fanduel_filenames[1])
        fd_csv_edit(entries, players_id, 'w', 1)  # goes to csv edit
        fd_csv_enter(players_id, 'w')
    else:
        print('Please Download Players List')
        raise FileNotFoundError
    print(first_lineup_names)


    for i in range(len(first_lineup_names)):
        print('Lineup {}'.format(i+2))
        updated_player_data = player_data[(player_data['Player Name'] != first_lineup_names[i])] #& (player_data['Player Name'] != 'Jimmy Butler')]
        updated_player_data.index = range(len(updated_player_data)) #updates the index values of dataframe
        #print(updated_player_data)
        players = fanduel_maximizer(updated_player_data, i+2)
        lineup = players['Player Name'].tolist()
        if len(fanduel_filenames) == 1:
            players_id = fd_data_handler(lineup, fanduel_filenames[0])   # handles the player list data, converts player name to player_id
            fd_csv_enter(players_id, 'a')
        else:
            players_id = fd_data_handler(lineup, fanduel_filenames[0])   # handles the player list data, converts player name to player_id
            fd_csv_edit(entries, players_id, 'a', i+2)  # goes to csv edit
            fd_csv_enter(players_id, 'a')
        #fd_csv_enter(lineup, fanduel_filenames[1], 'a')

main()
