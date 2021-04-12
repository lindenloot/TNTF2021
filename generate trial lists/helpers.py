"""
DESCRIPTION:
Generates block loops TNT with nu NULL trials, no distractors,
as is the case in:

- Prescan:
    - Evaluation
    - Learning block loop
    - Refresher
- Scanner:
    - Refresher
- Postscan:
    - TNT verbal response
    - Evaluation 2
"""

# Python modules:
import random
import os
from pseudorandom import Enforce, MaxRep, MinDist
from itertools import groupby
import sys


# Datamatrix modules:
from datamatrix import io
from datamatrix import operations as ops
from datamatrix import DataMatrix


def splitFillers(dm):
    
    """
    Splits filler trials into:
    - 2 first fillers, one negative, one neutral
    - 2 last fillers, one negative, one neutral
    - remaining fillers, that should be mixed with the experimental trials
    
    Arguments:
    dm        --- DataMatrix containing filler objects
    
    Returns:
    dm_first    --- dm containing only 2 rows, corresponding to the first 2 fillers
    dm_last     --- dm containing only 2 rows, corresponding to the last 2 fillers
    dm_remaining    --- dm containing the remainder (if any) of the fillers
    
    NOTE the order
    """

    # Below is an awful piece of script to make sure the first and last two fillers
    # consist of one neg and one neu trial.
    # I just don't see a way to do this more elegantly
    
    # Shuffle the fillers:
    dm= ops.shuffle(dm)
    
    # Split the fillers on the basis of valence:
    (cat1, filler_dm_negative), (cat2, filler_dm_neutral) = ops.split(dm["Emotion"])
    
    # Select 2 fillers, one from each valence category, as first 2 fillers:
    identifier_filler1_neg = filler_dm_negative["Object"][0]
    identifier_filler1_neu = filler_dm_neutral["Object"][0]
    
    dm_filler1_neg = filler_dm_negative["Object"] == identifier_filler1_neg
    dm_filler1_neu = filler_dm_neutral["Object"] == identifier_filler1_neu
    
    # Merge the two first trial_dms
    dm_first = dm_filler1_neg << dm_filler1_neu
    # Shuffle
    dm_first = ops.shuffle(dm_first)
    # Add a column indicating the type of filler (for later debugging/cross
    # checking)
    dm_first["filler_type"] = "first"
    
    # Remove the already selected pairs from the dms
    # (i.e., select WITHOUT replacement):
    filler_dm_negative = filler_dm_negative[1:]
    filler_dm_neutral = filler_dm_neutral[1:]
    
    # Do the same thing for the last 2 fillers:
    # Select 2 fillers, one from each valence category, as first 2 fillers:
    identifier_filler2_neg = filler_dm_negative["Object"][0]
    identifier_filler2_neu = filler_dm_neutral["Object"][0]
    
    dm_filler2_neg = filler_dm_negative["Object"] == identifier_filler2_neg
    dm_filler2_neu = filler_dm_neutral["Object"] == identifier_filler2_neu
    # Merge:
    dm_last = dm_filler2_neg << dm_filler2_neu
    # And shuffle:
    dm_last = ops.shuffle(dm_last)
    # Add column with filler type
    dm_last["filler_type"] = "last"
    
    # Remove from the dms:
    filler_dm_negative = filler_dm_negative[1:]
    filler_dm_neutral = filler_dm_neutral[1:]
    
    # Merge the remaining filler dms:
    dm_remaining = filler_dm_negative << filler_dm_neutral
    # Shuffle:
    dm_remaining = ops.shuffle(dm_remaining)
    # Add column with filler type
    dm_remaining["filler_type"] = "middle"

    
    
    return dm_first, dm_last, dm_remaining
    

def checkReps(l):

    """
    Checks the max number of repetitions in a given list
    
    Returns the maximum number of consecutive repetitions
    """
    
    count_dups = [sum(1 for _ in group) for _, group in groupby(l)]

    return max(count_dups)

def addValenceColumn(dm):
    
    """
    Add a column with the column name "Emotion", which has
    the value "neg" or "neu".
    
    The current valence is read from the column "condition"
    """

    # NOTE: when assigning column values by iterating over rows,
    # the new column does NOT have to be created beforehand

    for row in dm:
        
        # Get current condition:
        condition = row["condition"]
        
        if condition != "NULL":
            
            # Deduce current valence:
            emotion = condition[-3:]

        else:
            emotion = None
        
        
        # Add emotion to a new column called "emotion"
        row["Emotion"] = emotion
        
    return dm
        
def addThinkColumn(dm, nTrialsPerLevel=12):
    
    """
    Adds a column containing the think condition per pair
    
    Arguments:
    dm
    nTrialsPerCondition        --- default = 12
    """
    
    # NOTE: when slicing on the basis of selections,
    # a new column has to be created beforehand
    dm["think_condition"] = None
    
    
    dmNeg = dm["Emotion"] == "neg"
    dmNeu = dm["Emotion"] == "neu"
    
    l_think_conditions = (["NT"] * \
        nTrialsPerLevel) + (["T"] * nTrialsPerLevel)

    # Assign to the neg trials, after shuffling    
    random.shuffle(l_think_conditions)
    dm["think_condition"][dmNeg] = l_think_conditions
    
    # Assign to the neg trials, after re-shuffling    
    random.shuffle(l_think_conditions)
    dm["think_condition"][dmNeu] = l_think_conditions    

    return dm

