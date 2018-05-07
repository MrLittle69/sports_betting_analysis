# -*- coding: utf-8 -*-
"""
Created on Sat Apr 28 19:20:10 2018

@author: oliver.cairns
"""
import pandas as pd
import numpy as np

root = "C:/Users/oliver.cairns/Desktop/sports_betting_analysis/"

#page_url = "https://raw.githubusercontent.com/JeffSackmann/tennis_MatchChartingProject/master/charting-m-points.csv"

######################################################################
# 1 - Import raw data on results and odds, downloaded as Excel files and combine as one DF.
#######################################################################

min_year = 2001
max_year = 2018

for year in range(min_year,max_year+1):
    
    #Difference in file types - xlx after 2012
    if year < 2013:
        year_path = root + "Data/tennis-data.co.uk/" + str(year) + ".xls"
    else:
        year_path = root + "Data/tennis-data.co.uk/" + str(year) + ".xlsx"
    year_df = pd.read_excel(year_path, error_bad_lines=False,encoding='latin1')
    
    #Append together into one dataframe - matches_df
    if year == min_year:
        matches_df = year_df
    else:
        matches_df = matches_df.append(year_df)


######################################################################
# 2 - Basic data processing
#######################################################################


#Moke column outcome - checking if player 1 won the relevant set (nan if set didn't take place)
for i in range(1,6):
    matches_df['O_' +str(i)] = np.select(((matches_df['W'+str(i)].isnull() | matches_df['L'+str(i)].isnull()), 
                        matches_df['W'+str(i)] > matches_df['L'+str(i)], matches_df['W'+str(i)] < matches_df['L'+str(i)]), 
                        [np.NaN, 1, 0])

#Bookies' odds are the columns ending with W and L. Take the largest -> best odds    
matches_df["winner_odds"] = matches_df[matches_df.columns[pd.Series(matches_df.columns).str.endswith('W')]].max(axis=1)
matches_df["loser_odds"] = matches_df[matches_df.columns[pd.Series(matches_df.columns).str.endswith('L')]].max(axis=1)

#Compute the implied probability of winning
matches_df["winner_prob"] = 1.0 / matches_df["winner_odds"]
matches_df["loser_prob"] = 1.0 / matches_df["loser_odds"]

#Find what each set was first to. E.g. best of 5 = first to 3.
matches_df['first_to'] = np.ceil(matches_df['Best of']/2).astype(int)

#Reset index
matches_df.reset_index(drop=True,inplace=True)
matches_df["match_id"] = np.copy(matches_df.index)

#Reshape long - Now each set is a different column
matches_df = pd.wide_to_long(matches_df, stubnames='O_', i='match_id', j='set_num').reset_index()

#Convert to number - will be string 1-5
matches_df['set_num'] = pd.to_numeric(matches_df['set_num'])

#Fix so can use default elo functions
matches_df.rename(index=str, columns={"Winner": "Player 1", "Loser": "Player 2","O_":"Outcome"},inplace=True)

#Take subset - which columns are we using for this analysis?

elo_df = matches_df.loc[:,['Player 1','Player 2','Outcome','set_num','Date','match_id','winner_prob','loser_prob','first_to','Surface']]

#Combine carpets with grass - fewer permuations for optimisation
elo_df.loc[elo_df['Surface'] == "Carpet", 'Surface'] = "Grass"

#Other cleaning and sorting
elo_df['Date'] = pd.to_datetime(elo_df['Date'])
elo_df.sort_values(by=['Date','match_id', 'set_num'],inplace=True)
elo_df= elo_df[elo_df['Outcome'].notnull()]

#Train - just on earlier data. If we have interesting results, will validate on 2017 onwards.
elo_df = elo_df[elo_df['Date'].dt.year < 2017]
elo_df.reset_index(drop=True,inplace=True)

elo_df.to_csv(root + "Data/tennis-data.co.uk/Clean data 2001 - 2016.csv")