from datamatrix import io
from datamatrix import operations as ops
from datamatrix import DataMatrix
import random

import sys


def combine(dm, l_neg_dist1,l_neg_dist2 ,l_neu_dist1 ,l_neu_dist2):
    
    """
    Make a potential combination of distractors
    
    Arguments:
    dm                --- a DataMatrix instance
    l_neg_dist1       --- list of potential first negative distractors
    l_neg_dist2
    l_neg_dist1
    l_neu_dist2
    
    Returns:
    new_dm_exp
    """
    
    # Create an empty data file which will eventually contain all experimental trial info
    new_dm_exp = DataMatrix()

    # Walk through the rows of the experimental dm
    for row in dm:
        
        # Retrieve trial info:
        target_scene = row.Scene
        target_emotion = row.Emotion
        trial_id = row.Trial_ID
        target_object = row.Object
        exp_id = row.Exp_ID
        
        print("valence = ", target_emotion)
        #sys.exit()
        # Create an empty mini dm:
        trial_dm = DataMatrix(1)

        # Randomly select two possible distractors (from the same category as the target scene)
        if target_emotion == "neg":
            dist1 = random.choice(l_neg_dist1)
            dist2 = random.choice(l_neg_dist2)
            l_neg_dist1.remove(dist1)
            l_neg_dist2.remove(dist2)
            
        elif target_emotion == "neu":
            dist1 = random.choice(l_neu_dist1)
            dist2 = random.choice(l_neu_dist2)
            l_neu_dist1.remove(dist1)
            l_neu_dist2.remove(dist2)
        else:
            raise Exception("Unknown valence category")
    
        # Add info to the trial_dm:
        trial_dm["distractor_1"] = dist1
        trial_dm["distractor_2"] = dist2
        trial_dm["Scene"] = target_scene
        trial_dm["Emotion"] = target_emotion
        trial_dm["Trial_ID"] = trial_id
        trial_dm["Object"] = target_object
        trial_dm["Exp_ID"] = exp_id
        
        # Merge the current trial to the big dm:
        new_dm_exp = new_dm_exp << trial_dm
    
    # After having looped through all rows, return the full dm:
    return new_dm_exp


def addDistractors(dm):
    
    """
    Adds distractors to a given datamatrix, making sure that both
    distractors are different from the target and from each other

    Arguments:
    dm        --- a DataMatrix() instance without distractors

    Returns:
    new_dm        --- a DataMatrix instance with distractors
    """
    
    exp_ID = dm["Exp_ID"][0]
    
    if exp_ID == "TNT_memory_prescan":
        target_type = "Scene"
    elif exp_ID == "IMDF_memory_postscan":
        target_type = "Object"
    else:
        raise Exception("Unknown exp ID: %s" % exp_ID)
        
    # Shuffle the dm:
    dm = ops.shuffle(dm)
    
    # Split the original dm by emotion:
    neg_dm = dm.Emotion == "neg"
    neu_dm = dm.Emotion == "neu"
    
    # Make a list of potential scenes for negative distractor 1
    L_NEG_DIST1 = list(neg_dm[target_type])
    # and negative distractor 2
    L_NEG_DIST2 = list(neg_dm[target_type])
    
    # Make a list of potential scenes for neutral distractor 1
    L_NEU_DIST1 = list(neu_dm[target_type])
    # and 2
    L_NEU_DIST2 = list(neu_dm[target_type])

    new_dm = combine(dm, L_NEG_DIST1[:], L_NEG_DIST2[:], L_NEU_DIST1[:], L_NEU_DIST2[:])

    # Make sure target, distractor 1 and distractor 2 are different scenes:
    while any(
        row["distractor_1"] == row["distractor_2"] or
        row["distractor_1"] == row[target_type] or
        row["distractor_2"] == row[target_type]
        for row in new_dm
        ):
        # If not, try again:
         print("try again")
         new_dm = combine(dm, L_NEG_DIST1[:], L_NEG_DIST2[:], L_NEU_DIST1[:], L_NEU_DIST2[:])
    
    
    return new_dm


if __name__ == "__main__":
    
    exp = "TNT memorytest prescan"
    
    # Read dm containing stimuli without distractors:
    dm_exp = io.readtxt('TNT_pairs_exp.csv')
    dm_exp["Exp_ID"] = exp
    dm_new = addDistractors(dm_exp)
    io.writetxt(dm_new, "test-distractors.csv")
