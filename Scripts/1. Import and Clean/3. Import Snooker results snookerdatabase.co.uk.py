from time import sleep
import pandas as pd
import bs4
import requests

from IPython import embed

player_url = 'http://www.snookerdatabase.co.uk/PlayerStats.aspx?statKey=1&pg='
event_url = 'http://www.snookerdatabase.co.uk/EventResults.aspx?EventKey='
game_url = 'http://www.dartsdatabase.co.uk/PlayerDetails.aspx?PlayerKey=1&organPd=All&tourns=All&plStat=2#PlayerResults'
count = 0
waiting_period = 0
start_event = 1
end_event = 699

root = "/Users/oli/Desktop/tennis_analysis"

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

results_cols = ['player_1','player_2','result','tournament_name']

results_df = pd.DataFrame(columns=results_cols)

#load url + number
page_url = event_url + str(num)
page = requests.get(page_url,headers = headers)
parsed = bs4.BeautifulSoup(page.content,'lxml') 

#all sleeps are to avoid detection
sleep(waiting_period)

#find 3rd table on page --> players
tables = parsed.find_all("table")

count = 0

#loop should load 50 players/page
for num in range(start_event,end_event +1):
    try:
        #load url + number
        page_url = event_url + str(num)
        page = requests.get(page_url,headers = headers)
        parsed = bs4.BeautifulSoup(page.content,'lxml') 

        #all sleeps are to avoid detection
        sleep(waiting_period)
        
        tournament_name = parsed.find('h1').get_text()

        #find 3rd table on page --> players
        tables = parsed.find_all("table")
        results_table=tables[1]

        #find list of player data - 2nd row and later of table
        results = results_table.find_all('tr')
        #loop through list of player data, recording attribute
        for result in results:
            try:
            #find attributes
                attributes = result.find_all('td')
                player_1 = attributes[0].get_text()
                result = attributes[1].get_text()
                player_2 = attributes[2].get_text()

                #add atrributes to list
                result_hash = {'player_1':player_1, 'player_2': player_2, \
                 'result': result, 'tournament_name': tournament_name}
                results_df = results_df.append(result_hash,ignore_index=True)

            except:
                pass
    except:
        pass
    count +=1
    if count % 10 == 0:
        results_df.to_excel(root+"/snookerdatabase/Reults.xlsx")
    print(count)

results_df.to_excel(root+"/snookerdatabase/Reults.xlsx")