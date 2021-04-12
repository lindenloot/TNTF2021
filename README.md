# TNTF2021

## generate trial lists

## scale stimuli

Scale scene stimuli to a given size, check whether objects all have the same size

## generate trial lists

Generates csv files per experimental block and per participants. Resulting csv files are read in in the `block_loop` items in OpenSesame

Uses `DataMatrix` and the built-in Python module `pseudorandom`

### input files

The input files are deduced from the final .xlsx files that CVS sent

#### TNT

For the pre-lab and post-lab phase:

- TNT_pairs_exp.csv
- TNT_pairs_fillers.csv -> contains all filler pairs
- TNT_practice_pairs_fillers.csv -> only contains the filler pairs that are not used in the scanner

For the scanner phase:

- TNT_scanner_pairs.csv -> contains pairs AND NULL trials
- TNT_scanner_pairs_fillers.csv -> only contains four filler pairs

#### TNT


For the post-lab phase:

- IMDF_pairs_exp.csv
- IMDF_pairs_fillers.csv

For the scanner phase

- IMDF_scanner_pairs_exp.csv -> contains pairs AND NULL trials
- IMDF_scanner_pairs_fillers.csv -> so far similar to the other filler list

### output folders

- trial list prescan
- trial list scanner
- trial list postscan

### scripts




## experimental files

To run the osexp files, all the stimuli should be placed in the experimental folder, that is, in the same directory as where the osexp files are placed. This is because I had to empty the file pool because it became too large

 
