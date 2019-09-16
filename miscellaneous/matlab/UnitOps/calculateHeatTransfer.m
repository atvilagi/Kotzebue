%Calculate BTU/hr. Heating Value is based on LHV Enginering ToolBox value 
%"Fuel Oil and Combustion Values." Fuel Oil and Combustion Values.
%Engineering ToolBox, n.d. Web. 17 June 2016.
%<http://www.engineeringtoolbox.com/fuel-oil-combustion-values-d_509.html>. 
function HT=calculateHeatTransfer(flowrate, efficiency)
%Lower Heating Value of Fuel No 2
HV=137000;

HT=HV*flowrate*efficiency;