%%Function to convert Date Format from UnixTime to Coordinated Universal
%%Time (UTC)
%This function converts time recorded in a UNIX timestamp into UTC, the
%basis for civil time (Year, Month, Day, Time) by using the datestr and
%datenum functions inherent to MATLAb. 
%
%datestr converts the datetime numeric values to text representing dates
%and times in the format day-month-year hour:minute:second
%
%datenum converts the datetime values to serial date numbers
%
%Unix time is defined at the number of seconds elapsed since )0:00:00 UTC,
%January 1, 1970.
%
%This function takes a Unix timestamp in seconds as its input, divides this
%number by the number of seconds in a day, or $$60*60*24$$, adds this to
%the number of seconds accumulated since January 1,1970, and adjusts by 9
%hours for the Alaska Timezone. 
function U=UnixtoAKTime(x)
U=datestr(x/(60*60*24)+datenum(1970,1,1));