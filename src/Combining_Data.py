import os
import pandas as pd

pd.set_option('display.max_columns', 500)



def fix_nba_names(nba):
    fix_these_names = {"T.J. Warren":"TJ Warren", "CJ McCollum":"C.J. McCollum", "Otto Porter Jr.":"Otto Porter", "DeAndre' Bembry":"DeAndre Bembry",
                   "JJ Redick":"J.J. Redick", "Kelly Oubre Jr.":"Kelly Oubre", "Larry Nance Jr.":"Larry Nance", "Juancho Hernangomez": "Guillermo Hernangomez",
                    "PJ Tucker":"P.J. Tucker", "James Ennis III": "James Ennis"}
    names = nba[nba['PLAYER_NAME'].isin(fix_these_names.keys())]
    #print(len(f))
    #print(names)
    if len(names) > 0:

        for i in names.index:
            #print("Updated Name: ",fix_these_names[fix_names.loc[i, 'Nickname']])
            #print("BEFORE: ",nba.loc[i, 'PLAYER_NAME'])
            nba.loc[i, 'PLAYER_NAME'] = fix_these_names[names.loc[i, 'PLAYER_NAME']]
            #print("AFTER: ",nba.loc[i, 'PLAYER_NAME'])

    #print(roto)
    return nba



def combine_roto_data():
    directory = "Roto_Data/"

    year_df = pd.DataFrame()
    for filename in os.listdir(directory):

        df = pd.read_csv(os.path.join(directory, filename))
        df["Date"] = filename.strip(".csv")[-4:]+'-' + filename[:5]

        year_df = year_df.append(df)
        #print(year_df)
        print(filename)

    year_df = year_df.set_index(['Date','Name'])
    year_df.to_csv("2018-19_Roto_Data.csv", index=True)

def merge_roto_nba(roto, nba):

    roto_nba = pd.merge(roto, nba, how='inner', left_on=['Date','Name'], right_on=['GAME_DATE','PLAYER_NAME'])
    return roto_nba.drop(['GAME_DATE', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'TEAM_NAME', 'MATCHUP'], axis=1)#.reset_index()



if __name__ == "__main__":
    #combine_roto_data()
    comb_columns = ['Date', 'Name', 'Salaries', 'Team', 'Position', 'Opponent',
       '', 'Projected Minutes', 'DvP', 'DvPRank', 'O/U', 'Line',
       'Total', 'Movement', 'Ceiling', 'Floor', 'Projection', 'Pts/$/K', 'WL',
       'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA',
       'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF',
       'PTS', 'PLUS_MINUS']
    roto_data = pd.read_csv('2018-19_Roto_Data.csv')
    #print(roto_data)
    nba_data = pd.read_csv('NBA_data_18-19.csv')
    nba_data = fix_nba_names(nba_data)
    #d = fix_roto_names(roto_data)
    data = merge_roto_nba(roto_data, nba_data).sort_values('Date').reset_index(drop=True)
    data.columns = comb_columns
    '''broken_names = set(data[data['Date'].isnull()]['PLAYER_NAME'].values)
    #print(data[data['Date'].isnull()])
    print(broken_names)
    print("Number of misspelled names: ",len(broken_names))
    print(data.columns)'''
    data['FD_PTS'] = data['PTS'] + 1.2 * data['REB'] + 1.5 * data['AST'] + 3 * data['STL'] + 3 * data['BLK'] - data['TOV']
    data.to_csv('Combined_Roto_NBA_18-19.csv', index=False)
    print(data.columns)
