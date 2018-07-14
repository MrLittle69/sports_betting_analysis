# -*- coding: utf-8 -*-
"""
Created on Sat Apr 28 19:20:10 2018

@author: oliver.cairns
"""
import pandas as pd
import seaborn
import math
from scipy import optimize
import numpy as np
import os
from IPython import embed
from analysis_functions import plot_roc_curve
"""
Source: http://glicko.net/glicko/glicko2.pdf

Step 1: 

    Determine a rating and RD for each player at the onset of the rating period. The
    system constant, τ , which constrains the change in volatility over time, needs to be
    set prior to application of the system. Reasonable choices are between 0.3 and 1.2,
    though the system should be tested to decide which value results in greatest predictive
    accuracy. Smaller values of τ prevent the volatility measures from changing by large
    amounts, which in turn prevent enormous changes in ratings based on very improbable
    results. If the application of Glicko-2 is expected to involve extremely improbable
    collections of game outcomes, then τ should be set to a small value, even as small as,
    say, τ = 0.2.
    (a) If the player is unrated, set the rating to 1500 and the RD to 350. Set the player’s
    volatility to 0.06 (this value depends on the particular application).
    (b) Otherwise, use the player’s most recent rating, RD, and volatility σ.
    
    DONE - Initialising Gliko2 scaling to avoid steps 2 and 8.

Step 2. 

    For each player, convert the ratings and RD’s onto the Glicko-2 scale:
    µ = (r − 1500)/173.7178
    φ = RD/173.7178
    
    REDUNDANT - initialising with values 0 and 350/173.7178
    
    The value of σ, the volatility, does not change.
    We now want to update the rating of a player with (Glicko-2) rating µ, rating deviation
    φ, and volatility σ. He plays against m opponents with ratings µ1, . . . , µm, rating
    deviations φ1, . . . , φm. Let s1, . . . , sm be the scores against each opponent (0 for a loss,
    0.5 for a draw, and 1 for a win). The opponents’ volatilities are not relevant in the
    calculations.
    
    

Step 3. 

    Compute the quantity v. This is the estimated variance of the team’s/player’s
    rating based only on game outcomes.

    i)
    v = (Sum j g(φj )^2E(µ, µj, φj ){1 − E(µ, µj, φj )})^-1
    
    ii)
    g(φ) = 1 / 1 + 3φ2/π2
    
    iii)
    E(µ, µj, φj ) = 1 / 1 + exp(−g(φj )(µ − µj )).


Step 4. 

    Compute the quantity ∆, the estimated improvement in rating by comparing the
    pre-period rating to the performance rating based only on game outcomes.
    ∆ = v*sum( g(φj ){sj − E(µ, µj, φj )})
    with g() and E() defined above.

Step 5. 

    Determine the new value, σ' of the volatility. This computation requires iteration.
    
    2
    1. Let a = ln(σ2), and define
    f(x) = e^x(∆2 − φ 2 − v − ex) /2(φ2 + v + ex^)2 −(x − a)/τ2
    
    Also, define a convergence tolerance, ε. The value ε = 0.000001 is a sufficiently
    small choice.
    
    2. Set the initial values of the iterative algorithm.
    • Set A = a = ln(σ2)
    • If ∆2 > φ2 + v, then set B = ln(∆2 − φ2 − v).
    If ∆2 ≤ φ2 + v, then perform the following iteration:
    (i) Let k = 1
    (ii) If f(a − kτ ) < 0, then
    Set k ← k + 1
    Go to (ii).
    and set B = a − kτ . The values A and B are chosen to bracket ln(σI2), and
    the remainder of the algorithm iteratively narrows this bracket.
    
    3. Let fA = f(A) and fB = f(B).
    
    4. While |B − A| > ε, carry out the following steps.
    (a) Let C = A + (A − B)fA/(fB − fA), and let fC = f(C).
    (b) If fCfB < 0, then set A ← B and fA ← fB; otherwise, just set fA ← fA/2.
    (c) Set B ← C and fB ← fC.
    (d) Stop if |B − A| ≤ ε. Repeat the above three steps otherwise.
    5. Once |B − A| ≤ ε, set
    σ' ← eA/2


Step 6. 

    Update the rating deviation to the new pre-rating period value, φ'
    φ' = root(φ2 + σ2)

Step 7. 

    Update the rating and RD to the new values, µ' and φ':
    
    φ' = 1/root(1/φ'2 + 1/v)

    µ' = µ + φ'2 sum(g(φj ){sj − E(µ, µj, φj )}

Step 8 

    Redundant (using Gliko 2 scales)
                     
"""