def addRememberColumn(dm):
    
    """
    Adds a column containing the forgetting condition 
    (TBF or TBR) per pair
    """
    
    # NOTE: when slicing on the basis of selections,
    # a new column has to be created beforehand
    dm["remember_condition"] = None
    
    dmNeg = dm["Emotion"] == "neg"
    dmNeu = dm["Emotion"] == "neu"
    
    l_remember_conditions = (["TBR"] * 30) + (["TBF"] * 30)
    random.shuffle(l_remember_conditions)

    dm["remember_condition"][dmNeg] = l_remember_conditions
    
    random.shuffle(l_remember_conditions)
    dm["remember_condition"][dmNeu] = l_remember_conditions    
    print(dmNeg.length)
    
    return dm


def addConditionColumn(dm):
    
    """
    Add a column indicating the current condition
    (i.e. the combination of Valence and Think Condition)

    This replaces the old column called "condition"
    """
    
    # Determine the exp (TNT or IMDF)
    exp = dm["Exp_ID"][0]
    
    for row in dm:
        emotion = row["Emotion"]
        if "TNT" in exp:
            col_header = "think_condition"
        elif "IMDF" in exp:
            col_header = "remember_condition"
        else:
            raise Exception("Unknown exp: %s" % exp)
        task_condition = row[col_header]
        old_condition = row["condition"]
        
        if old_condition == "NULL":
            current_condition = "NULL"
        else:
            current_condition = "%s_%s" % (task_condition, emotion)
        row["condition"] = current_condition
        
    return dm

def addColorColumn(dm):
    
    """
    Add a column containing the variable Boxcolor.
    Think = green
    NoThink = red

    Returns:
    dm        --- The dm with the new column
    """
    
    # Create new column:
    dm["color"] = None
    
    # Determine exp:
    exp = dm["exp_ID"][0]
    
    if "TNT" in exp:
        dm_think = dm["think_condition"] == "T"
        dm_nothink = dm["think_condition"] == "NT"
        
        dm["color"][dm_think] = "green"
        dm["color"][dm_nothink] = "red"
    
    if exp == "IMDF_scanner":
        dm_TBR = dm["remember_condition"] == "TBR"
        dm_TBF = dm["remember_condition"] == "TBF"
        
        dm["color"][dm_TBR] = "green"
        dm["color"][dm_TBF] = "red"
        
    
    return dm
    
    
def addSetColumn(dm):
    
    """
    Add a column indicating to which set (1,2,3 or 4) a pair belongs
    """
    
    # Determine current experiment (TNT or IMDF)
    exp = dm["exp_ID"][0]
    
    # In TNT, we have 2 main runs. Each main run is divided into 4
    # sets containing 3 trials of each condition.
    # This was necessary to make sure that the first 16 pairs in Run 1
    # would also be the first 16 pairs (although in different order)
    # in Run 2, etc.
    if exp == "TNT_scanner":
        list_set_IDs = [1, 2, 3, 4] * 3
    
    # CHECK: Is this reasoning correct?
    # It means that we have 15 trials of each condition
    # (NegTBF, NegTBR, NeuTBF, NeuTBR, NULL) per main run
    if exp == "IMDF_scanner":
        list_set_IDs = [1,2] * 15
    
    dm["Set_ID"] = None
    
    # Make sure each set contains the same number of
    # conditions
    for condition in dm["condition"].unique:
        
        # (Re-)shuffle:
        random.shuffle(list_set_IDs)
        
        # Select all trials from a given condition
        cond_dm = dm["condition"] == condition
        
        
        # And randomly assign a set ID
        dm["Set_ID"][cond_dm] = list_set_IDs
    
    return dm


if __name__ == "__main__":
    
        
    src_exp = "trial list postscan/TNT_pairs_exp.csv"
    src_fillers = "trial list postscan/TNT_pairs_fillers.csv"
    dst = "trial lists postscan/block loops TNT postscan"
    
    main_dm = io.readtxt(src_exp)
    
    # Read in fillers:
    dm = io.readtxt(src_fillers)
    dm_first, dm_last, dm_remaining = splitFillers(dm)
    
    # Merge the remaining fillers with the main dm:
    merged_dm = main_dm << dm_remaining
    
    # Shuffle the merged dm:
    merged_dm = ops.shuffle(merged_dm)
    
    # Create an Enforce object, and add constraint
    ef = Enforce(merged_dm)
    ef.add_constraint(MaxRep, cols=[merged_dm.Emotion], maxrep=3)
    ef.add_constraint(MinDist, cols=[merged_dm.Trial_ID], mindist=2)
    
    # Enforce the constraints
    merged_dm = ef.enforce()
    
    # Add the first fillers:
    merged_dm = dm_first << merged_dm
    # Add the last fillers:
    merged_dm = merged_dm << dm_last

    io.writetxt(merged_dm, "FINAL.csv")
