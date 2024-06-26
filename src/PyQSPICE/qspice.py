import sys
import subprocess
import codecs
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
	verstr = "2024.05.14"

## Global (Class) Path Information
	gpath = {}
	gpath['cwd'] = os.getcwd()
	gpath['home'] = expanduser("~")
	usrp = gpath['home'] + "/QSPICE/"
	sysp = r"c:/Program Files/QSPICE/"

	for exe in ['QUX', 'QSPICE64', 'QSPICE80']:
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

		self.sim = {"label": 'default', "labels": ['default'], "Nline": 4999, "Nstep": 0, "Nbit": 64}

		self.path['user'] = fname
		self.path['base'] = fname.removesuffix('.qsch').removesuffix('.qraw').removesuffix('.cir')
		clsQSPICE.tstime(self, ['qsch', 'qraw', 'cir', 'utf8'])

# How many data points to read from QRAW simulation result files
# Too small, too zigzag; too big, too slow ☹    
	def setNline(self, i):
		self.sim['Nline'] = i

	def setNbit(self, i):
		if (i == 64) or (i == 80):
			self.sim['Nbit'] = i

	def selectSimLabel(self, label, Nline = -999, Nbit = -999):
		self.sim['label'] = label
		if Nline != -999: (self.sim['label=' + label])['Nline'] = Nline
		if (Nbit == 64) or (Nbit == 80):
			(self.sim['label=' + label])['Nbit'] = str(Nbit)

    # Generate a netlist CIR file from the source schematic QSCH file
	def qsch2cir(self):
		if self.ts['qsch']:
			with open(self.path['cir'], "w") as ofile:
				subprocess.run([self.gpath['QUX'], "-Netlist", self.path['qsch'], "-stdout"], stdout=ofile)
				clsQSPICE.tstime(self, ['cir'])
			with codecs.open(self.path['cir'], 'r', 'latin_1') as ifile:
				lines = ifile.read()
			with codecs.open(self.path['utf8'], 'w', 'utf_8') as ofile:
				ofile.write(lines)
				clsQSPICE.tstime(self, ['utf_8'])

	def opt4SEPIA(self, cir, prnPeak = False, Verbose = False, fnTran0 = "", fnTran1 = "", fnAC0 = "", fnAC1 = "", fnLog = "", runTran0 = False, runTran1 = False, runAC0 = False, runAC1 = False, log = False):
		options = ""	
		if prnPeak: options += "p"
		if Verbose: options += "v"
		if fnLog != "":  options += "l" + fnLog + ":"
		elif log:        options += "l" ":"
		if fnTran0 != "":
			options += "t0" + fnTran0
			if runTran0: options += "/"
			else:        options += ":"
		if fnTran1 != "":
			options += "t1" + fnTran1
			if runTran1: options += "/"
			else:        options += ":"
		if fnAC0 != "":
			options += "a0" + fnAC0
			if runAC0:   options += "/"
			else:        options += ":"
		if fnAC1 != "":
			options += "a1" + fnAC1
			if runAC1:   options += "/"
			else:        options += ":"
		options += "x"

		lines = ""
		with open(cir, encoding='SJIS') as f:
			for line in f:
				line = line.rstrip('\r\n')
				line = re.sub(r"char\* Opt=.*\s*$", "char* Opt=" + options, line)
				lines = lines + line + "\n"
		with open(cir, mode="w", encoding='SJIS') as f:
			f.write(lines)

	def cir4label(self, label = 'simulation_label'):
		if label == 'simulation_label': return

		in_label = ""
		lines = ""

		with open(self.path['cir'], encoding='SJIS') as f:
			for line in f:
				line = line.rstrip('\r\n')
				if ret := re.match(r'^\*\s*PyQSPICE\s+(\S+)\s+end\s*', line):
					in_label = ""
				if ret := re.match(r'^\*\s*PyQSPICE\s+(\S+)\s+begin\s*', line):
					in_label = ret.group(1)
					if re.match(label, in_label, flags=re.IGNORECASE):
						line = r'*' + line
						in_label = label
					else:
						in_label = "other"
				if in_label != "":
					if in_label == label:
						line = re.sub(r"^\*(.*)$", r"\1", line)
					else:
						line = re.sub(r"^\.(.*)$", r"*.\1", line)
				lines = lines + line + '\n'

		ofile = self.path['base'] + "." + label + ".cir"
		with open(ofile, 'w') as f:
			f.write(lines)
			clsQSPICE.tstime(self, [label + '.cir'])

		self.sim['label=' + label] = {'label': label, 'Nline': self.sim['Nline'], 'Nbit': self.sim['Nbit']}
		self.sim['labels'] += [label]

