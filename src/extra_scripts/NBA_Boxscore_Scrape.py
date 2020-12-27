from selenium import webdriver
import json
import os.path
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

year1 = 18
year2 = 19

pd.set_option('display.max_columns', 500)

base_url = ('http://stats.nba.com/stats/leaguegamelog?Counter=1000&DateFrom=&'
        'DateTo=&Direction=DESC&LeagueID=00&PlayerOrTeam={}&Season=20{}-{}'
        '&SeasonType=Regular+Season&Sorter=DATE')

driver = webdriver.Chrome('/Users/jordanlevy/Downloads/chromedriver')
script_dir = os.path.dirname(__file__)


def boxscore_scrape():
    p = open('playerBoxscores{}{}.json'.format(year1, year2))
    player_data = json.loads(p.read())
    player_boxscores = np.array(player_data['resultSets'][0]['rowSet'])
    return player_boxscores




def download_file(driver, url, local_filename):
    driver.get(url)
    print('Got url')
    soup = BeautifulSoup(driver.page_source, 'html5lib')

    json_str = soup.find('body').string
    sub = json_str.find('</plaintext></div></body></html>')

    if (sub > 0):
        json_str = json_str[:sub]
    with open(local_filename, 'w') as f:
        f.write(json_str)
    driver.close()



def download_setup():
    for key in modifiers:
        url = base_url.format(key, year1, year2)
        local_filename = os.path.join(script_dir,
            '{}Boxscores{}{}.json'.format(modifiers[key], year1, year2))
        download_file(driver, url, local_filename)

modifiers = {'P': 'player', 'T': 'team'}
if __name__ == "__main__":

    download_setup()



    player_headers = ['SEASON_ID', 'PLAYER_ID', 'PLAYER_NAME', 'TEAM_ID', 'TEAM_ABBREVIATION', 'TEAM_NAME', 'GAME_ID', 'GAME_DATE', 'MATCHUP', 'WL', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'PLUS_MINUS', 'VIDEO_AVAILABLE']

    player_data = pd.DataFrame(boxscore_scrape(), columns=player_headers).drop(['SEASON_ID', 'PLAYER_ID', 'TEAM_ID', 'GAME_ID', 'VIDEO_AVAILABLE'], axis=1).set_index(['GAME_DATE','PLAYER_NAME'])
    player_data.to_csv('NBA_data_{}-{}.csv'.format(year1,year2))
    try:
        driver.quit()
    except:
        pass
