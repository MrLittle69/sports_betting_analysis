import copy
from IPython import embed
import pandas as pd

def update_elos_and_gen_brier(args):
    '''
    Designed to be applied to df of matches, requires global RATINGS_DF with latest ELOS
    Unpacks 'args' to make player_1, player_2,k_factor,outcome,surface
    Updates the global RATINGS_DF, given a single game + k-factor as side effect.
    Also returns  rating_1, rating_2, e1, brier, which should be unpacked and added to df rowwise
    '''
    player_1, player_2,k_factor,outcome, match_surface = args
    rating_1 = RATINGS_DF[match_surface][player_1]
    rating_2 = RATINGS_DF[match_surface][player_2]
    
    q1 =10.0 ** (rating_1/400)
    q2 =10.0 ** (rating_2/400)
    e1 = q1/(q1+q2)
    e1_diff = outcome-e1

    for surface_rat in ['Grass','Hard','Clay']:
        RATINGS_DF[surface_rat][player_1] += (e1_diff*k_factor*SURFACE_MATRIX[match_surface][surface_rat])
        RATINGS_DF[surface_rat][player_1] -= (e1_diff*k_factor*SURFACE_MATRIX[match_surface][surface_rat])

    #measure performance of prediction vs actual win/loss draw. Brier change = square of prediction error.    
    brier =  (outcome - e1)**2
    return rating_1, rating_2, e1, brier

def calc_brier_and_elos(matches_df,params,brier_sum_only):
    '''
    Designed to be applied to entire dataframe of matches - needs matches df to have columns:
        'Player 1' - str 
        'Player 2' - str
        'Outcome' - int O/1
    
    params = list: unpkacked to make to make the following params
        k_factor int - how fast should ratings update given wins?
        grass_hard - how much should wins on grass influence hard court ratings and vica versa?
        grass_clay - as above for clay and grass
        hard_clay - as above for hard and clay

    brier_sum_only - should it return only the sum of squared prediction errors, or the entire frame?
    (set to true if optimising hyperparamters 'params')
    '''

    k_factor, grass_hard, grass_clay, clay_hard = params

    uniq_players = matches_df['Player 1'].append(matches_df['Player 2']).unique()

    #(1a) Make global ratings DF - unique list of players with starting rating 1200 on every surface

    global RATINGS_DF
    RATINGS_DF = pd.DataFrame(index=uniq_players)
    for surface in ['Grass','Hard','Clay']:
        RATINGS_DF[surface] = 1200

    #(1b) Make global map of rating update ratios
    global SURFACE_MATRIX 
    SURFACE_MATRIX = {}
    SURFACE_MATRIX['Grass']={'Grass':1,'Hard':grass_hard,'Clay':grass_clay}
    SURFACE_MATRIX['Hard']={'Grass':grass_hard,'Hard':1,'Clay':clay_hard}
    SURFACE_MATRIX['Clay']={'Grass':grass_clay,'Hard':clay_hard,'Clay':1}

    matches_df['K Factor'] = k_factor
    
   #(2) Apply update_elos_and_gen_brier to every column (see function for details)

    #Ratings are elos BEFORE game of both players on particular surface
    #E 1 is chance of 1st player winning
    #Brier is squared predition error
    matches_df[['Rating 1','Rating 2','E 1','Brier']] = matches_df[['Player 1','Player 2','K Factor','Outcome','Surface']].apply(update_elos_and_gen_brier,axis=1).apply(pd.Series)
    
    #(3) Return either entier dataframe, or prediciton errors 
    if brier_sum_only:
        #Check correlation factors are greater than zero
        if min(grass_hard,grass_clay,clay_hard) < 0:
            return 1e10 + min(grass_hard,grass_clay,clay_hard)
    
        #Check correlation factors are less than 1
        if max(grass_hard,grass_clay,clay_hard) > 1:
            return 1e10 - max(grass_hard,grass_clay,clay_hard)

        return matches_df['Brier'].sum()
    else:
        return matches_df