# Run a simulation from the netlist CIR file
	def cir2qraw(self, label = ""):
		if self.sim['label'] != 'default': label = self.sim['label']
		if label == "":
			add = ""
			bit = str(self.sim['Nbit'])
		else:
			add = label + "."
			bit = str(self.sim['label=' + label]['Nbit'])
		if self.ts[add + 'cir']:
			subprocess.run([self.gpath['QSPICE' + bit], self.path[add + 'cir']])
			clsQSPICE.tstime(self, [add + 'qraw'])

	def copy2qraw(self, label = ""):
		if self.sim['label'] != 'default': label = self.sim['label']
		if label == "":  add = ""
		else:           add = label + "."
		clsQSPICE.tstime(self, [add + 'qraw'])


# Load simulation result signals from the simulation results QRAW file
# Input:  Array of signal strings in the way you specify in ".PLOT" statement
# Output:  It returns Pandas DataFrame
#  ==> Pandas supports data loading from the STDOUT-STDIN PIPE/stream (where the Numpy doesn't...temporary file needed)
	def LoadQRAW(self, probe, label = "", Nline = -999):
		if self.sim['label'] != 'default':
			label = self.sim['label']
			Nline = (self.sim['label=' + label])['Nline']
		if label == "":  add = ""
		else:           add = label + "."
		if Nline == -999: Nline = self.sim['Nline']
		if self.ts[add + 'qraw']:
			plots = ",".join(probe)
			with subprocess.Popen([self.gpath['QUX'], "-Export", self.path[add + 'qraw'], plots, str(Nline), "SPICE", "-stdout"], stdout=subprocess.PIPE, text=True) as qux:
				flgv = 0
				while True:
					line = qux.stdout.readline()
					if line == '\n': continue        
					if line.startswith("Values:"): break
					if line.startswith("No. Points:"):
						self.sim['Nstep'] = int(int(re.match(r'^No. Points:\s*(\d+).*', line).group(1)) / (Nline + 1))
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

			with subprocess.Popen([self.gpath['QUX'], "-Export", self.path[add + 'qraw'], plots, str(Nline), "CSV", "-stdout"], stdout=subprocess.PIPE, text=True) as qux:

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
					tmp = tmp + ([i] * (Nline + 1))

				df["Step"] = tmp
				if self.sim['Nstep'] > 1:
					try: os.path.isfile(self.path[add + 'cir'])
					except:
						if not os.path.isfile(self.path['cir']): self.qsch2cir()
						if label != "": self.cir4label(label)
					with open(self.path[add + 'cir']) as f:
						for line in f:
							if re.match(r'^\.(step|STEP)', line):
								try: self.sim["StepInfo"]
								except: self.sim["StepInfo"] = ""
								self.sim["StepInfo"] = self.sim["StepInfo"] + line
				else:
					self.sim["StepInfo"] = "N/A"
					
				if self.sim['label'] != 'default':
					(self.sim['label=' + label])['Nstep'] = self.sim['Nstep']
					(self.sim['label=' + label])['Type']  = self.sim['Type']
					(self.sim['label=' + label])['Xlbl']  = self.sim['Xlbl']
					(self.sim['label=' + label])['Xmin']  = self.sim['Xmin']
					(self.sim['label=' + label])['Xmax']  = self.sim['Xmax']
					(self.sim['label=' + label])['StepInfo'] = self.sim['StepInfo']
					
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

