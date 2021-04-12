###################
# package imports #
###################

from datamatrix import DataMatrix
from datamatrix import io
from datamatrix import operations as ops
from pseudorandom import Enforce, MaxRep, MinDist
import neurodesign.classes
from neurodesign import generate
import matplotlib.pyplot as plt
import os
import os.path as op
import time
import numpy as np

dm = io.readtxt('dm.csv')
dm = dm["condition"] != "NULL"


# Determine the number of trials
nTrials = dm.length
# And unique conditions
nStim = len(np.unique(np.asarray(dm["condition"])))
print(nStim)

TNTfMRI = neurodesign.classes.experiment(
    TR=2,rho=0, # rho (assumed auotcorrelation coefficient) greatly impacts Fd i.e. higher rho (0.3 = default) = much lower Fd / 0 is best
    n_stimuli=nStim, n_trials=nTrials,
    P=[0.20,0.20,0.20,0.20,0.20],
    C=[[1,1,-1,-1,0],[1,0,-1,0,0],[0,1,0,-1,0]],
    t_pre=0,stim_duration=3,t_post=1, # since there are only 20% NULL events incl here I am ok with the intrusion ratings being modled with the NULL events, to add a bit more time to them (does that reasoning work? Or is it the frequency of NULL events that important i.e. not their duration?)
    #hardprob=True,maxrep=3, # (maxrep=3 is not true for NULL events)
    restnum=0,restdur=0,
    ITImodel="exponential",resolution=0.1, # resolution greatly impacts Fe i.e. higher (0.4) = much lower Fe / 0.1 is best
    ITImin=1.4,ITImean=2,ITImax=2.6,
    FeMax=1,FdMax=1,FcMax=1,FfMax=1,
    confoundorder=3) # lower confound order seems to more consistently yield better Fe (3 is default, but 1 seems to be best - however, still possible to get a good result with loop if set to 3)

# Read a datafile with Pandas and convert it to a pseudorandom DataFrame.


# Add a column containing condition as an int
# NULL trials are excluded?
i = 0

dm["condition_nr"] = None
for cond, _dm in ops.split(dm["condition"]):
    print(cond)
    dm["condition_nr"][dm["condition"] == cond] = i
    i +=1


# optimisation loop

Fe_threshold = 13#14.3 #(15)
Fd_threshold = 6#6.3 #(6.5)
Ff_threshold = 0.9 #(1)
Fc_threshold = 0.8 #(0.8)

timeout = time.time() + 60*5 # 5 minutes from now

while True:

    # convert new datamatrix to a list as input for DES1
    TNTorder = list(dm["condition_nr"])
    
    print(TNTorder)
    TNTdES = neurodesign.classes.design(
        order = TNTorder,
        ITI = generate.iti(ntrials=nTrials, model="exponential", min=1.4, mean=2, max=2.6,
                           resolution=0.1, seed=1234)[0],
        onsets = [], experiment = TNTfMRI)

    TNTdES.designmatrix()
    TNTdES.FeCalc();TNTdES.FdCalc();TNTdES.FfCalc();TNTdES.FcCalc()
    TNTdES.FCalc(weights=[0.25, 0.25, 0.25, 0.25])

    print("estimation efficiency = ", TNTdES.Fe, "\tdetection power = ", TNTdES.Fd, "\tstimulus frequency = ", TNTdES.Ff, "\tdesign predictability = ", TNTdES.Fc)

    if TNTdES.Fe > Fe_threshold and TNTdES.Fd > Fd_threshold and TNTdES.Ff > Ff_threshold and TNTdES.Fc > Fc_threshold or time.time() > timeout:
        print("Perfect")
    else:
        print("Not optimal")
        #break

print("FINAL: estimation efficiency = ", TNTdES.Fe, "\tdetection power = ", TNTdES.Fd, "\tstimulus frequency = ", TNTdES.Ff, "\tdesign predictability = ", TNTdES.Fc)

#print('TNT Run-1 Order Matrix:')
#print(TNTpseudM)
#print(ef.report)

TNTdm = DataMatrix(length=4)
TNTdm.efficiency = 'Fe','Fd','Ff','Fc'
TNTdm.score = (TNTdES.Fe,TNTdES.Fd,TNTdES.Ff,TNTdES.Fc)
print('TNT Run-1 Power & Efficiency Matrix:')
print(TNTdm)

TNTeffTOT = list(TNTdm.score)
TNTeffSUM = sum(TNTeffTOT)
print("TNT Run-1 Power & Efficiency Sum: "+str(TNTeffSUM))

TNTconditions = list(TNTpseudM.condition)

TNTtrialDm = DataMatrix(length=124)
TNTtrialDm.condition = (TNTconditions)
TNTtrialDm.order = (TNTdES.order)
TNTtrialDm.ITI = (TNTdES.ITI)
TNTtrialDm.onset = (TNTdES.onsets)
print('TNT Run-1 Trial Order Matrix:')
print(TNTtrialDm)

#print("Condition oder:")
#print(TNTorder)

#print("Interstimulus Intervals:")
#print(TNTdES.ITI)#[:120])

#print("Condition Onsets")
#print(TNTdES.onsets)#[:120])

# plot convolution model
plt.plot(TNTdES.Xconv)
out_dir = 'output'
if not op.isdir(out_dir):
    os.makedirs(out_dir)
plt.savefig(op.join(out_dir,'TNTrunCONV.pdf'),format="pdf")

print("Done!")
