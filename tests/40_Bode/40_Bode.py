from PyQSPICE import clsQSPICE as pqs

import re
import math
import cmath
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

fname = "Buck_COT_Bode"

run = pqs(fname)

try: not run.ts['cir']
except: run.qsch2cir()
try: not run.ts['qraw']
except: run.cir2qraw()

run.setNline(499)

df = run.LoadQRAW(["OpenLoopGain"])

def CalcGainPhase(row):
    row["gain"] = 20*math.log10(abs(row["OpenLoopGain"]))
    row["phase"] = math.degrees(cmath.phase(row["OpenLoopGain"]))
    return row
df = df.apply(CalcGainPhase, axis=1)

run.comp2real(df, ["Step", "gain", "phase", run.sim['Xlbl']])


#######
# Plot Default

mpl.rcParams.update([['font.sans-serif', ["Arial Rounded MT Bold", 'Arial Unicode MS', 'Arial', 'sans-serif']], ["mathtext.default", "rm"], ["legend.labelspacing", 0.1], ["legend.columnspacing", 0.2], ["legend.handletextpad", 0.3], ['axes.formatter.useoffset', False], ['xtick.minor.visible', True], ['ytick.minor.visible', True], ['grid.linewidth', 1],["savefig.dpi", 300], ["axes.unicode_minus", False]])

#######
# Plotting Pandas, AC

plt.close('all')
plt.style.use('ggplot')


fig2, (axT, axB) = plt.subplots(2,1,sharex=True,constrained_layout=True)

df.plot(ax=axB, x="Freq",  y="phase", label="Phase")
df.plot(ax=axT, x="Freq",  y="gain", label="Gain")

axB.set_xscale('log')
axB.set_xlim(1e3,100e3)
axB.set_xticks([1e3,2e3,4e3,6e3,8e3,1e4,2e4,4e4,6e4,8e4,1e5],["1k","2k","4k","6k","8k","10k","20k","40k","60k","80k","100k"])

axT.set_ylim(-20,60)
axB.set_ylim(0,90)

axT.set_ylabel('Gain (dB)', fontsize=14)
axB.set_ylabel('Phase (°)', fontsize=14)
axB.set_xlabel('Frequency (Hz)', fontsize=14)

axB.grid(which='major', linewidth="0.5")
axB.grid(which="minor", linewidth="0.35")
axT.grid(which='major', linewidth="0.5")
axT.grid(which="minor", linewidth="0.35")

axT.minorticks_on()
axB.minorticks_on()

plt.savefig(run.path['base'] + "_plt.png", format='png', bbox_inches='tight')

plt.show()

plt.close('all')

