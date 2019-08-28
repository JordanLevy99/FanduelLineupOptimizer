import pandas as pd
from selenium import webdriver
import json
import os.path
import time
from bs4 import BeautifulSoup

pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 500)
# pd.set_option('display.width', 1000)


driver = webdriver.Chrome('/Users/jordanlevy/Downloads/chromedriver')


def name_fixer(players_series):
    ### TODO UPDATE THIS WHEN THERE IS AN ERROR
    fix_these_names = {"T.J. Warren": "TJ Warren", "CJ McCollum": "C.J. McCollum", "Otto Porter Jr.": "Otto Porter",
                       "DeAndre' Bembry": "DeAndre Bembry",
                       "J.J. Redick": "JJ Redick", "Kelly Oubre Jr.": "Kelly Oubre", "Larry Nance Jr.": "Larry Nance",
                       "Juancho Hernangomez": "Juan Hernangomez",
                       "PJ Tucker": "P.J. Tucker", }  # "Walter Lemon":"Walter Lemon Jr."}   # name.strip "." and strip "Jr" unless its tim hardaway

    fix_names = players_series.isin(fix_these_names.keys())
    # print("These names need to be fixed: ")
    print(fix_names)
    if len(fix_names) > 0:

        for name in fix_names.index:
            # print("Updated Name: ",fix_these_names[fix_names.loc[i, 'Nickname']])
            players_series[name] = fix_these_names[players_series[name]]
    return players_series


def scrape_data(html, filename):
    ### TODO Potentially fix dtypes of player_df

    players_df = pd.DataFrame()

    if html is not None:
        player_stats = html.findAll(attrs={'class': "rgt-col"})  # .findAll(attrs={'class':'player-popup'})
        # print("Number of columns: ", len(player_stats))
        # players_df['Salaries'] =
        columns = ['Name', 'Salaries', 'Team', 'Position', 'Opponent', 'Projected Minutes', '', '', '', '', '', 'DvP',
                   'DvPRank', 'O/U', 'Line', 'Total', 'Movement', '', '', '', '', 'Ceiling', 'Floor', 'Projection',
                   'Pts/$/K']
        # dtypes = ['', 'int', 'object', 'object', 'object', 'object', 'object', 'object', 'object', 'object', 'object', 'object', 'int', 'float', 'float', 'float', 'float','object','object','object','object','float','float','float','float']
        for i in range(len(player_stats)):

            stat = pd.Series(player_stats[i].findAll('div')[1:])
            if i == 0:
                stat = pd.Series(player_stats[i].findAll(attrs={'class': 'player-popup'})).apply(lambda x: x.text)
            elif i == 1:
                stat = stat.apply(lambda x: int(float(x.text.strip('K').strip('$')) * 1000))
            else:
                stat = stat.apply(lambda x: x.text)

            players_df[columns[i]] = stat

        # for salary in salaries:
        #    salaries.append(salaries.text)

        # print(players_df)
        # print(players_df.dtypes)

        players_df.to_csv(os.path.join('Roto_Data', filename), index=False)
    ### TODO IMPLEMENT NAME_FIXER

    return players_df


def download_page(driver, url, filename):
    driver.get(url)
    # print('Got url')
    soup = BeautifulSoup(driver.page_source, 'html5lib')

    html = soup.find(attrs={'class': 'rgtable'})
    # print(html)

    scrape_data(html, filename)
    time.sleep(1)


def download_projections():
    # Start of season was 10-17-2018 and end of regular season was 4-12-2019
    start_date = '10-16-2018'  # Start date of the 2018-19 NBA Season
    end_date = '10-17-2018'  # End date of the 2018-19 NBA Regular Season

    daterange = pd.Series(pd.date_range(start_date, end_date)).astype(str).apply(
        lambda x: x.split('-')).to_list()  # Creates a list of datetime objects

    for date in daterange:
        year = date[0]
        month = date[1]
        day = date[2]
        url = "https://rotogrinders.com/projected-stats/nba-player?site=fanduel&date={}-{}-{}".format(str(year),
                                                                                                      str(month).zfill(
                                                                                                          2),
                                                                                                      str(day).zfill(2))
        print(url)
        download_page(driver, url, '{}-{}-{}.csv'.format(month, day, year))


if __name__ == "__main__":
    download_projections()
