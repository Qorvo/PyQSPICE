from PyQSPICE import clsQSPICE as pqs

import os
import math
import cmath
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

################
run = pqs("op")

run.qsch2cir()
run.cir2qraw()
run.setNline(16)

expr = run.parseCir()
df = run.LoadQRAW(expr)
#print(f"Expression of all V&I from QSPICE: {expr}")

print(f"Voltage Node Operating Points:\n{df.loc[:,list(map(lambda x: "V(" + x + ")",run.node))]}\n")

print(f"Voltage nodes: {run.node}")
print(f"Circuit elements: {run.elem}")
print(f"\t2 port elements: {run.ele2}")
print(f"\tTransistors: {run.eleT}")

################

run.InitPlot()
plt.close('all')

fig, ax = plt.subplots(tight_layout=True)

df.plot(ax=ax, x=run.sim['Xlbl'],  y="Id(J1)", label=r"$I_{DRAIN}$")

run.PrepFreqGainPlot(ax, f'.Step {run.sim['Xlbl']}', 'Drain Current (A)', [run.sim['Xmin'],run.sim['Xmax']])

plt.legend(ncol=1, loc="center left",fancybox=True)


run.tstime(['png'])
plt.savefig(run.path['png'], format='png', bbox_inches='tight')
plt.show()
plt.close('all')