def calc_g_ij(RD_j):
    return 1.0/math.sqrt((1+(3*RD_j**2))/math.pi**2)

def calc_E_ij(rat_i,rat_j,g_ij):
    return 1.0/(1 + math.exp(-g_ij*(rat_i - rat_j)))

def calc_v_inv_ij(E_ij,g_ij):
    return (g_ij ** 2) * E_ij * (1 - E_ij)

def calc_delta_ij(E_ij,g_ij,outcome):
    return g_ij  * (outcome - E_ij)

def f(x,delta_i,RD_i,v_i,TAU,a):
    e_x = math.exp(x)
    top_a = (e_x*(delta_i**2-RD_i**2-v_i-e_x))
    bottom_a = 2*((RD_i**2+v_i+e_x)**2)
    return top_a/bottom_a - (x-a)/(TAU**2)

def update_vol_i(vol_i,v_i,delta_i,RD_i):
    A = math.log(vol_i**2)
    a = math.log(vol_i**2)
    if vol_i**2 > RD_i**2 + v_i:
        B = math.log(vol_i**2 - RD_i**2 - v_i)
    else:
        k = 1
        x = A - k*TAU
        f_current = f(x,delta_i,RD_i,v_i,TAU,a)
        while f_current < 0:
            k +=1
            x = A - k*TAU
            f_current = f(x,delta_i,RD_i,v_i,TAU,a)
        B = A - k*TAU
    Fa = f(A,delta_i,RD_i,v_i,TAU,a)
    Fb = f(B,delta_i,RD_i,v_i,TAU,a)
    A_B_diff = abs(B-A)
    while A_B_diff > EPSILON:
        C = A + ((A-B)*Fa)/ (Fb - Fa)
        Fc = f(C,delta_i,RD_i,v_i,TAU,a)
        if Fc*Fb < 0:
            A = B
            Fa = Fb
        else:
            Fa /= 2
        B = C
        Fb = Fc
        A_B_diff = abs(B-A)
    return math.exp(A/2)
        
def update_rd_i(RD_i,v_i,vol_i):
    RD_pre_i = RD_i**2 + vol_i**2
    return 1/ math.sqrt(1/RD_pre_i + 1/ v_i)
    
def update_rat_i(RD_i,rat_i,perf_sum_i):
    return rat_i + ((RD_i**2)*perf_sum_i)

def update_glickos(period_df):
    #Merge on both player's ratings
    ##Preprocessing
    period_df = pd.merge(period_df,RATINGS_DF,how='inner',left_on='Player 1',right_index=True)
    period_df.rename(columns = {"rat":"rat_1","RD":"RD_1","vol":"vol_1"},inplace=True)
    period_df = pd.merge(period_df,RATINGS_DF,how='inner',left_on='Player 2',right_index=True)
    period_df.rename(columns = {"rat":"rat_2","RD":"RD_2","vol":"vol_2"},inplace=True)
    
    #Step 3 (not summed or inverted)
    period_df['g_12'] = period_df['RD_1'].apply(calc_g_ij)
    period_df['E_12'] = period_df.apply(lambda row: calc_E_ij(row['rat_1'],row['rat_2'],row['g_12']),axis=1)
    period_df['v_12'] = period_df.apply(lambda row: calc_v_inv_ij(row['E_12'],row['g_12']),axis=1)
    
    #Step 4 (not summed or multiplied by v)
    period_df['perf_sum_12'] = period_df.apply(lambda row: calc_delta_ij(row['E_12'],row['g_12'],row['Outcome']),axis=1)
    
    #Sum by player
    period_agg_df = period_df[['Player 1','v_12','perf_sum_12']].groupby('Player 1').sum()
    
    #Complete 3 (invert)
    period_agg_df['v'] = 1/period_agg_df['v_12'] 
    
    #Complete 4 (multiply by v)
    period_agg_df['delta'] = period_agg_df['v'] *period_agg_df['perf_sum_12']
    period_agg_df.drop(['v_12'],axis=1,inplace=True)
    
    #Merge ratings again
    period_agg_df = pd.merge(period_agg_df,RATINGS_DF,how='inner',left_on='Player 1',right_index=True)
 
    #Step 5 (most compute intensive - todo - check works and then optimise)
    period_agg_df['vol'] = period_agg_df.apply(lambda row: update_vol_i(row['vol'],row['v'],row['delta'],row['RD']),axis=1)
     
    #Steps 6-7
    period_agg_df['RD'] = period_agg_df.apply(lambda row: update_rd_i(row['RD'],row['v'],row['vol']),axis=1)
    period_agg_df['rat'] = period_agg_df.apply(lambda row: update_rat_i(row['RD'],row['rat'],row['perf_sum_12']),axis=1)

    output_ratings = period_agg_df[['rat','RD','vol']]

    output_predictions = period_df[['E_12']]
    return output_ratings, output_predictions

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

