%Function to calculate percent error
function PercentError=calculatePercentError(theoreticalValue, experimentalValue)

PercentError=(theoreticalValue-experimentalValue)/theoreticalValue;