import sys
import subprocess
import os
import os.path
from os.path import expanduser
from datetime import datetime
import re

import matplotlib as mpl
import matplotlib.font_manager as fm
import pandas as pd
import math
import cmath



class clsQSPICE:
## Version Number
    verstr = "2023.11.29"

## Global (Class) Path Information
    gpath = {}
    gpath['cwd'] = os.getcwd()
    gpath['home'] = expanduser("~")
    usrp = gpath['home'] + "/QSPICE/"
    sysp = r"c:/Program Files/QSPICE/"

    for exe in ['QUX', 'QSPICE64']:
        if os.path.isfile(sysp + exe + '.exe'): gpath[exe] = sysp + exe + '.exe'
        # User path has priority
        if os.path.isfile(usrp + exe + '.exe'): gpath[exe] = usrp + exe + '.exe'
        try: gpath[exe]
        except: print(exe + ".exe not found!") * exit()
    del usrp, sysp

    @classmethod
    def version(cls):
        return cls.verstr

    @classmethod
    def chdir(cls, dir):
        try: os.path.isdir(dir)
        except: print("No such directory:" + dir, file=sys.stderr) * exit()
        os.chdir(dir)
        cls.gpath['cwd'] = os.getcwd()

    def __init__(self, fname):
        self.path = {}
        self.ts = {}
        self.date = {}

        self.sim = {"Nline": 4999, "Nstep": 0}

        self.path['user'] = fname
        self.path['base'] = fname.removesuffix('.qsch').removesuffix('.qraw').removesuffix('.cir')
        clsQSPICE.tstime(self, ['qsch', 'qraw', 'cir'])

    # How many data points to read from QRAW simulation result files
    # Too small, too zigzag; too big, too slow ☹    
    def setNline(self, i):
        self.sim['Nline'] = i

    # Generate a netlist CIR file from the source schematic QSCH file
    def qsch2cir(self):
        if self.ts['qsch']:
            with open(self.path['cir'], "w") as ofile:
                subprocess.run([self.gpath['QUX'], "-Netlist", self.path['qsch'], "-stdout"], stdout=ofile)
                clsQSPICE.tstime(self, ['cir'])

    # Run a simulation from the netlist CIR file
    def cir2qraw(self):
        if self.ts['cir']:
            subprocess.run([self.gpath['QSPICE64'], self.path['cir']])
            clsQSPICE.tstime(self, ['qraw'])

    # Load simulation result signals from the simulation results QRAW file
    # Input:  Array of signal strings in the way you specify in ".PLOT" statement
    # Output:  It returns Pandas DataFrame
    #  ==> Pandas supports data loading from the STDOUT-STDIN PIPE/stream (where the Numpy doesn't...temporary file needed)
    def LoadQRAW(self, probe):
        if self.ts['qraw']:
            plots = ",".join(probe)
            with subprocess.Popen([self.gpath['QUX'], "-Export", self.path['qraw'], plots, str(self.sim['Nline']), "SPICE", "-stdout"], stdout=subprocess.PIPE, text=True) as qux:
                flgv = 0
                while True:
                    line = qux.stdout.readline()
                    if line == '\n': continue        
                    if line.startswith("Values:"): break
                    if line.startswith("No. Points:"):
                        self.sim['Nstep'] = int(int(re.match(r'^No. Points:\s*(\d+).*', line).group(1)) / (self.sim['Nline']+1))
                    if line.startswith("Plotname:"):
                        self.sim['Type'] = re.match(r'^Plotname:\s+(\S.*)$', line).group(1)
                        if self.sim['Type'].startswith("Tran"):
                            self.sim['Xlbl'] = "Time"
                        if self.sim['Type'].startswith("AC"):
                            self.sim['Xlbl'] = "Freq"
                        if self.sim['Type'].startswith("DC"):
                            self.sim['Xlbl'] = "DC"
                        if self.sim['Type'].startswith("Oper"):
                            self.sim['Xlbl'] = "OP"
                    if line.startswith("Abscissa:"):
                        pat = r'^Abscissa:\s+(\S+)\s+(\S+)\s*'
                        self.sim['Xmin'] = float(re.match(pat,line).group(1))
                        self.sim['Xmax'] = float(re.match(pat,line).group(2))
                    if flgv == 1 and (self.sim['Type'].startswith("DC") or self.sim['Type'].startswith("Ope")):
                        self.sim['Xlbl'] = re.match(r'^\s*(\S+)\s+(\S+)\s+(\S+).*', line).group(2)
                        flgv = 0
                    if line.startswith("Variables:"):
                        flgv = 1

            with subprocess.Popen([self.gpath['QUX'], "-Export", self.path['qraw'], plots, str(self.sim['Nline']), "CSV", "-stdout"], stdout=subprocess.PIPE, text=True) as qux:

                head = []
                head.append(self.sim['Xlbl'])
                head.extend(probe)

                if self.sim['Type'].startswith("AC"):
                    df = pd.read_csv(qux.stdout, sep='\t', header=0, names=head)
                if self.sim['Type'].startswith("Tran") or self.sim['Type'].startswith("DC") or self.sim['Type'].startswith("Ope"):
                    df = pd.read_csv(qux.stdout, sep=',', header=0, names=head)                    

                if self.sim['Type'].startswith("AC"):
                    for lbl in probe:
                        df[lbl] = df[lbl].map(lambda x: complex(x.replace(',-','-').replace(',','+') + 'j'))

                tmp = []
                for i in range(self.sim['Nstep']):
                    tmp = tmp + ([i] * (self.sim['Nline']+1))

                df["Step"] = tmp
                if self.sim['Nstep'] > 1:
                    try: os.path.isfile(self.path['cir'])
                    except: self.qsch2cir()
                    with open(self.path['cir']) as f:
                        for line in f:
                            if re.match(r'^\.(step|STEP)', line):
                                try: self.sim["StepInfo"]
                                except: self.sim["StepInfo"] = ""
                                self.sim["StepInfo"] = self.sim["StepInfo"] + line
                else:
                    self.sim["StepInfo"] = "N/A"

            return df

    # In the given DataFrame "df", search the "crossing" signal crossing ZERO from positive to negative,
    # then, returns the "target" signal and frequency "freq" values at the ZERO-crossing
    def x0pos2neg(self, df, crossing, target, freq="Freq"):
        dftmp = pd.concat([df[df[crossing] > 0].tail(1),df[df[crossing] < 0].head(1)])
        #print(dftmp)
        (x0,x1) = dftmp[crossing]
        (t0,t1) = dftmp[target]
        (f0,f1) = dftmp[freq]
        #print(x0,x1,t0,t1,f0,f1)
        f = (x0 / (x0 - x1)) * (f1 - f0) + f0
        t = (x0 / (x0 - x1)) * (t1 - t0) + t0
        return(f, t)

    # In the given DataFrame "df", search the "crossing" signal crossing ZERO from negative to positive.
    # then, returns the "target" signal and frequency "freq" values at the ZERO-crossing
    def x0neg2pos(self, df, crossing, target, freq="Freq"):
        dftmp = pd.concat([df[df[crossing] < 0].tail(1),df[df[crossing] > 0].head(1)])
        #print(dftmp)
        (x0,x1) = dftmp[crossing]
        (t0,t1) = dftmp[target]
        (f0,f1) = dftmp[freq]
        #print(x0,x1,t0,t1,f0,f1)
        f = f1 - (x1 / (x1 - x0)) * (f1 - f0)
        t = t1 - (x1 / (x1 - x0)) * (t1 - t0)
        return(f, t)

    # Calculate absolute value of the "target" in dB, also colculate argument of the "target"
    # If strings specified, it also extrace real and imaginary part of the "target"
    # Further-If "-1" specified, returns real and imaginary part of the "target" with 180 degree rotated.
    # NOTE: apply() method returns new DataFrame object, so it returns this new object
    def GainPhase(self, df, target, strabs, strarg, strre="none", strim="none", sign=1):
        def Calc(row):
            row[strabs] = 20*math.log10(abs(row[target]))
            row[strarg] = math.degrees(cmath.phase(row[target]))
            if strre != "none":
                row[strre] = row[target].real * sign
            if strim != "none":
                row[strim] = row[target].imag * sign
            return row
        return df.apply(Calc, axis=1)

    # Calculate QTg for NISM
    def QTg(self, df, flbl, vlbl, angle=1):
        ddf = df - df.shift()
        adf = (df + df.shift())/2
        ddf[flbl] = adf.iloc[:,0]
        def Calc(row):
            row[vlbl] = -0.5 * row.iloc[1] / row.iloc[0] * row[flbl] / angle
            return row
        retdf = ddf.drop(0).apply(Calc,axis=1).loc[:,[flbl, vlbl]]
        return retdf.reset_index(drop=True)
    
    # Convert Pandas DataFrame element to real/float
    #     Pandas converts all data into complex when using "apply" method, for example calculating "gain".
    #       ==> Someone, help here how to stop this Pandas' behavior !
    #     When we plot the data, we need real numbers.
    def comp2real(self, df, idx):
        for i in idx:
            df[i] = df[i].map(lambda x: (x).real)

    # Obtain a component value specified
    # It returns "number" or "simulation variable label".
