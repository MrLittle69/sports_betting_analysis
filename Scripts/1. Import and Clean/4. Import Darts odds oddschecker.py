from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import pandas as pd

from IPython import embed

root = "C:/Users/oliver.cairns/Desktop/sandbox/ad_hoc/sports_betting_analysis/"

start_year, end_year = [2010,2018]

# instantiate a chrome options object so you can set the size and headless preference
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")

# download the chrome driver from https://sites.google.com/a/chromium.org/chromedriver/downloads and put it in the
# current directory
chrome_driver = "chromedriver.exe"

tournament_names = ["premier-league","pdc-world-championship"]

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)

odds_df = pd.DataFrame()

#1. scrape all tournaments

tourn_list_url = "http://www.oddsportal.com/darts/results/"

driver.get(tourn_list_url)

table = driver.find_element_by_class_name("table-main")

links = table.find_elements_by_tag_name('a')

#Find all the HREFS in the table
links = [x.get_attribute('href') for x in links]

#Keep only the ones with the word results. These are actual tournaments. 
#Also drop the /results bit because we will add - year in between

tourns = [link.replace('/results/','') for link in links if '/results/' in link]

for i, tourn in enumerate(tourns):
    print('--------------')
    print(i)
    
    for year in range(start_year,end_year+1):
        print('Tournament: ',tourn)
        print('Year: ',year)
        print()
        if year == 2018:
            page_url = tourn + "/results/"
        else:
            page_url = tourn + "-" + str(year) + "/results/"
        
        print(page_url)
        try:
            driver.get(page_url)

            table = driver.find_element_by_id('tournamentTable')
            rows = table.find_elements_by_class_name('deactivate')
            embed()
            for row in rows:
                try:
                    players = row.find_element_by_class_name('name').text
                    score = row.find_element_by_class_name('table-score').text
                    odds_1 = row.find_elements_by_class_name('odds-nowrp')[0].text
                    odds_2 = row.find_elements_by_class_name('odds-nowrp')[1].text
                    #add atrributes to list
                    odds_hash = {'players':players, 'odds_1': odds_1, \
                        'odds_2': odds_2, 'year': year,'tournament_name':tourn,'score':score}
                    odds_df = odds_df.append(odds_hash,ignore_index=True)
                except:
                    print('fail')
                    pass
                    
        except:
            pass
    if i % 5 == 0:
        odds_df.to_excel(root+"/Data/oddschecker/Darts_odds.xlsx")

odds_df.to_excel(root+"/Data/oddschecker/Darts_odds.xlsx")
