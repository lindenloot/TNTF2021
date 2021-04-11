"""
DESCRIPTION:
Checks whether all objects are of equal size.
"""
from datamatrix import io

import os
from PIL import Image

src_imgs = "/home/lotje/Documents/Research, teaching and programming/OpenSesame/Scripts/Others/Claudius Schroeder/TNTF2021/experimental files"

exp = "IMDF"
stim_type = "Scene"

src_exp = "%s_pairs_exp.csv" % exp
src_fillers = "%s_pairs_fillers.csv" % exp

# Get dm containing the names of all objects:
dm_exp = io.readtxt(src_exp)
dm_fillers = io.readtxt(src_fillers)
dm = dm_exp << dm_fillers

# Walk through all objects:
print("\nThe following %s %ss have a deviating size:" % (exp, stim_type))

for row in dm:
    stim = row[stim_type]
    src_path = os.path.join(src_imgs, stim)
    
    # Open the image:
    img = Image.open(src_path)

    # Get the original size:
    w, h = img.size
    
    
    if stim_type == "Object":
        if exp == "TNT":
            if (w, h) != (2000, 2000):
                print("\tTNT:", stim)
                
        if exp == "IMDF":
            if (w, h) != (768, 576):
                print("\tIMDF:", stim)
    elif stim_type == "Scene":
         if (w,h) != (1000,750) and (w,h) != (600,800):
             print("\tIMDF:", stim)

        
