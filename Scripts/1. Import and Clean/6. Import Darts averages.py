from time import sleep
import pandas as pd
import bs4
import requests
from IPython import embed
import os

# params
GAME_URL = 'http://www.dartsdatabase.co.uk/PlayerDetails.aspx?PlayerKey=1&organPd=All&tourns=All&plStat=2#PlayerResults'
COUNT = 0
WAITING_PERIOD = 0
MAX_RESULTS_PAGE = 60

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


PLAYERS_DF = pd.read_excel("../../Data/dartsdatabase/Players.xlsx")

RESULTS_COLS = ['player_name', 'date', 'event', 'category', 'event_round', 'result', 'opponent', 'score','average']

RESULTS_DF = pd.DataFrame(columns=RESULTS_COLS)

#loop through player list
for index, player in PLAYERS_DF.iterrows():
    player_link = player['link']
    PAGE_COUNT = 0
    flag = True
    
    #Keep looping until either error, or maximum page visited.
    while flag and PAGE_COUNT < MAX_RESULTS_PAGE:
        try:
            PAGE_COUNT += 1
            
            #Make URL with specific player and page number
            page_link = 'http://www.dartsdatabase.co.uk/' + player_link + "&organPd=All&tourns=All&plStat=4&pg=" + \
            str(PAGE_COUNT) + "#PlayerResults"
            
            page = requests.get(page_link)
            parsed = bs4.BeautifulSoup(page.content,'lxml') 
            tables = parsed.find_all('table')
            sleep(WAITING_PERIOD)
            results_rows = tables[4].find_all('tr')
            
            #Remove header again
            header = results_rows.pop(0)
            
            #if no table on page - move onto next player
            if len(results_rows) < 2:
                flag = False
                break
    
            for row in results_rows:
                #find specific result and add to list
                attributes = row.find_all('td')
                att_text =  [a.get_text() for a in attributes]
                date, event, category, event_round, result, opponent, score, average = att_text
                player_name = player['name']
                result_hash = {'player_name': player_name, 'date': date, 'event': event, 'category': category, 'event_round': event_round, 'result': result, 'opponent': opponent, 'score': score, 'average':average}
                RESULTS_DF = RESULTS_DF.append(result_hash,ignore_index=True)
        
        #If getting results data threw an error, move onto next page
        except Exception as e: 
            print(e)
            flag = False
            break
			#print sample output
        
    #measure progress. Save to csv every 10 players
    print(player)
    print('Pages: ', str(PAGE_COUNT-1))
    if COUNT % 10 == 0:
        RESULTS_DF.to_csv("../../Data/dartsdatabase/Averages.csv")
    print('Count: ',index)
    print()
    
RESULTS_DF.to_csv("../../Data/dartsdatabase/Averages.csv")
