
import pandas as pd
import os
from IPython import embed
from pyramid.arima import auto_arima
import matplotlib.pyplot as plt

CURRENT_DIR = os.getcwd()

ROOT = CURRENT_DIR.replace("Scripts/2. Analysis","")

MATCHES_DF = pd.read_excel(ROOT + "/Data/dartsdatabase/Averages.xlsx")


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

embed()

