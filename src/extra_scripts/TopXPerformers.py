import pandas as pd
import os
import warnings






def top_x_performers(x, total_data):
    for date in date_range:
        player_data = total_data[total_data['Date'] == date]
        if len(player_data) == 0:
            continue
        player_data = player_data.sort_values('FD_PTS', ascending=False).reset_index(drop=True)
        top_x = player_data.loc[:int(len(player_data)*x)]
        #print(top_x)
        print(date)
        top_x.to_csv(os.path.join('Hist_Data', date, 'top_{}_performers.csv'.format(x)), index=False)



if __name__ == "__main__":
    start_date = '2018-10-16'
    end_date = '2019-04-10'
    date_range = pd.Series(pd.date_range(start_date, end_date)).astype(str).to_list()#.apply(lambda x: x.split('-')).to_list()  # Creates a list of datetime objects
    total_data = pd.read_csv('Combined_Roto_NBA_18-19.csv')
    top_x_performers(.33, total_data)
