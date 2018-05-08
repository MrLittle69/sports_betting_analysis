# -*- coding: utf-8 -*-
"""
Created on Sat Apr 28 19:20:10 2018

@author: oliver.cairns
"""
import pandas as pd
import seaborn

import elo_functions as elo
from matplotlib import pyplot as plt
from scipy import optimize
import numpy as np

#Solve recursive formula for base case, designed to be applied rowwise to pandas df
def match_winning_odds(args):
    e1, rating_1, rating_2, match_total, k_factor = args
    wins_1 = 0.0
    wins_2 = 0.0
    return elo.match_winning_prob(e1, rating_1,rating_2,wins_1,wins_2,match_total,k_factor)


#Check strategy profitability different confidence thresholds (how much does payoff have to exceed odds for me to bet?)
def check_profitability(df,thresholds):
    
    for threshold in thresholds:
    
        #Which cases would we have bet and won?
        model_wins = df[df['model_prob'] > df['winner_prob'] + threshold]
        
        #What was they net payoff in those cases for a bet of value 1? 
        total_wins = np.sum(1.0 / model_wins['winner_prob'] - 1)
        
        #Which cases would we have lost?
        model_losses = df['model_loser_prob'] < df['loser_prob'] - threshold
    
        #what was the net payoff in these cases (-1)
        total_losses = np.count_nonzero(model_losses)
    
        #print net payoff at threshold 
        print('threshold: ',str(threshold))
        print('payoff: ',total_wins-total_losses)
        print()


def outcome_map(result):
    if result == "Won":
        return 1.0
    elif result == "Lost":
        return 0.0
    else:
        return 0.5

############################################################################
#1. Load darts data 
############################################################################

root = "C:/Users/oliver.cairns/Desktop/sports_betting_analysis/"

matches_df = pd.read_excel(root + "Data/dartsdatabase/Results2.xlsx")


############################################################################
#2. Clean darts data 
############################################################################

#Drop matches that haven't yet happened
matches_df = matches_df[matches_df['result'] != 'fixture']

#Why are there some dups? Need to investigate
matches_df.drop_duplicates(inplace=True)

#Map outcomes to numerical values
matches_df['Outcome'] = matches_df['result'].apply(outcome_map)

#Rename columns - same as other versions
matches_df.rename(index=str, columns={"player_name": "Player 1", "opponent": "Player 2","date":"Date"},inplace=True)

matches_df['Tourn'] = matches_df['event'].str.upper()

matches_df['score'] =matches_df['score'].str.replace(' V ',':')



#Only keep relevant columns
elo_df = matches_df.loc[:,['Player 1','Player 2','Outcome','Date','Tourn','score']]

#Drop mirror image fixtures. Quite crude, need to check
already = []
for player_name in elo_df['Player 1'].unique():
    #Keep if - player name not current one, or rival not in 'already' group. 
    elo_df = elo_df[(elo_df['Player 1'] != player_name) | (-elo_df['Player 2'].isin(already))]
    already.append(player_name)

#Keep surname only
elo_df['Surname 1'] = elo_df['Player 1'].str.split(' ',n=1).str.get(1).str.upper().str.strip()
elo_df['Surname 2'] = elo_df['Player 2'].str.split(' ',n=1).str.get(1).str.upper().str.strip()



#Turn date into datetime variable
elo_df['Date'] = pd.to_datetime(elo_df['Date'])

elo_df['year'] =elo_df['Date'].dt.year

#Earliest fixtures first
elo_df.sort_values(by=['Date'],inplace=True)

#Merge on odds data - quite crude.

odds_df = pd.read_excel(root + "/Data/oddschecker/Darts_odds.xlsx")

odds_df['Player 1'] = odds_df['players'].str.split(' - ',n=1).str.get(0)
odds_df['Player 2'] = odds_df['players'].str.split(' - ',n=1).str.get(1)

odds_df['Surname 1'] = odds_df['Player 1'].str.slice(0,-2).str.upper().str.strip()
odds_df['Surname 2'] = odds_df['Player 2'].str.slice(0,-2).str.upper().str.strip()

odds_df['Tourn']=odds_df['tournament_name'].str.split('/').str.get(-1).str.replace("-"," ").str.upper()

#Same odds, the opposite way around
opp_df = odds_df.copy()

opp_df.rename(index=str, \
columns= {"odds_1": "odds_2", "odds_2": "odds_1","Player 1":"Player 2","Player 2":"Player 1","Surname 1":"Surname 2", \
"Surname 2":"Surname 1"},inplace=True)

#No
opp_df['score']=opp_df['score'].apply(lambda x: x[::-1])

odds_df = odds_df.append(opp_df,ignore_index=True)
    
    
combined_df = pd.merge(odds_df, elo_df,  how='outer',left_on=['Surname 1','Surname 2','Tourn','score'],right_on=['Surname 1','Surname 2','Tourn','score'],indicator=True)

print(combined_df['_merge'].value_counts())
"""
#For now, need to have the optimisation function in this file.
def optimize_brier(k_factor,args=(elo_df)):
    return elo.calc_brier_and_elos(elo_df,k_factor,ratings_dummy=False)

#Finds the optimal k factor using optimisation routine - takes quite a long time. Using output from last run.

optimization = optimize.minimize(optimize_brier,method='BFGS',x0=23)
print(optimization)
k_star= optimization['x'] 

k_star =   28.18944097

#Output data is the match level data (now with columns for player 1 winning chance and player 1 and 2 rating prior to game)
brier_score, output_data,ratings_dict = elo.calc_brier_and_elos(elo_df,k_star,ratings_dummy=True)

#Plot ELOs of best players. Good visual check that there are no massive errors
plt.plot(ratings_dict['Michael van Gerwen']['historic_dates'],ratings_dict['Michael van Gerwen']['historic_ratings'],'red',label='Michael van Gerwen')
plt.plot(ratings_dict['Phil Taylor']['historic_dates'],ratings_dict['Phil Taylor']['historic_ratings'],'green',label='Phil Taylor')
plt.plot(ratings_dict['James Wade']['historic_dates'],ratings_dict['James Wade']['historic_ratings'],'purple',label='James Wade')
plt.legend(loc='upper left')
plt.show()
"""