from selenium import webdriver
import json
import os.path
import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import time
import shutil
import re
import sys
import os
import subprocess
import platform
from tqdm import tqdm
from datetime import datetime, timedelta
import sqlite3

from nba_api.stats.endpoints.commonallplayers import CommonAllPlayers
from nba_api.stats.endpoints.leaguegamelog import LeagueGameLog

def chrome_version():
    # Source: https://sqa.stackexchange.com/a/41390
    osname = platform.system()
    if osname == 'Darwin':
        installpath = "/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome"
    elif osname == 'Windows':
        installpath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
    elif osname == 'Linux':
        installpath = "/usr/bin/google-chrome"
    else:
        raise NotImplemented(f"Unknown OS '{osname}'")

    verstr = os.popen(f"{installpath} --version").read().strip('Google Chrome ').strip()
    return verstr


def dates_scraper(st_yr, end_yr, dr):
    total_dates = pd.Series(dtype='datetime64[ns]')
    for curr_yr in range(st_yr, end_yr):
        season_name = f'{curr_yr}-{str(curr_yr+1)[-2:]}'
        url = f'https://en.wikipedia.org/wiki/{season_name}_NBA_season'
        url_txt = requests.get(url).text
        soup= BeautifulSoup(url_txt, features="lxml") # check this features arg
        yr_finder = soup.find('table', class_='infobox').find_all('tr')[3].find('td').text
#         yr_finder = driver.find_element_by_xpath('/html/body/div[3]/div[3]/div[4]/div/table[1]/tbody/tr[4]/td')
        # reg_season = str(yr_finder).strip('<td>').strip('</td>').split('<br/>')[0]
        date_pat = '[A-z]{3,8} [\d]{2}, [\d]{4,}'
        range_reg_season = re.match(f'{date_pat} – {date_pat}',yr_finder).group(0).split(' – ')
        # range_reg_season = reg_season.split(' – ')
        # print(reg_season)
        start_date = range_reg_season[0]
        end_date = range_reg_season[1]
        # print(end_date)
        print(season_name, 'dates scraped')
        #print(reg_season)
        daterange = pd.Series(pd.date_range(start_date, end_date))
        total_dates = total_dates.append(daterange)
    if not os.path.isdir(dr): os.mkdir(dr)
    fname = dr+f'{st_yr}-{end_yr}_season_dates.csv'
    print(f'Saving dates at {fname}')
    total_dates.to_csv(fname, index=False, header=None)
    return total_dates.reset_index(drop=True)

def download_roto_file(date, driver):
    '''Downloads html file at the given url, which is rotoguru1.com with the corresponding month, day, and year
    from which to scrape data from. After writing all these webpages to a local html file, we will scrape the
    information needed and store it in a .csv file.  Takes about 21 minutes to scrape 3 seasons worth of data.'''

    date_str = str(date)[:10]
    # print('cwd', os.getcwd())
    local_fname = 'data/raw/Roto_Data/Roto_html/roto_data_{}.html'.format(date_str)
    local_dir = '/'.join(local_fname.split('/')[:-1])
    if os.path.isdir(local_dir) == False:
        os.mkdir(local_dir)
    if os.path.exists(local_fname):
        print(f'{local_fname} already exists')
        return

    url = 'http://rotoguru1.com/cgi-bin/hyday.pl?game=fd&mon={}&day={}&year={}'.format(date.month, date.day, date.year)

    driver.get(url)
    # print('Got url:',str(date)[:10])

    soup = BeautifulSoup(driver.page_source, 'html5lib')

    json = soup.findAll('table')
    data = json[9]

    # temp_dir = ''
    # for dir in local_dir.split()

    if os.path.exists(local_fname) != True: # if the specified file does not exist
        with open(local_fname, 'w') as f:

            for row in data:
                #print(row)

                f.write(str(row))


def get_update_dates(total_dates, c, table_name):
    db_dates = c.execute(f"SELECT DISTINCT Date from {table_name}").fetchall()
    db_dates = [pd.to_datetime(date[0]) for date in db_dates]
    # print(max(db_dates))
    print(len(db_dates), 'number of (unique) dates in the database')
    print(len(total_dates), 'number of (unique) dates we want in the database')
    print((len(total_dates) - len(db_dates)), 'number of (unique) dates to be added to the database\n')
    # print(type(total_dates[0]))
    # print(db_dates[0])
    new_dates = set(total_dates) - set(db_dates)  ### <-- TODO: figure out why length of new_dates is 669 and not 98...
    # print(max(new_dates))
    print(len(new_dates), 'number of (unique) dates we found via set difference')
    return new_dates


