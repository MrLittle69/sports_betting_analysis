import pandas as pd
import os
from IPython import embed
import matplotlib.pyplot as plt
from scipy import optimize
from scipy.stats import norm
from statistics import variance
import numpy as np
from math import sqrt
from analysis_functions import plot_roc_curve
from analysis_functions import flip_underdog_wins

MATCHES_DF = pd.read_excel("..\\..\\Data\\dartsdatabase\\Averages.xlsx")


############################################################################
#2. Clean darts data 
############################################################################

#Drop matches that haven't yet happened
MATCHES_DF = MATCHES_DF[MATCHES_DF['result'] != 'fixture']

#Why are there some dups? Need to investigate
MATCHES_DF.drop_duplicates(inplace=True)

MATCHES_DF['date'] = pd.to_datetime(MATCHES_DF['date'])
MATCHES_DF['average'] = MATCHES_DF['averege'].str.replace("[^0-9\.]", "", n=-1, case=None, flags=0, regex=True)
MATCHES_DF['average'] = pd.to_numeric(MATCHES_DF['average'])

def find_prediction_error(h_life):
    MATCHES_DF['forecast'] = MATCHES_DF.groupby('player_name').average.apply(lambda x: x.ewm(halflife=20).mean())
    MATCHES_DF['validation'] = MATCHES_DF.groupby('player_name').average.shift()
    MATCHES_DF['error'] = (MATCHES_DF['forecast']-MATCHES_DF['validation'])**2
    return MATCHES_DF['error'].sum()

def calc_winning_chances(player_1,player_2,date):
    player_1_matches = MATCHES_DF[(MATCHES_DF['date'] < date) & (MATCHES_DF['player_name'] == player_1)]
    player_2_matches = MATCHES_DF[(MATCHES_DF['date'] < date) & (MATCHES_DF['player_name'] == player_1)]
    
    e_1 = player_1_matches['forecast'].iloc[-1]
    s_1 = variance(player_1_matches['forecast'])

    e_2 = player_2_matches['forecast'].iloc[-1]
    s_2 = variance(player_2_matches['forecast'])
    
    SE = sqrt(s_1 + s_2 )
    t = (e_1-e_2)/SE
    return norm.cdf(t)

brier = 0
h_star =  6

optimization = optimize.minimize_scalar(find_prediction_error,method='bounded',bounds=[0,50])
print(optimization)
h_star= optimization['x'] 

find_prediction_error(h_star)
brier = 0

for index, row in MATCHES_DF.iterrows():
    player_1 = row['player_name']
    player_2 = row['opponent']
    date = row['date']
    n1 =np.sum((MATCHES_DF['date']<date) & (MATCHES_DF['player_name']==player_1))
    n2 = np.sum((MATCHES_DF['date']<date) & (MATCHES_DF['player_name']==player_2))
    if min(n1,n2) > 5:
        e1 = calc_winning_chances(player_1,player_2,date)
        e2 = 1.0 - e1
        if row['result'] == 'Won':
            brier += e2*e2
        elif row['result'] == 'Lost':
            brier += e1*e1
        else:
            brier += ((1/2-e1)*(1/2-e1))+ ((1/2-e2)*(1/2-e2))
    
print(brier)

"""
van_gerwen = MATCHES_DF.loc[MATCHES_DF['player_name']=='Michael van Gerwen' ]

van_gerwen = van_gerwen.loc[van_gerwen['average']> 10 ]

forecast_series = van_gerwen[['average','date']]


forecast_series.sort_values('date',inplace=True)

stepwise_fit = auto_arima(forecast_series['average'], start_p=1, start_q=1,
                                max_p=3, max_q=3, m=12,
                                start_P=0, seasonal=True,
                                d=1, D=1, trace=True,
                                error_action='ignore',  # don't want to know if an order does not work
                                suppress_warnings=True,  # don't want convergence warnings
                                    stepwise=True)
"""
embed()

