%%Function to convert clicks to gallons per hour
%
%This function takes the "clicks" column from the stove struct,and 
%converts the number of clicks recorded into gallons per hour
%by prompting the user for the average rate of gallons per click for the
%particular unit, and then multiplies this number as a scalar against the
%input column. 
function x=calculateFuelConsumed(clicks,rate)
p=inputParser;

x=rate*clicks;

addRequired(p,'rate',@isscalar);