# Calculate absolute value of the "target", also colculate argument of the "target"
# If strings specified, it also extrace real and imaginary part of the "target"
# Further-If "-1" specified, returns real and imaginary part of the "target" with 180 degree rotated.
# NOTE: apply() method returns new DataFrame object, so it returns this new object
	def ImpePhase(self, df, target, strabs, strarg, strre="none", strim="none", sign=1):
		def Calc(row):
			row[strabs] = abs(row[target])
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
				line = line.rstrip('\r\n')
				if ret := re.match(two, line, flags=re.IGNORECASE):
					node[ret.group(2)] = 0
					node[ret.group(3)] = 0
					self.elem[ret.group(1)] = clsQSPICE._engSuf(ret.group(4))
					self.ele2.append(ret.group(1))
				if ret := re.match(three, line, flags=re.IGNORECASE):
					node[ret.group(2)] = 0
					node[ret.group(3)] = 0
					node[ret.group(4)] = 0
					self.elem[ret.group(1)] = ret.group(5) # model name
					if re.match(r"^[JZ]", line, flags=re.IGNORECASE):
						self.eleT.append(ret.group(1))
				if ret := re.match(four, line, flags=re.IGNORECASE):
					node[ret.group(2)] = 0
					node[ret.group(3)] = 0
					node[ret.group(4)] = 0
					node[ret.group(5)] = 0
					self.elem[ret.group(1)] = ret.group(6) # To be updated later
					if re.match(r"^[EGS]", line, flags=re.IGNORECASE):
						self.ele2.append(ret.group(1))
					if re.match(r"^[MQ]", line, flags=re.IGNORECASE):
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
	def PrepFreqGainPlot(self, ax, xlbl="", ylbl="", xlim=[], ylim=[], ttl=""):
		self.__PrepFreqPlot(ax, xlbl, ylbl, xlim, ylim, ttl)
		if len(ylim) == 2: ax.set_ylim(ylim[0],ylim[1])

# Matplotlib Preparing a Plot for Frequency-Impedance
	def PrepFreqImpePlot(self, ax, xlbl="", ylbl="", xlim=[], ylim=[], ttl=""):
		self.__PrepFreqPlot(ax, xlbl, ylbl, xlim, ylim, ttl)
				
		limpe = pd.DataFrame({
#            "v": [1e-6, 1e-5, 1e-4,  1e-3, 1e-2, 1e-1, 1,   10,  100,  1e3, 1e4,  1e5,   1e6],
			"v": [-120, -100, -80,   -60,  -40,  -20,   0,  20,  40,   60,  80,   100,   120],
			"l": ["1μ", "10μ","100μ","1m", "10m","100m","1","10","100","1k","10k","100k","1M"],
		})
		if len(ylim) == 2:  min, max = ylim[0], ylim[1]
		if ylim == "auto":  min, max = (ax.get_ylim())[0], (ax.get_ylim())[1]
		if "min" in locals():
			if (int(min/20)*20) == min:
				rmin = min
			else:
				rmin = (int(min/20)-1)*20
			if (int(max/20)*20) == max:
				rmax = max
			else:
				rmax = (int(max/20)+1)*20
			ly = limpe[(limpe.v >= rmin) & (limpe.v <= rmax)].reset_index(drop=True)
			ax.set_ylim(ly.iat[0,0],ly.iat[-1,0])
			ax.set_yticks(ly.loc[:,"v"],ly.loc[:,"l"])

	def __PrepFreqPlot(self, ax,  xlbl="", ylbl="", xlim=[], ylim=[], ttl=""):
		ax.set_xscale('log')
		ax.grid(which='major', linewidth="0.5")
		ax.grid(which='minor', linewidth="0.35")
		if ttl != "": ax.set_title(ttl)
		if xlbl != "": ax.set_xlabel(xlbl)
		if ylbl != "": ax.set_ylabel(ylbl)

		lfreq = pd.DataFrame({
			"f": [1e-18, 1e-17, 1e-16, 1e-15, 1e-14, 1e-13, 1e-12, 1e-11, 1e-10, 1e-9, 1e-8, 1e-7,  1e-6, 1e-5, 1e-4,  1e-3, 1e-2, 1e-1,  1,   10,   100,  1e3, 1e4,  1e5,   1e6, 1e7,  1e8,   1e9],
			"l": ["1a",  "10a", "100a","1f",  "10f", "100f","1p",  "10p", "100p","1n", "10n","100n","1μ", "10μ","100μ","1m", "10m","100m","1", "10", "100","1k","10k","100k","1M","10M","100M","1G"],
		})
		if len(xlim) == 2:  lf = lfreq[(lfreq.f > (xlim[0]/10)) & (lfreq.f < (xlim[1]*10))].reset_index(drop=True)
		if xlim == "auto":  lf = lfreq[(lfreq.f > (self.sim["Xmin"]/10)) & (lfreq.f < (self.sim["Xmax"]*10))].reset_index(drop=True)
		if "lf" in locals():
			ax.set_xlim(lf.iat[0,0],lf.iat[-1,0])
			ax.set_xticks(lf.loc[:,"f"],lf.loc[:,"l"])