#    def findRLC(self, target):
#        with open(self.path['cir'], encoding='SJIS') as f:
#            val = -1
#            for line in f:
#                l = line.rstrip('\r\n')
#                if (ret := re.match(target + r"\s+(\S+)\s+(\S+)\s+(\d+)(.*)", l, flags=re.IGNORECASE)):
#                    val = float(ret.group(3))
#                    if bytes(ret.group(4), 'sjis') == b'\xb5': val = val * 1e-6
#                    if (ret.group(4) == "f") or (ret.group(4) == "F"): val = val * 1e-15
#                    if (ret.group(4) == "p") or (ret.group(4) == "P"): val = val * 1e-12
#                    if (ret.group(4) == "n") or (ret.group(4) == "N"): val = val * 1e-9
#                    if (ret.group(4) == "u") or (ret.group(4) == "U"): val = val * 1e-6
#                    if (ret.group(4) == "m") or (ret.group(4) == "M"): val = val * 1e-3
#                    if (ret.group(4) == "k") or (ret.group(4) == "K"): val = val * 1e3
#                    if (ret.group(4) == "g") or (ret.group(4) == "G"): val = val * 1e9
#                    if (ret.group(4) == "t") or (ret.group(4) == "T"): val = val * 1e12 
#                    if re.match(r"[mM][eE][gG]", ret.group(4)): val = val * 1e6
#                elif (ret := re.match(target + r"\s+(\S+)\s+(\S+)\s+(\S+)", l, flags=re.IGNORECASE)):
#                    val = ret.group(3)
#            return val
            
    # Obtain a list of nodes
    def parseCir(self):
        two = r"^([RLCDFHIVWY]\S+)\s+(\S+)\s+(\S+)\s+(\S+)(.*)"
        three =      r"^([JUZ]\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)(.*)"
        four =   r"^([EGMOQST]\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)(.*)"
        
        node = {"0": 0}
        self.elem = {}
        self.ele2 = []
        self.eleT = []
        
        with open(self.path['cir'], encoding='SJIS') as f:
            for line in f:
                l = line.rstrip('\r\n')
                if ret := re.match(two, l, flags=re.IGNORECASE):
                    node[ret.group(2)] = 0
                    node[ret.group(3)] = 0
                    self.elem[ret.group(1)] = clsQSPICE._engSuf(ret.group(4))
                    self.ele2.append(ret.group(1))
                if ret := re.match(three, l, flags=re.IGNORECASE):
                    node[ret.group(2)] = 0
                    node[ret.group(3)] = 0
                    node[ret.group(4)] = 0
                    self.elem[ret.group(1)] = ret.group(5) # model name
                    if re.match(r"^[JZ]", l, flags=re.IGNORECASE):
                        self.eleT.append(ret.group(1))
                if ret := re.match(four, l, flags=re.IGNORECASE):                    
                    node[ret.group(2)] = 0
                    node[ret.group(3)] = 0
                    node[ret.group(4)] = 0
                    node[ret.group(5)] = 0
                    self.elem[ret.group(1)] = ret.group(6) # To be updated later
                    if re.match(r"^[EGS]", l, flags=re.IGNORECASE):
                        self.ele2.append(ret.group(1))
                    if re.match(r"^[MQ]", l, flags=re.IGNORECASE):
                        self.eleT.append(ret.group(1))
            del node["0"]
            self.node = list(node.keys())
            all = list(map(lambda x: "V(" + x + ")", self.node)) \
                + list(map(lambda x: "I(" + x + ")", self.ele2)) \
                + list(map(lambda x: "Id(" + x + ")", self.eleT)) \
                + list(map(lambda x: "Ig(" + x + ")", self.eleT)) \
                + list(map(lambda x: "Is(" + x + ")", self.eleT))
            return all


    def _engSuf(pat):
        val = pat
        if ret := re.match(r"(\d+)(\S+)", pat, flags=re.IGNORECASE):
            val = float(ret.group(1))
            if bytes(ret.group(2), 'sjis') == b'\xb5': val = val * 1e-6
            if (ret.group(2) == "f") or (ret.group(2) == "F"): val = val * 1e-15
            if (ret.group(2) == "p") or (ret.group(2) == "P"): val = val * 1e-12
            if (ret.group(2) == "n") or (ret.group(2) == "N"): val = val * 1e-9
            if (ret.group(2) == "u") or (ret.group(2) == "U"): val = val * 1e-6
            if (ret.group(2) == "m") or (ret.group(2) == "M"): val = val * 1e-3
            if (ret.group(2) == "k") or (ret.group(2) == "K"): val = val * 1e3
            if (ret.group(2) == "g") or (ret.group(2) == "G"): val = val * 1e9
            if (ret.group(2) == "t") or (ret.group(2) == "T"): val = val * 1e12 
            if re.match(r"[mM][eE][gG]", ret.group(2)): val = val * 1e6
        if ret := re.match(r"(\d+)", pat):
            val = float(ret.group(1))
        return val
    
    # Obtain time-stamp of specified suffix files on Windows OS
    # You may use this to add your plot files ".PNG", ".JPG" for the cleaning, see next function "clean()".
    def tstime(self, arr):
        for suf in arr:
            self.path[suf] = self.path['base'] + "." + suf
            try: self.ts[suf] = os.path.getmtime(self.path[suf])
            except:
                self.ts[suf] = 0
                try: del self.date[suf]
                except: pass
            if self.ts[suf]:
                self.date[suf] = datetime.fromtimestamp(self.ts[suf])

    # Delete specified files
    # Be carefule, it can delete your schematic "QSCH" file without warning.
    def clean(self,suf):
        for s in suf:
            try: os.remove(self.path[s])
            except: print("Can't remove file:" + self.path[s], file=sys.stderr)
        self.tstime(suf)

    # Matplotlib Preparing a Plot for Frequency-Gain
    def PrepFreqGainPlot(self, ax, xlbl="", ylbl="", xlim=[], ylim=[]):
        ax.set_xscale('log')
        ax.grid(which='major', linewidth="0.5")
        ax.grid(which='minor', linewidth="0.35")
        if xlbl != "": ax.set_xlabel(xlbl)
        if ylbl != "": ax.set_ylabel(ylbl)
        if len(ylim) == 2: ax.set_ylim(ylim[0],ylim[1])
        
        lfreq = pd.DataFrame({
            "f": [1e-18, 1e-17, 1e-16, 1e-15, 1e-14, 1e-13, 1e-12, 1e-11, 1e-10, 1e-9, 1e-8, 1e-7,  1e-6, 1e-5, 1e-4,  1e-3, 1e-2, 1e-1,  1,   10,   100,  1e3, 1e4,  1e5,   1e6, 1e7,  1e8,   1e9],
            "l": ["1a",  "10a", "100a","1f",  "10f", "100f","1p",  "10p", "100p","1n", "10n","100n","1μ", "10μ","100μ","1m", "10m","100m","1", "10", "100","1k","10k","100k","1M","10M","100M","1G"],
        })
        if len(xlim) == 2:
            lf = lfreq[(lfreq.f > (xlim[0]/10)) & (lfreq.f < (xlim[1]*10))].reset_index(drop=True)
            ax.set_xlim(lf.iat[0,0],lf.iat[-1,0])
            ax.set_xticks(lf.loc[:,"f"],lf.loc[:,"l"])
            
    # Matplotlib Preferences
    #   Font for Rounded Noto
    #   Style for "ggplot"
    def InitPlot(self):
        sfile = self.gpath['home'] + "/.config/matplotlib/ggplot_mod.mplstyle"
        if os.path.exists(sfile): mpl.rc_file(sfile)
        sfile = "./my.mplstyle"
        if os.path.exists(sfile): mpl.rc_file(sfile)

        mfont = self.gpath['home'] + "/.config/matplotlib/ResourceHanRoundedJP-Medium.ttf"
        if os.path.exists(mfont): fe = fm.FontEntry(fname=mfont, name="Resource Han Rounded JP Medium")
        mfont = self.gpath['home'] + "/.config/matplotlib/GenJyuuGothicL-Medium.ttf"
        if os.path.exists(mfont): fe = fm.FontEntry(fname=mfont, name="GenJyuuGothicL Medium")
        if fe:
            fm.fontManager.ttflist.insert(0,fe)
            mpl.rcParams['font.family'] = fe.name
