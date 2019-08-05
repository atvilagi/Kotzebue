function [ off ] = offTime( r,flowrate,timestamp )
%Compute the amount of time the heater is off
off=zeros(r,1);
n=1;
while n<r
    if flowrate(n,:)<1.0E-4
        off(n,1)=calculateOffTime(timestamp((n),:),timestamp(n+1,:));
    else
        off(n,1)=0;
    end
    n=n+1;
end
