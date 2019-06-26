function [ time ] = outputTime( timestamp )
%This function ouputs just the time portion of the timestamp
hours=str2num(datestr(timestamp/86400+datenum(1970,1,1), 'HH'));
minutes=str2num(datestr(timestamp/86400+datenum(1970,1,1), 'MM'));
seconds=str2num(datestr(timestamp/86400+datenum(1970,1,1), 'ss'));
time=minutes+hours*60;
end

