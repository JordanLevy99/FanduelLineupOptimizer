import pandas as pd
import os



def percent_top_performers(types):
    hist_dict = {}
    for type in types:
        for date in date_range:
            print(date)
            daily_names = pd.Series()
            try:
                top_20_names = pd.read_csv(os.path.join('Hist_Data', date, 'top_{}_performers.csv'.format(x)))['Name'].to_list()
            except FileNotFoundError:
                continue
            for i in range(1,11):
                lineup_names = pd.read_csv(os.path.join('Hist_Data',date,type,'lineup{}.csv'.format(i)))['Name']
                daily_names = daily_names.append(lineup_names).reset_index(drop=True)
            num_good = 0
            for name in daily_names.unique():
                if name in top_20_names:
                    num_good += 1
            percent_good = num_good / len(top_20_names)
            hist_dict[date] = percent_good
    print(hist_dict)
    return pd.Series(hist_dict, name='Pct_Good')

def avg_pts(types):
    hist_dict = {}
    for type in types:
        for date in date_range:
            print(date)
            daily_lineups = pd.Series()
            for i in range(1,11):
                try:
                    lineup = pd.read_csv(os.path.join('Hist_Data',date,type,'lineup{}.csv'.format(i)))['FD_PTS']
                except FileNotFoundError:
                    continue
                daily_lineups = daily_lineups.append(lineup).reset_index(drop=True)
            avg_pts = sum(daily_lineups) / 10
            hist_dict[date] = avg_pts
    return pd.Series(hist_dict, name='Avg Total FD Pts')


if __name__ == "__main__":
    x = 0.33
    start_date = '2018-10-16'
    end_date = '2019-04-10'
    types_of_lineups = ['Ceiling']
    date_range = pd.Series(pd.date_range(start_date, end_date)).astype(str).to_list()#.apply(lambda x: x.split('-')).to_list()  # Creates a list of datetime objects

    #good_performers = percent_top_performers(types_of_lineups)
    #good_performers.to_csv('top_{}_percentage.csv'.format(x), index=True, header=True)

    avg_fd_pts = avg_pts(types_of_lineups)
    avg_fd_pts.to_csv('avg_fd_fpts_18-19.csv', header=True)
