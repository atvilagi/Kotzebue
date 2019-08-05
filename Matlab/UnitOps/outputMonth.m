function [ date ] = outputMonth( timestamp )
%This function seperates the date from the timestamp 

date=str2num(datestr(timestamp/86400 +datenum(1970,1,1), 'mm'));

end
