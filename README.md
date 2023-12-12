# PyQSPICE

***

<a href="https://github.com/Qorvo/PyQSPICE"><img src="https://github.com/Qorvo/PyQSPICE/blob/be2fc3f600ba9d543223423d104355a425a8f0ec/images/SS.png?raw=True"  title="Example"></a>

***

## About PyQSPICE and QSPICE

The PyQSPICE is a Python package / class of wrapper script interface for the [QSPICE™](https://www.qspice.com/) - a SPICE circuit simulator - available from [Qorvo](https://www.qorvo.com) at no cost.

<a href="https://www.qspice.com/"><img src="https://www.qorvo.com/-/media/images/qorvopublic/news-item/20230725-qspice-pr-image-1500x1200.jpg"  title="QSPICE"></a>

The PyQSPICE invokes QSPICE executable files in a CUI (Charactor User Interface) manner.

* PyQSPICE executes simulations.
* PyQSPICE loads simulation results into Python memory for plotting.
* PyQSPICE expects QSPICE schematic (.qsch) or netlist (.cir) files prepared by users.
    * Using QSPICE GUI to capture schematics
    * Generate netlist files manually or programming manner

***

## Documents

[INSTALL.md](https://github.com/Qorvo/PyQSPICE/blob/main/INSTALL.md) ::

Please start with this installation procedure of PyQSPICE environment.

[QuickStart.md](https://github.com/Qorvo/PyQSPICE/blob/main/QuickStart.md) ::

From the end of INSTALL.md document, it continues to this quick start document.

Examples ::

* **DC** Simulation: [tests/10_DC](https://github.com/Qorvo/PyQSPICE/blob/main/tests/10_DC/README.md)<br/>
  ==> JupyterLab file is [tests/10_DC/README.ipynb](https://github.com/Qorvo/PyQSPICE/blob/main/tests/10_DC/README.ipynb)<br/>
<a href="https://github.com/Qorvo/PyQSPICE/blob/main/tests/10_DC/README.md"><img src="https://github.com/Qorvo/PyQSPICE/blob/be2fc3f600ba9d543223423d104355a425a8f0ec/images/output_DC_0.png?raw=True"  title="DC Simulation"></a>

* **AC** Simulation: [tests/20_AC](https://github.com/Qorvo/PyQSPICE/blob/main/tests/20_AC/README.md)<br/>
  ==> JupyterLab file is [tests/20_AC/README.ipynb](https://github.com/Qorvo/PyQSPICE/blob/main/tests/20_AC/README.ipynb)<br/>
<a href="https://github.com/Qorvo/PyQSPICE/blob/main/tests/20_AC/README.md"><img src="https://github.com/Qorvo/PyQSPICE/blob/be2fc3f600ba9d543223423d104355a425a8f0ec/images/output_AC_0.png?raw=True"  title="AC Simulation"></a>

* **AC, Nyquist Diagram**: [tests/22_NyquistDia](https://github.com/Qorvo/PyQSPICE/blob/main/tests/22_NyquistDia/README.md)<br/>
  ==> JupyterLab file is [tests/22_NyquistDia/README.ipynb](https://github.com/Qorvo/PyQSPICE/blob/main/tests/22_NyquistDia/README.ipynb)<br/>
<a href="https://github.com/Qorvo/PyQSPICE/blob/main/tests/22_NyquistDia/README.md"><img src="https://github.com/Qorvo/PyQSPICE/blob/be2fc3f600ba9d543223423d104355a425a8f0ec/images/output_Nyq_1.png?raw=True"  title="Nyquist Diagram"></a>
<a href="https://github.com/Qorvo/PyQSPICE/blob/main/tests/22_NyquistDia/README.md"><img src="https://github.com/Qorvo/PyQSPICE/blob/be2fc3f600ba9d543223423d104355a425a8f0ec/images/output_Nyq_0.png?raw=True"  title="Source Bode Plot for the Nyquist Diagram"></a>

* **TRAN** Simulation: [tests/30_TRAN](https://github.com/Qorvo/PyQSPICE/blob/main/tests/30_TRAN/README.md)<br/>
  ==> JupyterLab file is [tests/30_TRAN/README.ipynb](https://github.com/Qorvo/PyQSPICE/blob/main/tests/30_TRAN/README.ipynb)<br/>
<a href="https://github.com/Qorvo/PyQSPICE/blob/main/tests/30_TRAN/README.md"><img src="https://github.com/Qorvo/PyQSPICE/blob/be2fc3f600ba9d543223423d104355a425a8f0ec/images/output_TRAN_0.png?raw=True"  title="TRAN Simulation"></a>

* **Bode** Simulation: [tests/40_Bode](https://github.com/Qorvo/PyQSPICE/blob/main/tests/40_Bode/README.md)<br/>
  ==> JupyterLab file is [tests/40_Bode/README.ipynb](https://github.com/Qorvo/PyQSPICE/blob/main/tests/40_Bode/README.ipynb)<br/>
<a href="https://github.com/Qorvo/PyQSPICE/blob/main/tests/40_Bode/README.md"><img src="https://github.com/Qorvo/PyQSPICE/blob/be2fc3f600ba9d543223423d104355a425a8f0ec/images/output_Bode_0.png?raw=True"  title="Bode Plot"></a>

* **OP (Operating Point)** Simulation: [tests/50_OP](https://github.com/Qorvo/PyQSPICE/blob/main/tests/50_OP/README.md)<br/>
  ==> JupyterLab file is [tests/50_OP/README.ipynb](https://github.com/Qorvo/PyQSPICE/blob/main/tests/50_OP/README.ipynb)<br/>
<a href="https://github.com/Qorvo/PyQSPICE/blob/main/tests/50_Ope/README.md"><img src="https://github.com/Qorvo/PyQSPICE/blob/161ffda76e82bb9f601c78ca1ce960259178c286/images/50_OP.png?raw=True"  title="Operating Point"></a>

***

## License and Availability

The PyQSPICE is under the [Qorvo software license](https://github.com/Qorvo/PyQSPICE/blob/13ae6387ef4619cf605c854739218b3d24db69d2/LICENSE),

and PyQSPICE is available from two (2) repositories at the [Qorvo@GitHub](https://github.com/Qorvo) and the [PyPI](https://pypi.org) 
* GitHub:  [https://github.com/Qorvo/PyQSPICE](https://github.com/Qorvo/PyQSPICE)
* PyPI:  [https://pypi.org/project/PyQSPICE](https://pypi.org/project/PyQSPICE)

