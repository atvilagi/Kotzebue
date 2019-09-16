%%Function to sort data from text file into table
function M=readTempData(filename)
p=inputParser;
%read from text file
M=readtable(filename,'Delimiter','tab','ReadVariableNames',false);


%Set table property information
M.Properties.Description='ASOS Weather Data';
M.Properties.VariableNames{'Var1'}='Station';
M.Properties.VariableNames{'Var2'}='AkDatetime';
M.Properties.VariableNames{'Var3'}='Temperature';
M.Properties.VariableUnits={'' '' 'Fahrenheit'};

%verify input is properly formatted
addRequired(p, 'filename', @ischar)