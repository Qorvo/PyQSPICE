import sys
import subprocess
import os
import os.path
from os.path import expanduser
from datetime import datetime
import re

import pandas as pd


class clsQSPICE:
## Version Number
    verstr = "2023.10.10"

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

    def __init__(self, fname):
        self.path = {}
        self.ts = {}
        self.date = {}
        
        self.sim = {"Nline": 4999, "Nstep": 0}
        
        self.path['user'] = fname
        self.path['base'] = fname.removesuffix('.qsch').removesuffix('.qraw').removesuffix('.cir')
        clsQSPICE.tstime(self, ['qsch', 'qraw', 'cir'])
        
    def setNline(self, i):
        self.sim['Nline'] = i
    
    def qsch2cir(self):
        if self.ts['qsch']:
            with open(self.path['cir'], "w") as ofile:
                subprocess.run([self.gpath['QUX'], "-Netlist", self.path['qsch'], "-stdout"], stdout=ofile)
                clsQSPICE.tstime(self, ['cir'])
                
    def cir2qraw(self):
        if self.ts['cir']:
            subprocess.run([self.gpath['QSPICE64'], self.path['cir']])
            clsQSPICE.tstime(self, ['qraw'])

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
                        self.sim['Nstep'] = int(int(re.match(r'^No. Points:\s*(\d+).*', line).group(1)) / self.sim['Nline'])
                    if line.startswith("Plotname:"):
                        self.sim['Type'] = re.match(r'^Plotname:\s+(\S.*)$', line).group(1)
                        if self.sim['Type'].startswith("Tran"):
                            self.sim['Xlbl'] = "Time"
                        if self.sim['Type'].startswith("AC"):
                            self.sim['Xlbl'] = "Freq"
                        if self.sim['Type'].startswith("DC"):
                            self.sim['Xlbl'] = "DC"
                    if line.startswith("Abscissa:"):
                        pat = r'^Abscissa:\s+(\S+)\s+(\S+)\s*'
                        self.sim['Xmin'] = float(re.match(pat,line).group(1))
                        self.sim['Xmax'] = float(re.match(pat,line).group(2))
                    if flgv == 1 and self.sim['Type'].startswith("DC"):
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
                if self.sim['Type'].startswith("Tran") or self.sim['Type'].startswith("DC"):
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
                                
            return df
                        
    def comp2real(self, df, idx):
        for i in idx:
            df[i] = df[i].map(lambda x: (x).real)
    
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

        
    @classmethod
    def chdir(cls, dir):
        try: os.path.isdir(dir)
        except: print("No such directory:" + dir, file=sys.stderr) * exit()
        os.chdir(dir)
        cls.gpath['cwd'] = os.getcwd()

    def clean(self,suf):
        for s in suf:
            try: os.remove(self.path[s])
            except: print("Can't remove file:" + self.path[s], file=sys.stderr)
        self.tstime(suf)
        
