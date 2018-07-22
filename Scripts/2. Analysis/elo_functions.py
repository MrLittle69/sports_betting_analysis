import pandas as pd
from IPython import embed
#updates the global ratings_dict, given a single game + k-factor
def update_elos_and_gen_brier(args):
    player_1, player_2,k_factor,outcome= args
    rating_1 = RATINGS_SERIES[player_1]
    rating_2 = RATINGS_SERIES[player_2]
    e1, rating_1_new, rating_2_new = update_elos(rating_1,rating_2,outcome,k_factor)
    
    RATINGS_SERIES[player_1] = rating_1_new
    RATINGS_SERIES[player_2] = rating_2_new

    #measure performance of prediction vs actual win/loss draw. Brier change = square of prediction error.    
    brier =  (outcome - e1)**2
    return rating_1_new, rating_2_new, e1, brier

def calc_brier_and_elos(matches_df,k_factor,brier_sum_only):
    uniq_players = matches_df['Player 1'].append(matches_df['Player 2']).unique()

    global RATINGS_SERIES
    RATINGS_SERIES = pd.Series(index=uniq_players,data=1200)

    matches_df['K Factor'] = k_factor
    
    matches_df[['Rating 1','Rating 2','E 1','Brier']] = matches_df[['Player 1','Player 2','K Factor','Outcome']].apply(update_elos_and_gen_brier,axis=1).apply(pd.Series)
    
    if brier_sum_only:
        return matches_df['Brier'].sum()
    else:
        return matches_df

#Helper function for recursive match_winning_prob. Simply returns expectation, and updated elos for given match expectation
def update_elos(rating_1,rating_2,outcome,k_factor):
    
    q1 =10.0 ** (rating_1/400)
    q2 =10.0 ** (rating_2/400)
    e1 = q1/(q1+q2)
    
    rating_1 += (outcome-e1)*k_factor
    
    rating_2 += (e1-outcome)*k_factor
         
    return e1, rating_1, rating_2

#Recursive formula for finding the odds of player 1 giving a match of length 'match total' given current score 'wins1' and 'wins2'
def match_winning_prob(e1, rating_1,rating_2,wins_1,wins_2,match_total,k_factor):
    
    #Cannot use simple binomial calcs, because this is the 'hot' simulation - updating ability after simmed wins.
    
    #Base case 1 - player wins return 100%
    if wins_1 == match_total:
        return 1.0
    
    #Base case 2 - player loses return 0%
    elif wins_2 == match_total:
        return 0.0
    
    #Recursive component - if game is not over, then recursively find chance of winning given the two set outcomes
    else:
        
        #compute the new ELOs and expectations conditional on win/lose
        e1_win, r_1_win, r_2_win = update_elos(rating_1=rating_1,rating_2=rating_2,k_factor=k_factor,outcome=1.0) 
        e1_lose, r_1_lose, r_2_lose = update_elos(rating_1=rating_1,rating_2=rating_2,k_factor=k_factor,outcome=0.0) 
        
        #use these to return chance of winning conditional on win/lose
        return e1 * match_winning_prob(e1_win, r_1_win,r_2_win,wins_1+1,wins_2,match_total,k_factor) + \
        (1-e1) * match_winning_prob(e1_lose, r_1_lose,r_2_lose,wins_1,wins_2+1,match_total,k_factor)

