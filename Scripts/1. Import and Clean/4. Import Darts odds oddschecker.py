from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import pandas as pd

from IPython import embed

root = "/Users/oli/Desktop/tennis_analysis"

start_year, end_year = [2010,2018]

# instantiate a chrome options object so you can set the size and headless preference
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")

# download the chrome driver from https://sites.google.com/a/chromium.org/chromedriver/downloads and put it in the
# current directory
chrome_driver = os.getcwd() + "/chromedriver"

tournament_names = ["premier-league-","pdc-world-championship-","grand-slam-"]

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)


odds_cols = ['player_1','player_2','result','tournament_name','year']

odds_df = pd.DataFrame(columns=odds_cols)

for tourn in tournament_names:

    for year in range(start_year,end_year+1):
        page_url = "http://www.oddsportal.com/darts/world/" + \
        str(year) + "/results/"
        try:
            driver.get(page_url)

            table = driver.find_element_by_id('tournamentTable')
            rows = table.find_elements_by_class('deactivate')
            for row in rows:
                try:
                    players = row.find_element_by_class_name('name').text
                    score = row.find_element_by_class_name('table-score').text
                    odds_1 = row.find_elements_by_class_name('odds-nowrp')[0].text
                    odds_2 = row.find_elements_by_class_name('odds-nowrp')[1].text
                    #add atrributes to list
                    odds_hash = {'players':players, 'odds_1': odds_1, \
                        'odds_2': odds_2, 'year': year,'tournament_name':tourn}
                    odds_df = odds_df.append(odds_hash,ignore_index=True)
                except:
                    pass
        except:
            pass

print(odds_df)
embed()