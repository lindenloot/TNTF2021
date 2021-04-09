"""
DESCRIPTION:
Generates block loops TNT with no NULL trials, no distractors,
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
    
Fillers are added as follows:
- one negative, one neutral (randomly selected) to the beginning
(order of valence is randomized)
- same for the last two items
- the remaining fillers are randomly distributed across experimental trials
with the following constraints:
    - fillers are never immediately followed by another filler
    - the valence of the fillers counts for the maxrep constraint applied to
        the whole trial list
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

# Get paths to the stimulus lists
src_exp = "TNT_pairs_exp.csv"
src_fillers = "trial list postscan/TNT_pairs_fillers.csv"

for block in ["eval_TNT_prescan", "learning_TNT_prescan", 
                "refresher_TNT_prescan", "refresher_TNT_scanner",
                "TNT_test_postscan", "eval_TNT_postscan"]:
    
    # Get path to folder beloning to the current experimental phase
    # (prescan, scanner, postscan)
    exp_phase = block.split("_")[-1]
    dst = "trial list %s" % (exp_phase)
    
    for pp_ID in range(1, 71):

        main_dm = io.readtxt(src_exp)
        
        # Read in fillers:
        dm = io.readtxt(src_fillers)
        dm_first, dm_last, dm_remaining = helpers.splitFillers(dm)
        
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
        
        # Add exp ID to the dm:
        merged_dm["Exp_ID"] = block
        io.writetxt(merged_dm, os.path.join(dst, "blockloop_%s_PP_%s.csv" \
            % (block, pp_ID)))
