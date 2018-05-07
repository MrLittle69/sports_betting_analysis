from time import sleep
import pandas as pd
import bs4
import requests
from IPython import embed


# params
player_url = 'http://www.dartsdatabase.co.uk/PlayerStats.aspx?statKey=1&pg='
game_url = 'http://www.dartsdatabase.co.uk/PlayerDetails.aspx?PlayerKey=1&organPd=All&tourns=All&plStat=2#PlayerResults'
count = 0
waiting_period = 0
max_player_page = 10
max_results_page = 60

root = "C:/Users/oliver.cairns/Desktop/sports_betting_analysis/"

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

#list of players
players_cols = ['name','rank','country','link']

players_df = pd.DataFrame(columns=players_cols)

#loop should load 50 players/page
for num in range(1,max_player_page +1):
    try:
        #load url + number
        page_url = player_url + str(num)
        page = requests.get(page_url,headers = headers)
        parsed = bs4.BeautifulSoup(page.content,'lxml') 

        #all sleeps are to avoid detection
        sleep(waiting_period)
        
        #find 3rd table on page --> players
        tables = parsed.find_all("table")
        ranking_table=tables[2]

    		#find list of player data - 2nd row and later of table
        players = ranking_table.find_all('tr')
        
        #Remove header
        players.pop(0)
        #loop through list of player data, recording attribute
        for player in players:
            try:
                #find attributes
                attributes = player.find_all('td')
                rank = attributes[0].get_text()
                name = attributes[1].get_text()
                country = attributes[2].get_text()
                link = attributes[1].find('a')['href']
            except:
            #error handling - nested and ugly throughout!
                rank = 'error'
                name = 'error'
                country = 'error'
                link = 'error'
            
            #add atrributes to list
            player_hash = {'name':name, 'rank': rank, 'country': country, 'link': link}
            players_df = players_df.append(player_hash,ignore_index=True)
		
    except:
        print('failure. Number ',num)
	
    	#track progress
    count += 1 

players_df.to_excel(root+"Data/dartsdatabase/Players.xlsx")

results_cols = ['player_name', 'date', 'event', 'category', 'event_round', 'result', 'opponent', 'score']

results_df = pd.DataFrame(columns=results_cols)

players_df = players_df[players_df.rank > 60 & players_df.rank < 301]


#loop through player list
for index, player in players_df.iterrows():
    player_link = player['link']
    page_count = 0
    flag = True
    
    #Keep looping until either error, or maximum page visited.
    while flag and page_count < max_results_page:
        try:
            page_count += 1
            
            #Make URL with specific player and page number
            page_link = 'http://www.dartsdatabase.co.uk/' + player_link + "&organPd=All&tourns=All&plStat=2&pg=" + \
            str(page_count) + "#PlayerResults"
    
            
            page = requests.get(page_link)
            parsed = bs4.BeautifulSoup(page.content,'lxml') 
            tables = parsed.find_all('table')
            sleep(waiting_period)
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
                date = attributes[0].get_text()
                event= attributes[1].get_text()
                category = attributes[2].get_text()
                event_round = attributes[3].get_text()
                result = attributes[4].get_text()
                opponent = attributes[5].get_text()
                score = attributes[6].get_text()
                player_name = player['name']
                result_hash = {'player_name': player_name, 'date': date, 'event': event, 'category': category, 'event_round': event_round, 'result': result, 'opponent': opponent, 'score': score}
                results_df = results_df.append(result_hash,ignore_index=True)
        
        #If getting results data threw an error, move onto next page
        except:
            flag = False
            break
			#print sample output
        
    #measure progress. Save to Excel every 10 players
    print(player)
    print('Pages: ', str(page_count-1))
    if count % 10 == 0:
        results_df.to_excel(root+"Data/dartsdatabase/Results2.xlsx")
    print('Count: ',index)
    print()
    
#save as Excel

results_df.to_excel(root+"/dartsdatabase/Results2.xlsx")
