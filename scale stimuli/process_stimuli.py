# Import libraries:
import os
import sys
from PIL import Image


# Define constants:

# The script assumes that you have two folders in the current
# directory. (The current directory is the directory where your
# Python script is located and ran)

SRC = "./scenes_raw" # Folder containing original scenes
DST = "./scenes_scaled" # (Empty) destination folder for rescaled images

# Intended size (depending on whether the image is landscape or portrait)
GOAL_WIDTH_LANDSCAPE = 1000
GOAL_HIGH_PORTRAIT = 800

# Walk through raw scenes:
for raw_file in os.listdir(SRC):
    src_file = os.path.join(SRC, raw_file)

    # Open the image:
    img = Image.open(src_file)


    # Get the original size:
    w, h = img.size

    # Determine whether the scene is in landscape or portrait:

    if w > h:
        orientation = "landscape"
    else:
        orientation = "portrait"

    # Determine the desired size, depending on the orientation:
    # (Make sure new width and height are integers, not floats)
    if orientation == "landscape":
        w_new = GOAL_WIDTH_LANDSCAPE
        h_new = int(w_new * h / w)

    elif orientation == "portrait":
        h_new = GOAL_HIGH_PORTRAIT
        w_new  = int(h_new * w / h)


    else:
        raise Exception("Unknown orientation")

    # Scale the image:
    new_img = img.resize((w_new, h_new), Image.ANTIALIAS)

    # Determine the destination path
    dst_file = os.path.join(DST, raw_file)

    # Save the new image:
    new_img.save(dst_file)
