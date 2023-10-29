from PyQSPICE import clsQSPICE as pqs

import re
import math
import cmath
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

print("\n\nThis example needs, newer version of the PyQSPICE: " + pqs.version() + ".\n\n")

fname = "VRM_Nyquist"

run = pqs(fname)

run.qsch2cir()
run.cir2qraw()

run.setNline(2048)

g = "V(VOUT)/V(VO)"

df = run.LoadQRAW([g])

def Calc(row):
    row["gain"] = 20*math.log10(abs(row[g]))
    row["phase"] = math.degrees(cmath.phase(row[g]))
    row["reGain"] = row[g].real * -1
    row["imGain"] = row[g].imag * -1
    return row
df = df.apply(Calc, axis=1)

# Bring back some data "real"
run.comp2real(df, ["Step", "reGain", "imGain", "gain", "phase", run.sim['Xlbl']])

#######
# Plot Default

mpl.rcParams.update([['font.sans-serif', ["Arial Rounded MT Bold", 'Arial Unicode MS', 'Arial', 'sans-serif']], ["mathtext.default", "rm"], ["legend.labelspacing", 0.1], ["legend.columnspacing", 0.2], ["legend.handletextpad", 0.3], ['axes.formatter.useoffset', False], ['xtick.minor.visible', True], ['ytick.minor.visible', True], ['grid.linewidth', 1],["savefig.dpi", 300], ["axes.unicode_minus", False]])
plt.close('all')
plt.style.use('ggplot')

# Prepare a blank plotting area
fig2, (axT, axB) = plt.subplots(2,1,sharex=True,constrained_layout=True)

# Plot Bode (AC) curves
df.plot(ax=axB, x="Freq",  y="phase", label="Phase")
df.plot(ax=axT, x="Freq",  y="gain", label="Gain")

# Axis setup = begin =
axB.set_xscale('log')
axT.set_ylabel('Gain (dB)', fontsize=14)
axB.set_ylabel('Phase (°)', fontsize=14)
axB.set_xlabel('Frequency (Hz)', fontsize=14)
axB.grid(which='major', linewidth="0.5")
axB.grid(which="minor", linewidth="0.35")
axT.grid(which='major', linewidth="0.5")
axT.grid(which="minor", linewidth="0.35")
axT.minorticks_on()
axB.minorticks_on()
# Axis setup = end =

plt.show()
plt.close('all')

(fc, pm) = run.x0pos2neg(df, "gain", "phase")
(fg0, gmdB) = run.x0pos2neg(df, "phase", "gain")
gm = 10 ** (gmdB/20)

import numpy as np
from numpy import sin, cos, pi, linspace

# Prepare a blank plotting area
fig, (ax, axF) = plt.subplots(1,2,tight_layout=True)

# Zoomed Plot, at the left
df.plot(ax=ax, x="reGain",  y="imGain")
# Zoomed Plot, at the left

ax.set_title('Nyquist Diagram, Zoom')
ax.set_xlim(-2,2)
ax.set_ylim(-2,2)
ax.set_xlabel('', fontsize=14)
ax.set_ylabel('', fontsize=14)
ax.yaxis.tick_right()
ax.xaxis.tick_top()
ax.set_yticks([-2,-1,0,1,2])
ax.set_xticks([-2,-1,0,1,2])
ax.spines['top'].set_position(('data', 0))
ax.spines['top'].set_color('gray')
ax.spines['right'].set_position(('data', 0))
ax.spines['right'].set_color('gray')
ax.minorticks_off()
ax.get_legend().remove()
ax.set_aspect("equal", adjustable="box")

ax.plot(-cos(pm/180*pi),-sin(pm/180*pi), marker = 'o')
aar = linspace(0, 2*pi, 100)
xar = cos(aar)
yar = sin(aar)
ax.plot(xar,yar)
ax.plot([-2*cos(pm/180*pi),0],[-2*sin(pm/180*pi),0])

arc = linspace(0, pm/180*pi, 20)
xarc = -1.5 * cos(arc)
yarc = -1.5 * sin(arc)
ax.plot(xarc, yarc)
ax.text(-2,-0.3,r"$\phi_m$={:.1f}°".format(pm))

ax.plot(-gm,0,marker = 'o',markersize=4,markeredgecolor="black")
ax.plot([-gm,-gm], [0,0.4])
ax.text(-0.6,0.5,r"G.M.={:.1f}dB".format(gmdB))

# Full Plot, at the right
df.plot(ax=axF, x="reGain",  y="imGain")
# Full Plot, at the right

axF.set_xlabel('Re(Gain)', fontsize=14)
axF.set_ylabel('Im(Gain)', fontsize=14)
axF.set_aspect("equal", adjustable="box")
axF.get_legend().remove()
axF.set_title('Nyquist Diagram, Full')

run.tstime(['png'])
plt.savefig(run.path['png'], format='png', bbox_inches='tight')
plt.show()

plt.close('all')

