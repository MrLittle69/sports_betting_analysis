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
import elo
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

TAU = 0.6
EPSILON = 0.000001


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
        s_j = player_matches['outcome']
        E_j =E(rating,rating_j,RD_j)
        g_j = g(RD_j)
        v_total +=  (g_j**2)*E_j*(1-E_j)
        delta_total += g_j*(s_j- E_j)
        
    return 1.0/v_total, delta_total

def f(x,delta_i,RD_i,v_i,TAU,a):
    e_x = math.exp(x)
    top_a = (e_x*(delta_i**2-RD_i**2-v_i-e_x))
    bottom_a = 2*((RD_i**2+v_i+e_x)**2)
    return top_a/bottom_a + (x-a)/(TAU**2)

def update_vol_i(player_matches,player_name,ratings_dict):
    vol_i = ratings_dict[player_name]['vol']
    RD_i = ratings_dict[player_name]['RD']
    A = math.log(vol_i**2)
    v_i, delta_i = v_and_delta(player_matches,player_name,ratings_dict)
    if vol_i**2 > RD_i**2 + v_i:
        B = math.log(vol_i**2 - RD_i**2 - v_i)
    else:
        k = 1
        while f(A - k*TAU) < 0:
            k +=1
        B = A - k*TAU
    Fa = f(A)
    Fb = f(B)
    while abs(B - A) > EPSILON:
        C = A + ((A-B)*Fa)/ (Fb - Fa)
        Fc = f(C)
        if Fc*Fb < 0:
            A = B
            Fa = Fb
        else:
            Fa /= 2
        B = C
        Fb = Fc
    return math.exp(A/2)
        
def update_rd_i(RD_i,sigma_i):
    return math.sqrt(RD_i**2,sigma_i**2)
    

            


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

ratings_df = pd.DataFrame(columns = ['player','rating','RD','vol'])

for player in unique_players:
    ratings_df.append({'player':player,'rating':0,'RD':350/173.7178,'vol':0.06})
    
uniq_months=  elo_df['Year-Month'].unique()

for month in uniq_months:
    period_df = elo_df[elo_df['Year-Month']==month]