"""
DESCRIPTION:
Creates block loops for the MC IMDF memory test in post scan session.
As for the TNT prescan session, we applied the following constraints:
- None of the distractors should be identical to the target, 
    nor to each other. In other words, three distinct scenes should be shown.
- Each scene should occur exactly once as target, once as distractor 1, 
    and once as distractor 2
 - The distractors are pulled from the same category as the target
- And, because there was confusion about it, I implemented it anyway:
    The valence category is not repeated more than 3 times in a row
    
TODO: still relevant in the post scan?
- 12 fillers are added to the list. They are divided randomly across 
    the experimental trials, with the constraint that two (or more) fillers 
    should not occur in a row
- Except from the very first and last two trials. Those four are fillers at a
fixed position

A new trial list is generated for each participant (for now 70) and saved as csv files. 
The csv file is read in in OpenSesame, depending on the subject number
and the block, in the item called IMDF_recall_blockloop.

NOTE that valence of the associated scene is taken into account, such that the
two distractor objects are from the same associated valence as the target object.
If the target scene (to which the object should be linked) is negative, the two
distractor objects are also objects that are associated with (another) negative scene.
This was to keep things similar to the TNT MC task

TODO:
1. No other constraints are applied to the fillers. At the beginning and the
end there could be, by chance, two distractors from the same valence category
(so this is different from the fMRI part). THIS SHOULD BE CHANGED

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
import addDistractorsImdf
import getBlockLoopsScanner # TODO add...() functions in separate module?


def applyConstraints(dm_exp, dm_fillers):
    

    """
    Arguments:
    dm_exp        --- dm containing exp scene-object combinations
    dm_fillers    --- dm containing filler scene-object combinations
    
    Returns:
    final_dm        --- final datamatrix for the IMDF MC memory task
    """
    
    
    # Add distractors:
    dm_exp = addDistractorsImdf.addDistractors(dm_exp)
    dm_fillers = addDistractorsImdf.addDistractors(dm_fillers)
    

    # Shuffle the fillers:
    dm_fillers = ops.shuffle(dm_fillers)
    
    # Merge first 4 fillers to the main dm
    # NOTE: we leave out four fillers because we will use them for the
    # very first and the very last trials
    
    # TODO: select 2 neg en 2 neutral
    dm_fillers_slice = dm_fillers[0:4]
    main_dm = dm_exp << dm_fillers_slice
    
    # Shuffle the main dm:
    main_dm = ops.shuffle(main_dm)
    
    # Create an Enforce object, and add two constraints
    ef = Enforce(main_dm)
    ef.add_constraint(MaxRep, cols=[main_dm.Emotion], maxrep=3)
    ef.add_constraint(MinDist, cols=[main_dm.Trial_ID], mindist=2)
    
    # Enforce the constraints
    main_dm = ef.enforce()
    # See the resulting DataFrame and a report of how long the enforcement took.
    
    
    # Add two fillers to the beginning of the final dm:
    dm_fillers_slice_first = dm_fillers[4:6]
    final_dm = dm_fillers_slice_first << main_dm
    
    # And to the end fo the final dm:
    dm_fillers_slice_last = dm_fillers[6:]
    final_dm = final_dm << dm_fillers_slice_last
    
    return final_dm


if __name__ == "__main__":
    
    src_file = "trial list postscan"
    dst_file = "trial list postscan/block loops IMDF postscan"
    
    
    # And experimental trials (without distractors)
    dm_exp = io.readtxt(os.path.join(src_file, 'IMDF_pairs_exp.csv'))
    dm_exp = getBlockLoopsScanner.addValenceColumn(dm_exp)
    dm_exp["Exp_ID"] = "IMDF_postscan"
    
    # Read dm containing fillers (without distractors)
    dm_fillers = io.readtxt(os.path.join(src_file, 'IMDF_pairs_fillers.csv'))
    dm_fillers["Exp_ID"] = "IMDF_postscan"
    
    for subject_ID in range(1, 71):
        
        pp_dm = applyConstraints(dm_exp, dm_fillers)
        io.writetxt(pp_dm, os.path.join(dst_file, "block_loop_IMDF_postscan_PP_%s.csv" % subject_ID))

        
        
