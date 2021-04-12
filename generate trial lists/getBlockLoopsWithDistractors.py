"""
DESCRIPTION:

TNT:

Creates block loops for test feedback and criterion test.
I applied the following constraints:
- None of the distractors should be identical to the target, 
    nor to each other. In other words, three distinct scenes should be shown.
- Each scene should occur exactly once as target, once as distractor 1, 
    and once as distractor 2
 - The distractors are pulled from the same category as the target
- And, because there was confusion about it, I implemented it anyway:
    The valence category is not repeated more than 3 times in a row
- 12 fillers are added to the list. They are divided randomly across 
    the experimental trials, with the constraint that two (or more) fillers 
    should not occur in a row
- Except from the very first and last two trials; they are always fillers

Two new trial list (one for test feedback and one forrcriterion test are 
generated for each participant (for now 70) and saved as csv files. 
The csv file is read in in OpenSesame, depending on the subject number
and the block, in the items called testfeedback_blockloop and 
criteriontest_blockloop respectively.

NOTE:
The match of target and distractors is held constant between test feedback 
and criterion test, because that is what I understood from the description.
If distractors should be reshuffled, let me know.

IMDF:
As above, except that only one list per participant is generated. 
The csv files are read in in OpenSesame, depending on the subject number
in the item called IMDF_recall_blockloop.

NOTE that valence of the associated scene is taken into account, such that the
two distractor objects are from the same associated valence as the target object.
If the target scene (to which the object should be linked) is negative, the two
distractor objects are also objects that are associated with (another) negative scene.
This was to keep things similar to the TNT MC task

"""

# Python modules:
import random
import os
from pseudorandom import Enforce, MaxRep, MinDist
import sys

# Datamatrix modules:
from datamatrix import io
from datamatrix import operations as ops
from datamatrix import DataMatrix

# Import own modules:
import addDistractors
import helpers

dst_folder = "trial list prescan"
src_folder = "."

def applyConstraints(dm_exp, dm_fillers):
    

    """
    Arguments:
    dm_exp        --- dm containing exp scene-object combinations
    dm_fillers    --- dm containing filler scene-object combinations
    
    Returns:
    final_dm_test_feedback        --- final datamatrix for the test feedback blockloop
    final_dm_criterion_test        --- final datamatrix for the test feedback blockloop
    """
    
    
    # Add distractors:
    dm_exp = addDistractors.addDistractors(dm_exp)
    #print(dm_exp)
    #sys.exit()
    dm_fillers = addDistractors.addDistractors(dm_fillers)
    
    #print(dm_exp["Exp_ID"])
    #sys.exit()

    
    # Make sure we will collect two dms
    list_dms = []
    
    # A little HACK because TNT requires two block loops, whereas
    # IMDF requires only one

    if dm_exp["Exp_ID"][0] == "TNT_memory_prescan":
        block_list = ["test_feedback", "criterion_test"]
    elif dm_exp["Exp_ID"][0] == "IMDF_memory_postscan":
        block_list = ["memory_test_IMDF"]
    else:
        raise Exception("Unknown exp ID: %s" % dm_exp["Exp_ID"][0])
    
    for block in block_list:
    
        # Shuffle the fillers:
        dm_fillers = ops.shuffle(dm_fillers)
        
        # Slice filler dm (for constraints see helpers.py)
        dm_first, dm_last, dm_middle = helpers.splitFillers(dm_fillers)
        
        # Merge middle fillers to the main dm:
        main_dm = dm_exp << dm_middle
        
        # Shuffle the main dm:
        main_dm = ops.shuffle(main_dm)
        
        # Create an Enforce object, and add two constraints
        ef = Enforce(main_dm)
        ef.add_constraint(MaxRep, cols=[main_dm.Emotion], maxrep=3)
        ef.add_constraint(MinDist, cols=[main_dm.Trial_ID], mindist=2)
        
        # Enforce the constraints
        main_dm = ef.enforce()
        
        # Add two fillers to the beginning of the final dm:
        final_dm = dm_first << main_dm
        
        # And to the end fo the final dm:
        final_dm = final_dm << dm_last
        
        # Append to the dm list:
        list_dms.append(final_dm)
    
    # Another little HACK because TNT requires 2 block loops
    if len(list_dms) > 1:
        # Unpack the list so we can return two separate dms
        dm1, dm2 = list_dms
        return dm1, dm2
    # Whereas IMDF requires only one:
    else:
        return list_dms[0]


def getBlockLoopsMemoryPrescan():

    
    """
    Prepares TNT test feedback and criterion test
    """
    

    exp = "TNT_memory_prescan"
    phase = exp.split("_")[-1]
    task = exp.split("_")[0]
    
    src_path = "."
    dst_path = "trial list %s" % phase
    
    # Read dm containing experimental pairs (without distractors)
    dm_exp = io.readtxt(os.path.join(src_path, '%s_pairs_exp.csv' % task))
    dm_exp["Exp_ID"] = exp
    
    # Read dm containing fillers (without distractors)
    dm_fillers = io.readtxt(os.path.join(src_path, '%s_pairs_fillers.csv' % task))
    dm_fillers["Exp_ID"] = exp
    
    for subject_ID in range(1, 71):
        
        dm1, dm2 = applyConstraints(dm_exp, dm_fillers)
        io.writetxt(dm1, os.path.join(dst_path, "block_loop_test_feedback_PP_%s.csv" % subject_ID))
        io.writetxt(dm2, os.path.join(dst_path, "block_loop_criterion_test_PP_%s.csv" % subject_ID))
        
def getBlockLoopsMemoryPostScan():
        
    """
    Prepares IMDF post scan memory task
    
    NOTE: here the distractors are objects
    """
        
    exp = "IMDF_memory_postscan"
    phase = exp.split("_")[-1]
    task = exp.split("_")[0]
    
    src_path = "."
    dst_path = "trial list %s" % phase
    
    # Read dm containing experimental pairs (without distractors)
    dm_exp = io.readtxt(os.path.join(src_path, '%s_pairs_exp.csv' % task))
    dm_exp["Exp_ID"] = exp
    
    # Read dm containing fillers (without distractors)
    dm_fillers = io.readtxt(os.path.join(src_path, '%s_pairs_fillers.csv' % task))
    dm_fillers["Exp_ID"] = exp
    
    # Add column header Emotion:
    dm_exp = helpers.addValenceColumn(dm_exp)
    dm_fillers = helpers.addValenceColumn(dm_fillers)
    
    for subject_ID in range(1, 71):
        
        pp_dm = applyConstraints(dm_exp, dm_fillers)
        io.writetxt(pp_dm, os.path.join(dst_path, "block_loop_IMDF_postscan_PP_%s.csv" % subject_ID))
        
if __name__ == "__main__":
    
    getBlockLoopsMemoryPrescan()
    getBlockLoopsMemoryPostScan()