def combine_roto_data(roto_dir, total_dates, update, c=None, table_name=None):
    dir_dates = set()
    total_dates_set = set(total_dates)
    date_pat = '[\d]{4}-[\d]{2}-[\d]{2}'
    if update == True:
        assert table_name is not None and c is not None, "Cursor to DB and table_name must be provided in order to update the given table"
        dates = get_update_dates(total_dates, c, table_name)
    else:
        for date in os.listdir(roto_dir):
        #     print(re.match(date_pat, date).group(0))
        #     print(date)
            try:
                date = pd.to_datetime(re.search(date_pat, date).group(0))
                dir_dates.add(date)
            except AttributeError: pass
        dates = sorted(list(dir_dates.intersection(total_dates_set)))

    # print(os.getcwd())
    total_df = pd.DataFrame()
    for date in tqdm(dates):
        date_str = str(date)[:10]
        local_filename = f'{roto_dir}/roto_data_{date_str}.html'
        data= BeautifulSoup(open(local_filename), features='lxml')#,'html.parser')

        trs = data.findAll('tr')
        if len(trs) == 0:
            continue
        tds = [tr.findAll('td') for tr in trs]
        player_data = [tr.text for tr in trs]
        pattern = '[A-Za-z]+, [A-Za-z]+'
    #     prog = re.compile(pattern)
        player_data_alt = [player[2:] if player[0] != 'C' else player[1:] for player in player_data]
        player_names = [re.search(pattern, player.replace('.','')).group(0).strip(' ') for player in player_data_alt if re.search(pattern, player.replace('.',''))]
        td_data = [pd.Series(td).apply(lambda x: x.text) for td in tds if len(td) ==9]
        player_df = pd.DataFrame(td_data)#.apply(lambda x: x.apply(lambda y: y.text))
        player_df['LastName, FirstName'] = player_names
        player_data_df = player_df.drop([1],axis=1)
        cols = ['Position', 'FD PTS', 'Salary', 'Team', 'Opp Team', 'Score', 'Min', 'Statline', 'LastName, FirstName']
        player_data_df.columns = cols

        player_data_df['Date'] = [date_str for _ in range(len(player_data_df['Position']))]
        new_cols = ['Date', 'Position', 'LastName, FirstName', 'FD PTS', 'Salary', 'Team', 'Opp Team', 'Score', 'Min', 'Statline']
        player_data_df = player_data_df[new_cols]
        player_data_df['Salary'] = player_data_df['Salary'].str.strip('$')
        player_data_df['Min'] = player_data_df['Min'].str.replace('DNP','0').replace('NA','0')

        player_data_df = player_data_df.astype({'Date':'datetime64'})
        total_df = total_df.append(player_data_df)
        # print(player_data_df)
        # time.sleep(100)
    return total_df


# def create_sql_roto(conn, c):
#     c.execute("""
#     CREATE TABLE roto_player_name (
#
#
#
#     )
#
#     """)

def load_nba_player_info(table_name, conn):
    pl = CommonAllPlayers()
    player_info = pl.get_data_frames()[0]
    player_info.to_sql(table_name, conn, if_exists='replace', index=False)
    print(f'{table_name} sucessfully created with {len(player_info)} rows')
    del player_info

def load_player_team_boxscores(conn, start_year, end_year, total_dates, update, sql_if_exists):
    # as of 12/25/20, 101105 rows in nba_player_boxscores and 9950 rows in nba_team_boxscores
    if update == True: start_year = end_year - 1
    yr_str = lambda yr: f'{yr}-{str(yr+1)[-2:]}'
    date_min, date_max = (str(total_dates.min().date()), str(total_dates.max().date()))
    print(date_min, date_max)
    box_table_dict = {'T': 'nba_team_boxscores', 'P': 'nba_player_boxscores'}
    for year in range(start_year, end_year):
        season_str = yr_str(year)
        for box_type in list(box_table_dict.keys()): # for boxscore type in player or team

            lgl = LeagueGameLog(season=season_str, player_or_team_abbreviation=box_type,\
             date_from_nullable=date_min, date_to_nullable=date_max)
            boxscores = lgl.get_data_frames()[0]
            boxscores['GAME_DATE'] = boxscores['GAME_DATE'].astype('datetime64')
            if year==start_year+1: sql_if_exists = 'append'
            table = box_table_dict[box_type]
            boxscores.to_sql(name=table, con=conn, if_exists=sql_if_exists, index=False)
            print(f'{season_str} "{box_type}" data ({len(boxscores)} rows) successfully loaded into {table}')

