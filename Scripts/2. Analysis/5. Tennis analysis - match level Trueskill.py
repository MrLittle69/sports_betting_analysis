# -*- coding: utf-8 -*-
"""
Created on Sat Apr 28 19:20:10 2018

@author: oliver.cairns
"""
import pandas as pd
import seaborn
import math
from matplotlib import pyplot as plt
from scipy import optimize
import numpy as np
import os
import trueskill
from IPython import embed


#Need to impliment
def apply_match_winning_odds(args):
    e1, rating_1, rating_2, match_total, k_factor = args
    wins_1 = 0.0
    wins_2 = 0.0
    pass

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

CURRENT_DIR = os.getcwd()

ROOT = CURRENT_DIR.replace("Scripts/2. Analysis","")

MATCHES_DF = pd.read_csv(ROOT + "Data/tennis-data.co.uk/Clean data 2001 - 2016.csv",index_col=0)

TAU = 0.6
EPSILON = 0.000001

#Other cleaning and sorting
MATCHES_DF['Date'] = pd.to_datetime(MATCHES_DF['Date'])

#Looking at match level data. Therefore only taking 1 observation per match, and first one (with starting ELOs)
MATCHES_DF = MATCHES_DF[MATCHES_DF['set_num']==1]

MATCHES_DF.drop(['winner_prob','set_num','first_to','Surface'],axis=1,inplace=True)

#Winner of ovearll match is always player 1
MATCHES_DF['Outcome'] = 1.0

#Duplicate df
opp_df = MATCHES_DF.copy()

opp_df['Outcome'] = 0.0
opp_df.rename(index=str,columns = {"Player 1":"Player 2","Player 2":"Player 1"},inplace=True)

MATCHES_DF = MATCHES_DF.append(opp_df,ignore_index=True,sort=True)

MATCHES_DF['Year-Month'] = MATCHES_DF['Date'].dt.to_period('M')

UNIQ_PLAYERS = MATCHES_DF['Player 1'].unique()

RATINGS_DF = pd.DataFrame(index=UNIQ_PLAYERS)

RATINGS_DF['rat'] = 0

RATINGS_DF['RD'] = 350/173.7178

RATINGS_DF['vol'] = 0.06

#Testing
test_period = MATCHES_DF.loc[(MATCHES_DF['Year-Month']== MATCHES_DF['Year-Month'].min())]
embed()
'''
period_agg_df = update_glickos(test_period)

RATINGS_DF.update(period_agg_df,overwrite=True)

for period in MATCHES_DF['Year-Month'].unique():
    print(period)
    period_df = MATCHES_DF[MATCHES_DF['Year-Month']==period]
    updated_ratings = update_glickos(period_df)
    RATINGS_DF.update(updated_ratings,overwrite=True)
'''