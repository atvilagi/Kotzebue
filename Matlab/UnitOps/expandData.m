function [t ] = expandData( table)
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here
[m,n]=size(table);
t=zeros(m,1);

diff=table.Date_in_UnixTime_Format(m)-table.Date_in_UnixTime_Format(1);
disp(diff);
for a=1:diff
    t(a,1)=table.Date_in_UnixTime_Format(1)+(a-1);
end

for v=2:(m-1)
for x=(table.Date_in_UnixTime_Format(v)-table.Date_in_UnixTime_Format(1)):(table.Date_in_UnixTime_Format(v)-table.Date_in_UnixTime_Format(1))+(table.Date_in_UnixTime_Format(v+1)-table.Date_in_UnixTime_Format(v))
    t(x,2)=table.Flowrate(v);
%    t(x,3)=table.DD(v);
    t(x,3)=outputDate(t(x,1));
end
end

end

