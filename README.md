# PyQSPICE

***

![](images/SS.png)

***

## About PyQSPICE and QSPICE

The PyQSPICE is a Python package / class of wrapper script interface for the [QSPICE™](https://www.qorvo.com/design-hub/design-tools/interactive/qspice) - a SPICE circuit simulator - available from [Qorvo](https://www.qorvo.com) at no cost.

![](images/QSPICE.jpg)

The PyQSPICE invokes QSPICE executable files in a CUI (Charactor User Interface) manner.

* PyQSPICE executes simulations.
* PyQSPICE loads simulation results into Python memory for plotting.
* PyQSPICE expects QSPICE schematic (.qsch) or netlist (.cir) files prepared by users.
    * Using QSPICE GUI to capture schematics
    * Generate netlist files manually or programming manner

***

## Documents

[INSTALL.md](INSTALL.md) ::

Please start with this installation procedure of PyQSPICE environment.

[QuickStart.md](QuickStart.md) ::

From the end of INSTALL.md document, it continues to this quick start document.

Examples ::

* **DC** Simulation <br/>
  [tests/10_DC](tests/10_DC/10_DC.md) <br/>
  ==> JupyterLab file is **tests/10_DC/10_DC.ipynb**
* **AC** Simulation <br/>
  [tests/20_AC](tests/20_AC/20_AC.md) <br/>
  ==> JupyterLab file is **tests/20_AC/20_AC.ipynb**
* **AC, Nyquist Diagram**<br/>
  [tests/22_NyquistDia](tests/22_NyquistDia/22_NyquistDia.md) <br/>
  ==> JupyterLab file is **tests/22_NyquistDia/22_NyquistDia.ipynb**
* **TRAN** Simulation <br/>
  [tests/30_TRAN](tests/30_TRAN/30_TRAN.md) <br/>
  ==> JupyterLab file is **tests/30_TRAN/30_TRAN.ipynb**
* **Bode** Simulation <br/>
  [tests/40_Bode](tests/40_Bode/40_Bode.md) <br/>
  ==> JupyterLab file is **tests/40_Bode/40_Bode.ipynb**

***

## License and Availability

The PyQSPICE is under the [Qorvo software license](https://github.com/Qorvo/PyQSPICE/blob/13ae6387ef4619cf605c854739218b3d24db69d2/LICENSE),

and PyQSPICE is available from two (2) repositories at the [Qorvo@GitHub](https://github.com/Qorvo) and the [PyPI](https://pypi.org) 
* GitHub:  [https://github.com/Qorvo/PyQSPICE](https://github.com/Qorvo/PyQSPICE)
* PyPI:  [https://pypi.org/project/PyQSPICE](https://pypi.org/project/PyQSPICE)

