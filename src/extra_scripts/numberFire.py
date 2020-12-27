#import selenium
import os
from selenium import webdriver
from bs4 import BeautifulSoup


url = 'https://www.numberfire.com/nba/daily-fantasy/daily-basketball-projections'


driver = webdriver.Chrome('/Users/jordanlevy/Downloads/chromedriver')
script_dir = os.path.dirname(__file__)



def import_numberFire():
    driver.get(url)
    driver.implicitly_wait(10)
    #soup = BeautifulSoup(driver.page_source, 'html5lib')
    return driver.find_elements_by_xpath('/html/body/main/div[2]/div[4]/div/span[2]/a').click()



print(import_numberFire())
