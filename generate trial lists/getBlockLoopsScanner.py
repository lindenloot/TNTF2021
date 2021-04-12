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

import helpers

def applyConstraints(dm):
    
    """
    Apply the following constraints:
    maxrep Valence = 3
    maxrep Think Condition = 3
    
    mindist NULL = 2

    It applies the constraints within a mini-run. Next, the main-dm
    is double checks for max number of repetitions. If > 3, we try again

    (This was the only way I could think of to check the main dm while keeping
    the mini-runs grouped)
    """
    
    # Determine exp (TNT or IMDF):
    exp = dm["Exp_ID"][0]
    
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
        max_repetition_emotion = helpers.checkReps(new_dm["Emotion"])
        if exp == "TNT_scanner":
            max_repetition_task_condition = helpers.checkReps(new_dm["think_condition"])
        elif exp == "IMDF_scanner":
            max_repetition_task_condition = helpers.checkReps(new_dm["remember_condition"])
        max_repetition_NULL = helpers.checkReps(new_dm["null_ID"])
        print("max emotion: ", max_repetition_emotion)
        print("max think: ", max_repetition_task_condition)
        print("max NULL: ", max_repetition_NULL)

        
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
    
    TODO
    
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
    exp = filler_dm["Exp_ID"][0]

    # Shuffle the fillers:
    filler_dm = ops.shuffle(filler_dm)
    
    # Randomly assign think or no think:
    if "TNT" in exp:
        list_filler_think_conditions = ["T", "T", "NT", "NT"]
        filler_dm["think_condition"] = list_filler_think_conditions
        #print(filler_dm)
        #sys.exit()
    
    elif "IMDF" in exp:
        list_filler_remember_conditions = ["TBR", "TBF"] * 4
        filler_dm["remember_condition"] = list_filler_remember_conditions
    
    else:
        raise Exception("Unknown exp type: %s" % exp)
    
    # re-set condition value to "filler"
    filler_dm["condition"] = "FILLER"
    
    # Make sure valence is not repeated:
    ef = Enforce(filler_dm)
    ef.add_constraint(MaxRep, cols=[filler_dm.Emotion], maxrep=1)
    filler_dm = ef.enforce()
    
    # Determine the first, the last, and the middle (if any) fillers:
    # NOTE: for the TNT part, the middle dm should be empty
    # because there are only fillers at the beginning and end of the
    # main runs:
    dm_first, dm_last, dm_middle = helpers.splitFillers(filler_dm)

    
    # For the TNT part, remember that the trial list is split into 2 halfs
    # and that fillers are repeated
    
    if exp == "TNT_scanner":

        # Seperate the first two and the last two fillers in separate dms
        
        # Filler 1 and 2 + main dm
        merged_dm = dm_first << exp_dm
        # Main dm + filler 3 and 4
        merged_dm = merged_dm << dm_last
    
    # For the IMDF part, rwe generate one big trial list with 2 fillers
    # at the begining, 2 at the end and four in the middle (halfway):
    # Divide the experimental dm in two halfs by using set_ID
    # to split on (this works because set_ID is not shuffled)
    elif exp == "IMDF_scanner":
        # NOTE that split() returns a tuple containing (value, split dm)
        (_set1, dm_run1), (_set2, dm_run2) = ops.split(exp_dm["Set_ID"])
        
        # Do the merging:
        merged_dm = dm_first << dm_run1
        merged_dm = merged_dm << dm_middle
        merged_dm = merged_dm << dm_run2
        merged_dm = merged_dm << dm_last
    
    
    else:
        raise Exception("Unknown exp type: %s" % exp)
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
    
    # NOTE that the input trial lists are different from the ones
    # that are used in the pre-scanner part, because:
    # - filler lists are different
    # - for TNT, not all pairs are shown in the scanner
    # - NULL trials are added
    src_path = "%s_scanner_pairs_exp.csv" % exp
    filler_path = "%s_scanner_pairs_fillers.csv" % exp
    
    
    # Read in the csv file containing exp pairs and the filler pairs:
    main_dm = io.readtxt(src_path)
    filler_dm = io.readtxt(filler_path)

    main_dm["Exp_ID"] = "%s_scanner" % exp
    filler_dm["Exp_ID"] = "%s_scanner" % exp
    
    # Shuffle dms:
    main_dm = ops.shuffle(main_dm)
    filler_dm = ops.shuffle(filler_dm)
    
    # Add columns:
    main_dm = helpers.addValenceColumn(main_dm)
    #filler_dm = helpers.addValenceColumn(filler_dm)

    if exp == "TNT":
        main_dm = helpers.addThinkColumn(main_dm)
        #filler_dm = helpers.addThinkColumn(filler_dm)
    
    if exp == "IMDF":
        main_dm = helpers.addRememberColumn(main_dm)
        #filler_dm = helpers.addRememberColumn(filler_dm)
    
    #print(main_dm.column_names)
    #sys.exit()
    
    main_dm = helpers.addConditionColumn(main_dm)
    #filler_dm = helpers.addConditionColumn(filler_dm)

    main_dm = helpers.addSetColumn(main_dm)
    
    # Apply constraints:
    main_dm = applyConstraints(main_dm)
    main_dm = addFillers(main_dm, filler_dm)
    
    # Add the Boxcolor variable:
    main_dm = helpers.addColorColumn(main_dm)
    
    return main_dm

