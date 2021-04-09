"""
DESCRIPTION:
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
1. No other constraints are applied to the fillers. At the beginning and the
end there could be, by chance, two distractors from the same valence category
(so this is different from the fMRI part)
2. The match of target and distractors is held constant between test feedback 
and criterion test, because that is what I understood from the description.
If distractors should be reshuffled, let me know.

"""

# Python modules:
import random
import os
from pseudorandom import Enforce, MaxRep, MinDist


# Datamatrix modules:
from datamatrix import io
from datamatrix import operations as ops
from datamatrix import DataMatrix


# Import own modules:
import addDistractors


dst_folder = "trial list prescan"
src_folder = "trial list prescan"

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
    dm_fillers = addDistractors.addDistractors(dm_fillers)
    
    # Make sure we will collect two dms
    list_dms = []
    
    for block in ["test_feedback", "criterion_test"]:
    
        # Shuffle the fillers:
        dm_fillers = ops.shuffle(dm_fillers)
        
        # Merge first 8 fillers to the main dm
        # NOTE: we leave out four fillers because we will use them for the
        # very first and the very last trials
        dm_fillers_slice = dm_fillers[0:8]
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
        dm_fillers_slice_first = dm_fillers[8:10]
        final_dm = dm_fillers_slice_first << main_dm
        
        # And to the end fo the final dm:
        dm_fillers_slice_last = dm_fillers[10:]
        final_dm = final_dm << dm_fillers_slice_last
        
        # Append to the dm list:
        list_dms.append(final_dm)

    # Unpack the list so we can return two separate dms
    dm1, dm2 = list_dms

    return dm1, dm2


if __name__ == "__main__":
    
    
    # And experimental trials (without distractors)
    dm_exp = io.readtxt(os.path.join(src_path, 'dm_exp.csv'))
    
    # Read dm containing fillers (without distractors)
    dm_fillers = io.readtxt(os.path.join(src_path, 'dm_fillers.csv'))
    
    for subject_ID in range(1, 71):
        
        dm1, dm2 = applyConstraints(dm_exp, dm_fillers)
        io.writetxt(dm1, os.path.join(dst_path, "block_loop_test_feedback_PP_%s.csv" % subject_ID))
        io.writetxt(dm2, os.path.join(dst_path, "block_loop_criterion_test_PP_%s.csv" % subject_ID))
        
        
