import pandas as pd
import seaborn
import os
import elo_functions_surfaces as elo_sf
import elo_functions as elo
from matplotlib import pyplot as plt
from scipy import optimize
import numpy as np
from analysis_functions import check_profitability, flip_underdog_wins, plot_roc_curve
from IPython import embed

def match_winning_odds(args):
    ''''Solve recursive formula for base case, designed to be applied rowwise to pandas df'''
    e1, rating_1, rating_2, match_total, k_factor = args
    wins_1 = 0.0
    wins_2 = 0.0
    return elo.match_winning_prob(e1, rating_1,rating_2,wins_1,wins_2,match_total,k_factor)

CURRENT_DIR = os.getcwd()

ROOT = CURRENT_DIR.replace("Scripts/2. Analysis","")

elo_df = pd.read_csv(ROOT + "/Data/tennis-data.co.uk/Clean data 2001 - 2016.csv")

#Other cleaning and sorting
elo_df['Date'] = pd.to_datetime(elo_df['Date'])

#For now, need to have the optimisation function in this file.
def optimize_brier(params,args=(elo_df)):
    return elo_sf.calc_brier_and_elos(elo_df,params,brier_sum_only=True)

#Finds the optimal k factor using optimisation routine - takes quite a long time. Using output from last run.

"""
optimization = optimize.minimize(optimize_brier,method='BFGS',x0=[15.24031615,0.7,0.7,0.7])
print(optimization)

params= optimization['x']
"""
params = [ 19.17,   0.8234,   0.4122,   0.6275]

#Output data is the set level data (now with columns for player 1 winning chance and player 1 and 2 rating prior to game)
output_data = elo_sf.calc_brier_and_elos(elo_df,params,brier_sum_only=False)

'''
#Plot ELOs of best players. Also good visual check everything is working correctly
plt.plot(ratings_dict['Federer R.']['historic_dates'],ratings_dict['Federer R.']['historic_ratings'],'red',label='Roger Federer')
plt.plot(ratings_dict['Nadal R.']['historic_dates'],ratings_dict['Nadal R.']['historic_ratings'],'green',label='Rafael Nadal')
plt.plot(ratings_dict['Murray A.']['historic_dates'],ratings_dict['Murray A.']['historic_ratings'],'purple',label='Andy Murray')
plt.plot(ratings_dict['Djokovic N.']['historic_dates'],ratings_dict['Djokovic N.']['historic_ratings'],'brown',label='Novak Djokovic')
plt.legend(loc='upper left')
plt.show()
'''

#Only evaluate betting on games after 1st 2 years - allow ELO to callibrate
betting_df = output_data[output_data['Date'].dt.year > 2002]

#Looking at match level accuracy. Therefore only taking 1 observation per match, and first one (with starting ELOs)
betting_df = betting_df[betting_df['set_num']==1]

#Winner of ovearll match is always player 1
betting_df['Outcome'] = 1.0


#Compute my model's match winning odds. Hopefully they are more accurate than bookmaker :)
betting_df['model_prob'] = betting_df[['E 1','Rating 1','Rating 2','first_to','K Factor']].apply(match_winning_odds, axis=1)

betting_df['Outcome']= betting_df['Outcome'].apply(lambda x: int(x))

betting_df[['model_prob','Player 1','Player 2','Outcome']] = \
betting_df[['model_prob','Player 1','Player 2','Outcome']].apply(flip_underdog_wins,axis=1).apply(pd.Series)

test_1 = plot_roc_curve(betting_df['Outcome'], betting_df['model_prob'])

