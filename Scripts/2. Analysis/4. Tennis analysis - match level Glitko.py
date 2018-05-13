# -*- coding: utf-8 -*-
"""
Created on Sat Apr 28 19:20:10 2018

@author: oliver.cairns
"""
import pandas as pd
import seaborn
import math
import elo_functions as elo
from matplotlib import pyplot as plt
from scipy import optimize
import numpy as np

tau = 0.6

def g(RD):
    return 1.0/math.sqrt((1+(3*RD**2))/math.pi**2)

def E(rating,rating_j,RD_j):
    return 1.0/(1 + math.exp(-g(RD_j)*(rating - rating_j)))

def v_and_delta(player_matches,player_name,ratings_dict):
    rating = ratings_dict[player_name]['rating']
    v_total = 0.0
    delta_total = 0.0
    
    for match_j in player_matches:
        rating_j = ratings_dict[player_matches['rival_name']]['rating']
        RD_j = ratings_dict[player_matches['rival_name']]['RD']
        outcome_j = player_matches['outcome']
        E_j =E(rating,rating_j,RD_j)
        g_j = g(RD_j)
        v_total +=  E_j*(1-E_j)*(g_j**2)
        delta_total + g_j*(outcome_j- E_j)
        
    return 1.0/v_total, delta_total

def f(x,delta_i,RD_i,v_i,tao,a):
    e_x = math.exp(x)
    top_a = (e_x*(delta_i**2-RD_i**2-v_i-e_x))
    bottom_a = 2*((RD_i**2+v_i+e_x)**2)
    return top_a/bottom_a + (x-a)/(tao**2)

def update_vol_i():
    a = math.log(RD_i**2)


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


#Looking at match level data. Therefore only taking 1 observation per match, and first one (with starting ELOs)
elo_df = elo_df[elo_df['set_num']==1]

#Winner of ovearll match is always player 1
elo_df['Outcome'] = 1.0

elo_df['Year-Month'] = elo_df['Date'].dt.to_period('M')


unique_players = set(elo_df['Player 1']).union(set(elo_df['Player 2']))

vol_change = 0.75

ratings_dict = {}
for player in unique_players:
    ratings_dict[player]={'rating':0,'RD':350/173.7178,'vol':0.06}
    
uniq_months=  elo_df['Year-Month'].unique()

for month in uniq_months:
    period_df = elo_df[elo_df['Year-Month']==month]