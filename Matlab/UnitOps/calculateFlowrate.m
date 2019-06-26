function flowrate=calculateFlowrate(r, gallons,timestamp)
flowrate=zeros(r,1);
n=2;
while n<=r
    deltaV=gallons(n,:)-gallons((n-1),:);
    deltaT=timestamp(n,:)-timestamp((n-1),:);
    flowrate((n-1),:)=deltaV/deltaT*3600;
    n=n+1;
end
    