MATCHES_DF = pd.read_csv(ROOT + "/Data/tennis-data.co.uk/Clean data 2001 - 2016.csv",index_col=0)

TAU = 0.6
EPSILON = 0.000001

#Other cleaning and sorting
MATCHES_DF['Date'] = pd.to_datetime(MATCHES_DF['Date'])

#Looking at match level data. Therefore only taking 1 observation per match, and first one (with starting ELOs)
MATCHES_DF = MATCHES_DF[MATCHES_DF['set_num']==1]

MATCHES_DF.drop(['loser_prob','set_num','first_to','Surface'],axis=1,inplace=True)

#Winner of ovearll match is always player 1
MATCHES_DF['Outcome'] = 1

#Duplicate df
opp_df = MATCHES_DF.copy()

opp_df['Outcome'] = 0
opp_df.rename(index=str,columns = {"Player 1":"Player 2","Player 2":"Player 1"},inplace=True)

MATCHES_DF = MATCHES_DF.append(opp_df,ignore_index=True,sort=True)

MATCHES_DF.reset_index(inplace=True,drop=True)

MATCHES_DF['Year-Month'] = MATCHES_DF['Date'].dt.to_period('M')

UNIQ_PLAYERS = MATCHES_DF['Player 1'].unique()

RATINGS_DF = pd.DataFrame(index=UNIQ_PLAYERS)

RATINGS_DF['rat'] = 0

RATINGS_DF['RD'] = 350/173.7178

RATINGS_DF['vol'] = 0.06

#Testing - for now only taking first 5 years


#MATCHES_DF = MATCHES_DF.loc[(MATCHES_DF['Year-Month'] <  MATCHES_DF['Year-Month'].min() + 36)]


"""
test_period = MATCHES_DF.loc[(MATCHES_DF['Year-Month']== MATCHES_DF['Year-Month'].min())]

updated_ratings, period_predictions = update_glickos(test_period)

#RATINGS_DF.update(updated_ratings,overwrite=True)

#test_2 = pd.merge(MATCHES_DF,period_predictions,how='left',left_index=True,right_index=True)
"""


N = 1
for period in MATCHES_DF['Year-Month'].unique():
    print(period)
    period_df = MATCHES_DF[MATCHES_DF['Year-Month']==period]
    updated_ratings, period_predictions = update_glickos(period_df)
    RATINGS_DF.update(updated_ratings,overwrite=True)
    if N == 1:
        MATCHES_DF = pd.merge(MATCHES_DF,period_predictions,how='left',left_index=True,right_index=True)
    else:
        MATCHES_DF.update(period_predictions,overwrite=True)
    N += 1

assert MATCHES_DF[MATCHES_DF.E_12.isnull()].shape[0] == 0

test = MATCHES_DF[MATCHES_DF['Year-Month'] != MATCHES_DF['Year-Month'].min()]

test = MATCHES_DF[((MATCHES_DF['Year-Month'] <  MATCHES_DF['Year-Month'].min() + 60)
 & (MATCHES_DF['Outcome'] ==1)) | ((MATCHES_DF['Year-Month'] >=  MATCHES_DF['Year-Month'].min() + 60)
& (MATCHES_DF['Outcome'] ==0))]

test_1 = plot_roc_curve(test['Outcome'], test['E_12'])

test = test[test['winner_prob'].notnull()]
test_2 = plot_roc_curve(test['Outcome'], test['winner_prob'])
embed()

