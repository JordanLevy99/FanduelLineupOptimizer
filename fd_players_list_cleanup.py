import pandas as pd


players = pd.read_csv('FanDuel_NBA_2018-2019.csv')
print(players['Id'])

print(len(set(players['Id'].tolist())))
#print(len(players))
