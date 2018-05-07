# -*- coding: utf-8 -*-
"""
Created on Sat Apr 28 12:10:28 2018

@author: oliver.cairns
"""
import pandas as pd
import seaborn
from matplotlib import pyplot as plt
from scipy import optimize


#Collected together my ELO functions
from elo_functions import *

#For now, need to have the optimisation function in this file.
def optimize_brier(k_factor,args=(elo_df)):
    elo_df = args
    return calc_brier_and_elos(elo_df,k_factor,ratings_dummy=False)


root_path = "C:/Users/oliver.cairns/Desktop/tennis_analysis/"

points_file_path = root_path + "jeff_sackman/charting-m-points.csv"

matches_file_path =  root_path + "jeff_sackman/charting-m-matches.csv"

#Load point data
points_df = pd.read_csv(points_file_path, error_bad_lines=False,encoding='latin1')

#Find only who won the last point of each match - and so the match overall
winner_df = points_df[['match_id','PtWinner']].groupby('match_id').last()

#Load game data
matches_df = pd.read_csv(matches_file_path, error_bad_lines=False,encoding='latin1',quoting=3,index_col='match_id')

winner_df = winner_df.join(matches_df,how='inner')

#Dummy variable. 1 if first player won, otherwise 0.
winner_df['Outcome'] = 2.0 - winner_df['PtWinner']
elo_df = winner_df[['Player 1','Player 2','Outcome','Date']] 

elo_df = elo_df[elo_df['Outcome'] >= 0.0]

elo_df['Date'] = pd.to_datetime(elo_df['Date'])

#Train - just on earlier data
elo_df = elo_df[elo_df['Date'].dt.year < 2017]

#Finds the optimal k factor - takes quite a long time

optimization = optimize.minimize(optimize_brier,method='BFGS',x0= 15.24031615,args=(elo_df))
print(optimization)
k_star= optimization['x'] 

#k_star = 15.24031615

brier_score, matches_data,ratings_dict = calc_brier_and_elos(elo_df,k_star,ratings_dummy=True)

plt.plot(ratings_dict['Roger Federer']['historic_dates'],ratings_dict['Roger Federer']['historic_ratings'],'red',label='Roger Federer')
plt.plot(ratings_dict['Rafael Nadal']['historic_dates'],ratings_dict['Rafael Nadal']['historic_ratings'],'green',label='Rafael Nadal')
plt.plot(ratings_dict['Andy Murray']['historic_dates'],ratings_dict['Andy Murray']['historic_ratings'],'purple',label='Andy Murray')
plt.plot(ratings_dict['Novak Djokovic']['historic_dates'],ratings_dict['Novak Djokovic']['historic_ratings'],'brown',label='Novak Djokovic')
plt.legend(loc='upper left')
plt.show()
"""
"""