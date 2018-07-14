# -*- coding: utf-8 -*-
"""
Created on Sat Apr 28 19:30:25 2018

@author: oliver.cairns
"""
#1. Simple ELO analysis on match winner
#calculate the winning chances of a player vs oppoent, for a given ratings dataframe. 
def calc_winning_chances(ratings_dict, first_player,second_player):
	#implimented from formula for elo: e1 = 10^(r1/400)/[10^(r1/400) + 10^(r2/400)]
	rating_1 =  ratings_dict[first_player]['current_rating']/400
	rating_2 =  ratings_dict[second_player]['current_rating']/400
	q1 = 10.0 ** rating_1
	q2 = 10.0 ** rating_2
	return q1/(q1+q2)

def get_ratings(first_player,second_player,ratings_dict):
     rating_1 = ratings_dict[first_player]['current_rating']
     rating_2 = ratings_dict[second_player]['current_rating'] 
     return [rating_1,rating_2]
#updates the global ratings_dict, given a single game + k-factor
def update_elos_and_winning_chances(game,game_index,ratings_dict,k_factor,elo_df,ratings_dummy):
    first_player=game['Player 1']
    second_player=game['Player 2']
    outcome=game['Outcome']
    
    #calculate chance of first player winning game (can be reused with other ratings algorithms
    e1 = calc_winning_chances(ratings_dict,first_player,second_player)
    
    #update historic rankings - allows you to plot ELO charts
    if ratings_dummy:       
        e2 = 1.0 - e1
        date = game['Date']
        
        rating_1, rating_2 = get_ratings(first_player,second_player,ratings_dict)
        ratings_dict[first_player]['historic_ratings'].append(rating_1)
        ratings_dict[second_player]['historic_ratings'].append(rating_2)
        ratings_dict[first_player]['historic_predictions'].append(e1)
        ratings_dict[second_player]['historic_predictions'].append(e2)
        ratings_dict[first_player]['historic_dates'].append(date)
        ratings_dict[second_player]['historic_dates'].append(date)
    
        elo_df.loc[game_index,'Elo 1'] = ratings_dict[first_player]['current_rating']
        elo_df.loc[game_index,'Elo 2'] = ratings_dict[second_player]['current_rating']
        elo_df.loc[game_index,'e1'] = e1
    
    #measure performance of prediction vs actual win/loss draw. Brier change = square of prediction error.    
    e1_diff = outcome - e1 
    
    ratings_dict[first_player]['current_rating'] += e1_diff*k_factor
    ratings_dict[second_player]['current_rating'] -= e1_diff*k_factor
        
    return e1_diff**2

def calc_brier_and_elos(elo_df,k_factor,ratings_dummy):
    if ratings_dummy:
        elo_df['Elo 1'] = 0
        elo_df['Elo 2'] = 0
        elo_df['e1'] = 0
    
    
    unique_players = set(elo_df['Player 1']).union(set(elo_df['Player 2']))
    
    ratings_dict = {}
    for player in unique_players:
        ratings_dict[player]={'current_rating':1200.0,'historic_ratings':[],'historic_predictions':[], 'historic_dates':[]}
            
    current_brier = 0
        
    for i, game in elo_df.iterrows():
        current_brier += update_elos_and_winning_chances(game=game,game_index = i, ratings_dict = ratings_dict, k_factor=k_factor, elo_df = elo_df,ratings_dummy = ratings_dummy)

    if ratings_dummy:
        return current_brier,elo_df, ratings_dict
    else:
        return current_brier

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