# Matplotlib Preparing a Plot for Time Domain
	def PrepTimePlot(self, ax, xlbl="", ylbl="", xlim=[], ylim=[], ttl=""):
		ax.grid(which='major', linewidth="0.5")
		ax.grid(which='minor', linewidth="0.35")
		if ttl != "": ax.set_title(ttl)
		
		if ylbl != "": ax.set_ylabel(ylbl)
		if len(ylim) == 2: ax.set_ylim(ylim[0],ylim[1])
			
		if len(xlim) == 2: min, max = xlim[0], xlim[1]
		if xlim == "auto": min, max = (ax.get_xlim())[0], (ax.get_xlim())[1]
		if "min" in locals():
			uni = self.__timeP(ax, min, max)
		if xlbl != "": ax.set_xlabel(xlbl + f" ({uni})")
			
	def __timeP(self, ax, a, b):
		tsu = pd.DataFrame({
			"v": [1e-15,1e-12,1e-9, 1e-6, 1e-3, 1,   1e3],
			"l": ["fs", "ps", "ns", "μs", "ms", "s", "×1000 s"],
		})

		bin = [0.2, 0.4, 0.8, 1, 2, 4, 5, 10, 12, 16, 20, 24, 30, 40, 50, 60, 75, 80, 100]

		pdic = {
			0.2: [0,  0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
			0.4: [0,  0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
			0.8: [0,  0.2, 0.4, 0.6, 0.8, 1.0, 1.2],
			1:  [0,  0.2, 0.4, 0.6, 0.8, 1],
			2:  [0,  0.5,  1,  1.5,  2],
			4:  [0,  1,  2,  3,  4],
			5:  [0,  1,  2,  3,  4, 5],
			10: [0,  2,  4,  6,  8, 10],
			12: [0,  2,  4,  6,  8, 10, 12],
			16: [0,  2,  4,  6,  8, 10, 12, 14, 16],
			20: [0,  2,  4,  6,  8, 10, 12, 14, 16, 18, 20],
			24: [0,  4,  8, 12, 16, 20, 24],
			30: [0,  5, 10, 15, 20, 25, 30],
			40: [0,  5, 10, 15, 20, 25, 30, 35, 40],
			50: [0,  5, 10, 15, 20, 25, 30, 35, 40, 45, 50],
			60: [0, 10, 20, 30, 40, 50, 60],
			75: [0, 15, 30, 45, 60, 75],
			80: [0, 10, 20, 30, 40, 50, 60, 70, 80],
			100:[0, 10, 20, 30, 40, 50, 60, 70, 80, 90,100],
		}

		rdic = {}
		for i in pdic.keys():
			t = list(reversed(pdic[i]))
			rdic[-i] = [n * -1 for n in t]

		d = round(b - a, 6)

####
#       (k,l) = tsu[tsu.v < d].tail(1).reset_index(drop=True).iloc[0,:]
####
		if abs(a) > abs(b): dd = abs(a)
		else:               dd = abs(b)
		
		(k,l) = tsu[tsu.v < dd].tail(1).reset_index(drop=True).iloc[0,:]
####
		m = 1
		if round(d/k, 6) > 10: m = 10
		if round(d/k, 6) > 100:  m = 100
		mk = m * k

		p = [n for n in bin if round(d*10 /mk, 6) <= n][0]

		#print(f"min: {a/k} {l}, max: {b/k} {l}, range: {p}, scale: x{m}")

		pos, rev = pdic[p], rdic[-p]
		aT, bT = round(a*10 /mk, 6), round(b*10 /mk, 6)

		if (a < 0) & (b > 0):
			if aT in rev:
				aR = aT
			else:
				aR = [n for n in rev if n < aT][-1]
			if bT in pos:
				bR = bT
			else:
				bR = [n for n in pos if n > bT][0]        
			res = [n for n in rev if n >= aR and n < 0] + [n for n in pos if n <= bR]

		elif (a == 0) & (b > 0):
			if bT in pos:
				bR = bT
			else:
				bR = [n for n in pos if n > bT][0]
			res = [n for n in pos if n <= bR]
		
		elif (a < 0) & (b == 0):
			if aT in rev:
				aR = aT
			else:
				aR = [n for n in rev if n < aT][-1]
			res = [n for n in rev if n >= aR]

		elif b < 0:
			c = rev[1] - rev[0]
			offs = int(bT / c) * c
			rev = [n + offs for n in rev]
		
			if aT in rev:
				aR = aT
			else:
				aR = [n for n in rev if n > aT][0]
			#print(f"a = {a}, at = {aT}, ar = {aR}, b = {b}, bT = {bT}, offs = {offs}, {rev}")
			res = [n for n in rev if n >=aR]
		
		elif a > 0:
			c = pos[1] - pos[0]
			offs = int(round(aT / c, 6)) * c
			pos = [n + offs for n in pos]
		
			if bT in pos:
				bR = bT
			else:
				bR = [n for n in pos if n > bT][0]
			#print(f"a = {a}, aT = {aT}, b = {b}, bT = {bT}, br = {bR}, offs = {offs}, {pos}")
			res = [n for n in pos if n <=bR]
		
		def _fmt(n, m):
			if p < 10: text = f"{n/10 *m:,.2f}"
			else:      text = f"{n/10 *m:,.1f}"
			while True:
				if ("." in text and text[-1] == "0") or (text[-1] == "."):
					text = text[:-1]
					continue
				break
			return text

		val = [round(n/10 * mk,6) for n in res]
		if m == 1:
			lbl = [_fmt(n, m) for n in res]
		if m > 1:
			lbl = [f"{int(n/10 *m):,}" for n in res]
			
		ax.set_xlim(val[0], val[-1])
		#print("MMM")
		#print(val)
		#print("MMM")
		#print(lbl)
		#print("MMM")
		ax.set_xticks(val, lbl)
		return l
		

# Matplotlib Preferences
#   Font for Rounded Noto
#   Style for "ggplot"
	def InitPlot(self):
		sfile = self.gpath['home'] + "/.config/matplotlib/ggplot_mod.mplstyle"
		if os.path.exists(sfile): mpl.rc_file(sfile)
		sfile = "./my.mplstyle"
		if os.path.exists(sfile): mpl.rc_file(sfile)

		fe = None
		mfont = self.gpath['home'] + "/.config/matplotlib/ResourceHanRoundedJP-Medium.ttf"
		if os.path.exists(mfont): fe = fm.FontEntry(fname=mfont, name="Resource Han Rounded JP Medium")
		mfont = self.gpath['home'] + "/.config/matplotlib/GenJyuuGothicL-Medium.ttf"
		if os.path.exists(mfont): fe = fm.FontEntry(fname=mfont, name="GenJyuuGothicL Medium")
		if fe:
			fm.fontManager.ttflist.insert(0,fe)
			mpl.rcParams['font.family'] = fe.name

