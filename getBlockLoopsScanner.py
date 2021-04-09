"""
DESCRIPTION:

Prepairs trial lists per participant for
part in the scanner.

For applied constraints, see email conversation

CHECK:
- Randomly assigned instead of rotated depending on pp number:
    - T/NT or TBR/TBF) conditions are randomly assigned to object pairs
        (but equally divided amongst NEU and NEG)
    - Same for Set condition (1,2,3 or 4)
    - Condition (T/NT or TBR/TBF) of the filler trials


CHECK:
In TNT:
- T and NT condition equally divided within sets, that is:
    - 3 Think Neu
    - 3 Think Neg
    - 3 No Think Neu
    - 3 No Think Neg
    - 3 NULL
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
        
def addThinkColumn(dm):
    
    """
    Adds a column containing the think condition per pair
    """
    
    # NOTE: when slicing on the basis of selections,
    # a new column has to be created beforehand
    dm["think_condition"] = None
    
    dmNeg = dm["Emotion"] == "neg"
    dmNeu = dm["Emotion"] == "neu"
    
    l_think_conditions = (["NT"] * 12) + (["T"] * 12)
    random.shuffle(l_think_conditions)

    dm["think_condition"][dmNeg] = l_think_conditions
    
    random.shuffle(l_think_conditions)
    dm["think_condition"][dmNeu] = l_think_conditions    
    print(dmNeg.length)
    
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
    exp = dm["exp_ID"][0]

    for row in dm:
        emotion = row["Emotion"]
        if exp == "TNT_scanner":
            col_header = "think_condition"
        elif exp == "IMDF_scanner":
            col_header = "remember_condition"
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
    
    if exp == "TNT_scanner":
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
        
def applyConstraints(dm):
    
    """
    Apply the following constraints:
    maxrep Valence = 3
    maxrep Think Condition = 3
    
    mindist NULL = 2

    It applies the constraints within a mini-run. Next, the main-dm
    is double checks for max number of repetitions. If > 3, we try again

    (This was the only way I could think of checking the main dm while keeping
    the mini-runs grouped)
    """
    
    # Determine exp (TNT or IMDF):
    exp = dm["exp_ID"][0]
    
    while True:
        new_dm = DataMatrix()
        
        for _set in dm["Set_ID"].unique:
            
            set_dm = dm["Set_ID"] == _set
                
            # Shuffle the pairs in the current set:
            set_dm = ops.shuffle(set_dm)
            
            # Create an Enforce object, and add two constraints
            ef = Enforce(set_dm)
            ef.add_constraint(MaxRep, cols=[set_dm.Emotion], maxrep=3)
            if exp == "TNT_scanner":
                ef.add_constraint(MaxRep, cols=[set_dm.think_condition], maxrep=3)
            elif exp == "IMDF_scanner":
                ef.add_constraint(MaxRep, cols=[set_dm.remember_condition], maxrep=3)
            # Apply constraint NULL trials
            ef.add_constraint(MinDist, cols=[set_dm.null_ID], mindist = 2)
        
            # Enforce the constraints
            set_dm = ef.enforce()
            # See the resulting DataFrame and a report of how long the enforcement took.
            
            new_dm = new_dm << set_dm
    
        # Check max number of repetitions:
        max_repetition_emotion = checkReps(new_dm["Emotion"])
        if exp == "TNT_scanner":
            max_repetition_task_condition = checkReps(new_dm["think_condition"])
        elif exp == "IMDF_scanner":
            max_repetition_task_condition = checkReps(new_dm["remember_condition"])
        max_repetition_NULL = checkReps(new_dm["null_ID"])
        print("max emotion: ", max_repetition_emotion)
        print("max think: ", max_repetition_task_condition)
        print("max NULL: ", max_repetition_NULL)
        #sys.exit()
        
        # HACK:
        # If max rep also applies to whole main-run, break from the loop
        if max_repetition_emotion <= 3 and \
                max_repetition_task_condition <= 3 and \
                max_repetition_NULL == 1:
            break
        # Otherise: try again
        else:
            print("reshuffling...")

    return new_dm

def addFillers(exp_dm, filler_dm):
    
    """
    TNT:
    Add 4 fillers to the main dm, two at the beginning and two at the end. Make sure that:
    - One first filler is negative and one first filler is neutral
        - NOTE: no such rule is applied to think and nothink, otherwise it becomes too predictable?
    - The fillers that follow each other at half of the experiment ("thick black line" in C's visual')
        should not be identical
    
    IMDF:
    Just as the experimental pairs, fillers are not repeated
    They are added as follows:
    Run 1: starts and ends with 2 fillers
    Run 2: starts and ends with 2 fillers
    """
    # Determine the exp (TNT or IMDF):
    exp = filler_dm["exp_ID"][0]
    
    # Shuffle the fillers:
    filler_dm = ops.shuffle(filler_dm)
    
    # Randomly assign think or no think:
    if exp == "TNT_scanner":
        list_filler_think_conditions = ["T", "T", "NT", "NT"]
        filler_dm["think_condition"] = list_filler_think_conditions
    
    elif exp == "IMDF_scanner":
        list_filler_remember_conditions = ["TBR", "TBF"] * 4
        filler_dm["remember_condition"] = list_filler_remember_conditions
 
    # Make sure valence is not repeated:
    ef = Enforce(filler_dm)
    ef.add_constraint(MaxRep, cols=[filler_dm.Emotion], maxrep=1)
    filler_dm = ef.enforce()
    
    # Some ugly HACKS to add the fillers at the correct positions:
    # For the TNT part, remember that the trial list is split into 2 halfs
    # and that fillers are repeated
    if exp == "TNT_scanner":
        # Seperate the first two and the last two fillers in separate dms
        fillers_start = filler_dm[0:2]
        fillers_end = filler_dm[2:]
        
        # Filler 1 and 2 + main dm
        merged_dm = fillers_start << exp_dm
        # Main dm + filler 3 and 4
        merged_dm = merged_dm << fillers_end
    
    # For the IMDF part, remember that we generate one big trial list
    # so 4 fillers have to be added halfway
    # Divide the experimental dm in two halfs by using set_ID
    # to split on (this works because set_ID is not shuffled)
    if exp == "IMDF_scanner":
        # NOTE that split() returns a tuple containing (value, split dm)
        (_set1, dm_run1), (_set2, dm_run2) = ops.split(exp_dm["Set_ID"])
        
        fillers_start = filler_dm[0:2]
        fillers_middle = filler_dm[2:6]
        fillers_end = filler_dm[6:]
        
        # Do the merging:
        
        merged_dm = fillers_start << dm_run1
        merged_dm = merged_dm << fillers_middle
        merged_dm = merged_dm << dm_run2
        merged_dm = merged_dm << fillers_end
    
    return merged_dm
    
def getMainDm(exp):
    
    """
    Arguments:
    exp        --- string indicating whether we are preparing the
                    TNT or the IMDF block loops
                    
    TNT:
    Creates a dm for a given main run, i.e., a list containing of 64 trials:
        - 12 Neu Think
        - 12 Neg Think
        - 12 Neu No Think
        - 12 Neg No Think
        - 12 NULL
        - 4 fillers
    With the necessary constraints applied

    IMDF:
    Creates a dm for two main runs, i.e. a list containign all 158 trials
    (120 experimental, 30 NULL, 8 fillers)

    """
    
    src_path = "trial list scanner/%s_pairs_exp.csv" % exp
    filler_path = "trial list scanner/%s_pairs_fillers.csv" % exp
    
    
    # Read in the csv file containing exp pairs:
    main_dm = io.readtxt(src_path)
    
    # Determine the current experiment:
    exp = main_dm["exp_ID"][0]
    
    # Shuffle the main dm:
    main_dm = ops.shuffle(main_dm)


    # Add columns:
    main_dm = addValenceColumn(main_dm)
    
    if exp == "TNT_scanner":
        main_dm = addThinkColumn(main_dm)
    
    if exp == "IMDF_scanner":
        main_dm = addRememberColumn(main_dm)

    main_dm = addConditionColumn(main_dm)
    main_dm = addSetColumn(main_dm)
    
    # Apply constraints:
    main_dm = applyConstraints(main_dm)

    # Add fillers:
    filler_dm = io.readtxt(filler_path)
    main_dm = addFillers(main_dm, filler_dm)
    
    # Add the Boxcolor variable:
    main_dm = addColorColumn(main_dm)
    
    return main_dm

def getDmsImdf():
    
    """
    Prepares IMDF block loops for 70 participants
    """
    
    
    dst_folder = "trial list scanner/block loops IMDF scanner"

    
    for pp in range(1, 71):
    
        pp_dm = getMainDm(exp="IMDF")
        pp_dm["pp_ID"] = pp
        pp_dm["trial_count"] = range(1, pp_dm.length + 1)
        
        file_name = "IMDF_scanning_PP%s.csv" % (pp)
        io.writetxt(pp_dm, os.path.join(dst_folder, file_name))

def getDmsTnt():


    dst_folder = "trial list scanner/block loops TNT scanner"

    for pp in range(1, 71):
        
        while True:
        
            pp_dm = DataMatrix()
        
            for repetition in ["one", "two"]:
                
                main_dm = getMainDm(exp="TNT")
                main_dm["repetition"] = repetition
                
                pp_dm = pp_dm << main_dm
                
            pp_dm["pp_ID"] = pp
            pp_dm["trial_count"] = range(1, pp_dm.length + 1)
            
            # HACK: an extremely ugly hack to make sure that the two
            # fillers in the middle of the experiment are not the same:
            
            # Determine the filler at the end of main run 1:
            last_filler_run1 = pp_dm["Scene"][pp_dm["trial_count"] == 64][0]
            
            # Determine the filler at the end of main run 1:
            first_filler_run2 = pp_dm["Scene"][pp_dm["trial_count"] == 65][0]
    
        
            # If they are not repeated: break from the loop
            if last_filler_run1 != first_filler_run2:
                break
            else:
                print("Filler occurs twice in a row. Let's try again...")
        
        file_name = "TNT_scanning_PP%s.csv" % pp
        io.writetxt(pp_dm, os.path.join(dst_folder, file_name))



if __name__ == "__main__":
    
    getDmsImdf()
    #getDmsTnt()
