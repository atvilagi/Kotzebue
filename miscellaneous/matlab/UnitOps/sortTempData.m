%%Function to sort data from text file into table
function T=sortTempData(filename)
p=inputParser;
%read from text file
M=readTempData(filename);

Day=datestr(datenum(M.AkDatetime,31),7);
Hour=datestr(datenum(M.AkDatetime,31),'HH');

N=table(Day,Hour);
T=[M N];

%verify input is properly formatted
addRequired(p, 'filename', @ischar)