def getDmsImdf():
    
    """
    Prepares IMDF block loops for 70 participants
    """
    
    
    dst_folder = "trial list scanner"

    
    for pp in range(1, 71):
    
        pp_dm = getMainDm(exp="IMDF")
        pp_dm["pp_ID"] = pp
        pp_dm["trial_count"] = range(1, pp_dm.length + 1)
        
        file_name = "IMDF_scanning_PP%s.csv" % (pp)
        io.writetxt(pp_dm, os.path.join(dst_folder, file_name))


def getDmsTnt():


    dst_folder = "trial list scanner"

    for pp in range(1, 71):
        
        while True:
        
            pp_dm = DataMatrix()
            
            for main_run in ["first", "second"]:
            
                for repetition in ["one", "two"]:
                    
                    main_dm = getMainDm(exp="TNT")
                    main_dm["repetition"] = repetition
                    main_dm["main_run"] = main_run
                    pp_dm = pp_dm << main_dm
            
            print(pp_dm.length)
            pp_dm["pp_ID"] = pp
            pp_dm["trial_count"] = range(1, pp_dm.length + 1)
            
            # HACK: an extremely ugly hack to make sure that the two
            # fillers never repeat, not even when two runs are merged:
            
            # Determine the filler at the end of repetition 1 main run 1:
            filler_index_64 = pp_dm["Scene"][pp_dm["trial_count"] == 64][0]
            
            # Determine the filler at the beginning of repetition 2 main run 2:
            filler_index_65 = pp_dm["Scene"][pp_dm["trial_count"] == 65][0]
            
            # Etc. for the other 2 "transitions":
            filler_index_128 = pp_dm["Scene"][pp_dm["trial_count"] == 128][0]
            filler_index_129 = pp_dm["Scene"][pp_dm["trial_count"] == 129][0]
            
            filler_index_192 = pp_dm["Scene"][pp_dm["trial_count"] == 192][0]
            filler_index_193 = pp_dm["Scene"][pp_dm["trial_count"] == 193][0]

            # filler_index_256 = pp_dm["Scene"][pp_dm["trial_count"] == 256][0]
            # filler_index_257 = pp_dm["Scene"][pp_dm["trial_count"] == 257][0]

            # If they are not repeated: break from the loop
            if filler_index_64 != filler_index_65 and \
                filler_index_128 != filler_index_129 and \
                filler_index_192 != filler_index_193:
#                filler_index_256 != filler_index_257:
                break
            else:
                print("Filler occurs twice in a row. Let's try again...")
        
        file_name = "TNT_scanning_PP%s.csv" % pp

        io.writetxt(pp_dm, os.path.join(dst_folder, file_name))


if __name__ == "__main__":
    
    getDmsImdf()
    getDmsTnt()
