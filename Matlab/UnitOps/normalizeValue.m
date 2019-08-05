function normalizedPoint=normalizeValue(data)
xMax=max(data);
xMin=min(data);

[m,n]=size(data);
normalizedPoint=zeros(m,1);

i=1;
while i<=m 
    normalizedPoint(i)=(data(i)-xMin)/(xMax-xMin);
    i=i+1;
end