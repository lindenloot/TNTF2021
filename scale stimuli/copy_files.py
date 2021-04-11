from datamatrix import io
from datamatrix import operations as ops
from datamatrix import DataMatrix

import os
import shutil

src_exp = "IMDF_pairs_exp.csv"
src_fillers = "IMDF_pairs_fillers.csv"

src_imgs = "/home/lotje/Documents/Research, teaching and programming/OpenSesame/Scripts/Others/Claudius Schroeder/TNTF2021/experimental files"

dst_imgs = "./IMDF_scenes_raw" # Folder containing original scenes

dm_exp = io.readtxt(src_exp)
dm_fillers = io.readtxt(src_fillers)
dm = dm_exp << dm_fillers
print(dm.length)

for row in dm:
    scene = row["Scene"]
    src_path = os.path.join(src_imgs, scene)
    dst_path = os.path.join(dst_imgs, scene)
    shutil.copy(src_path, dst_path)