# def update_player_team_boxscores(c, conn, end_year, total_dates):
#     # The update function currently assumes the user only needs updates for the current season.
#     # Set update_boxscores to false if multiple seasons needed
#     yr_str = lambda yr: f'{yr}-{str(yr+1)[-2:]}'
#     date_min, date_max = (str(total_dates.min().date()), str(total_dates.max().date()))
#     box_table_dict = {'T': 'nba_team_boxscores', 'P': 'nba_player_boxscores'}
#     season_str = yr_str(end_year)
#     for box_type in list(box_table_dict.keys()):
#         lgl = LeagueGameLog(season=season_str, player_or_team_abbreviation=box_type,\
#             date_from_nullable=date_min, date_to_nullable=date_max)
#         boxscores = lgl.get_data_frames()[0]
#         boxscores['GAME_DATE'] = boxscores['GAME_DATE'].astype('datetime64')
#         boxscores.to_sql('tmp_boxscores', conn)
#         table =box_table_dict[box_type]
#         c.execute(f"""INSERT INTO {table}
#                       VALUES (SELECT * FROM tmp_boxscores WHERE NOT EXISTS (SELECT * ))""")


def preprocess_data(download_chromedriver, download_roto, get_dates, start_year, end_year, update, update_player_info, update_boxscores, **kwargs):
    tqdm.pandas()
    sys.path.insert(0, 'src')
    script_dir = os.getcwd()+'/src/'
    # TODO: add os and version number of chrome as a config param
    if download_chromedriver == True:
        # chromever = chrome_version()
        subprocess.check_call(['src/download_chromedriver.sh', chrome_version()])
        print(f'Successfully downloaded chromedriver at {os.getcwd()+"/src/"}')
        print('Remember to set download_chromedriver to False in config/etl-params.json')
    else: print(f"chromedriver already downloaded at {script_dir+'chromedriver'}")
    # print(script_dir)
    # time.sleep(10)
    dr = 'src/data/date_ranges/'
    total_dates = pd.Series(dtype='datetime64[ns]')
    if get_dates==True: total_dates = dates_scraper(start_year, end_year, dr)
    else:
        dates_fname = dr+f'{start_year}-{end_year}_season_dates.csv'
        print(f'Loading in dates from {dates_fname}')
        total_dates = pd.read_csv(dates_fname, parse_dates=[0], squeeze=True)
    total_dates = total_dates.loc[total_dates < (datetime.now() - timedelta(days=1))]
    if download_roto==True:
        driver = webdriver.Chrome(script_dir+'chromedriver') # change to your path for chromedriver
        print('Downloading roto_files up to ',total_dates.max())
        # time.sleep(10)
        total_dates.progress_apply(lambda date: download_roto_file(date, driver))
    else:
        print('Roto Files already downloaded')
    roto_table_name = 'roto_player_data'
    conn = sqlite3.connect('data/raw/nba_data.db')
    c = conn.cursor()
    # Turns all html files into pandas dataframes that will be written to a SQL DB
    total_df = combine_roto_data('data/raw/Roto_Data/Roto_html', total_dates, update, c=c, table_name=roto_table_name)

    # Writes combined data to csv and SQL
    print(len(total_df), 'number of rows')
    sql_if_exists, keyword = '', ''
    if update == False: sql_if_exists, keyword = 'replace', 'created'
    else: sql_if_exists, keyword = 'append', 'updated'
        # total_df.to_csv(f'data/raw/{roto_table_name}.csv', index=False)
    total_df.to_sql(roto_table_name, con=conn, index=False, if_exists=sql_if_exists)
    print(f'{roto_table_name} table {keyword} with {len(total_df)} (additional) rows')
    # total_df.to_sql(roto_table_name, con=conn, index=False, if_exists='append')
    # print(f'{roto_table_name} table updated with {len(total_df)} additional rows')
    ### Finished loading in roto data

    ### Now loading in NBA.com data via nba_api
    # Source: https://github.com/swar/nba_api
    # Loads in player_ids and basic info
    if update_player_info==True: load_nba_player_info('nba_player_info', conn)
    # Loads in player and team boxscores for the given dates
    ### TODO: update_boxscores should be combined with the generic update parameter
    ### TODO: make sure that total_dates starts at the latest date in the roto_html directory when update=True
    ### TODO: fix update method for boxscores, currently is appending when it should be updating, maybe execute a sql insert if update=True instead of boxscore.to_sql
    if update_boxscores == False:
        sql_if_exists, keyword = 'replace', 'created'
        load_player_team_boxscores(conn, start_year, end_year, total_dates, update_boxscores, sql_if_exists)

    else: sql_if_exists, keyword = 'append', 'updated'
    # create_sql_roto(total_df, conn, c)


    # driver = webdriver.Chrome(script_dir+'chromedriver')
