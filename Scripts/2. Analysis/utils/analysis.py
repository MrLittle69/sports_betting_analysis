from sklearn.metrics import roc_curve, auc, log_loss
from matplotlib import pyplot as plt
from IPython import embed

def plot_roc_curve(outcome,prediction):
    # Compute ROC curve and ROC area for each class
    fpr, tpr, _ = roc_curve(outcome, prediction)
    roc_auc = auc(fpr, tpr)
    lw = 2
    plt.plot(fpr, tpr, color='darkorange',
    lw=lw, label='ROC curve (area = %0.2f)' % roc_auc)
    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.show()

def flip_underdog_wins(row):
    prediction,player_1,player_2,outcome = row
    assert int(outcome) in [0,1] and prediction >= 0 and prediction <= 1
    if (prediction > 0.5 and int(outcome) == 1) or (prediction <= 0.5 and int(outcome) == 0):
        return prediction,player_1,player_2,1
    else:
        return 1.0-prediction,player_2,player_1,0


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