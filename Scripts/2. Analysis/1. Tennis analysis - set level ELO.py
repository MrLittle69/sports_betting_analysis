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


############################################################################
#1. Load cleaned Tennis data 
############################################################################

root = "C:/Users/oliver.cairns/Desktop/sports_betting_analysis/"

elo_df = pd.read_csv(root + "Data/tennis-data.co.uk/Clean data 2001 - 2016.csv")

#Other cleaning and sorting
elo_df['Date'] = pd.to_datetime(elo_df['Date'])


#For now, need to have the optimisation function in this file.
def optimize_brier(k_factor,args=(elo_df)):
    return elo.calc_brier_and_elos(elo_df,k_factor,ratings_dummy=False)

#Finds the optimal k factor using optimisation routine - takes quite a long time. Using output from last run.
"""
optimization = optimize.minimize(optimize_brier,method='BFGS',x0=15.24031615)
print(optimization)
k_star= optimization['x'] 
"""
k_star =  15.42498011

#Output data is the set level data (now with columns for player 1 winning chance and player 1 and 2 rating prior to game)
brier_score, output_data,ratings_dict = elo.calc_brier_and_elos(elo_df,k_star,ratings_dummy=True)

#Plot ELOs of best players. Also good visual check everything is working correctly
plt.plot(ratings_dict['Federer R.']['historic_dates'],ratings_dict['Federer R.']['historic_ratings'],'red',label='Roger Federer')
plt.plot(ratings_dict['Nadal R.']['historic_dates'],ratings_dict['Nadal R.']['historic_ratings'],'green',label='Rafael Nadal')
plt.plot(ratings_dict['Murray A.']['historic_dates'],ratings_dict['Murray A.']['historic_ratings'],'purple',label='Andy Murray')
plt.plot(ratings_dict['Djokovic N.']['historic_dates'],ratings_dict['Djokovic N.']['historic_ratings'],'brown',label='Novak Djokovic')
plt.legend(loc='upper left')
plt.show()

#Only evaluate betting on games after 1st 2 years - allow ELO to callibrate
betting_df = output_data[output_data['Date'].dt.year > 2002]

#Looking at match level accuracy. Therefore only taking 1 observation per match, and first one (with starting ELOs)
betting_df = betting_df[betting_df['set_num']==1]

#Winner of ovearll match is always player 1
betting_df['Outcome'] = 1.0

#This will be used by column-wise function match_winning_odds
betting_df['k_factor'] = k_star

#Compute my model's match winning odds. Hopefully they are more accurate than bookmaker :)
betting_df['model_prob'] = betting_df[['e1','Elo 1','Elo 2','first_to','k_factor']].apply(match_winning_odds, axis=1)
betting_df['model_loser_prob'] = 1.0 - betting_df['model_prob']

#check profitability, with different thresholds = how much higher my probability has to be than bookie odds before I bet.
check_profitability(df=betting_df,thresholds = [0,0.01,0.05,0.10,0.2])

#Export betting df - easy to check
betting_df.to_excel(root + "Data/Outputs/1. Tennis 2003 - 2016 without surfaces.xlsx")