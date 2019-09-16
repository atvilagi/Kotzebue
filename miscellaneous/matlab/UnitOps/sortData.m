%%Function to sort data from text file into table
%This function take a text file as input and sorts it into the following
%columns: Date recorded in UnixTime Format, Boiler Status, Number of
%Recorded Clicks, Thermister Resistance, Calculated Temperature, Date in UTC format,
%Calculated Rate of Gallons/Hr, and Calculated BTU/Hr. The first four
%columns are based on gathered experimental data, the rest are calculated
%based on this information and related specifications unique to each fuel pump.
%Calculated data calls to the calculateTemperature, UnixtoUTC, and rateConversion functions. 
function t=sortData(filename)
p=inputParser;
%read from text file
M=dlmread(filename);

%move to own function
%get volume per click for this unit
[r,c]=size(M);
if (c-1)==5
    volumeRate=M(1,5);
else
    prompt='What is the flow rate for this unit?  ';
    volumeRate=input(prompt);
end

%move to own function
%get heater efficiency for this unit
if c==6
    efficiency=M(1,6);
else
    prompt='What is the efficiency for this unit?  ';
    efficiency=input(prompt);
end

Unitprompt='Heater type: ';
UnitSelected=input(Unitprompt);

%set desired columns
%Collected Data
c1=M(:,1);%Unix Timestamp
c2=M(:,2);%Boiler Status
c3=M(:,3);%Clicks
c4=M(:,4);%Thermister Resistance

%Calculated Data
c5=UnixtoUTC(c1);%UTC Timestamp
c6=UnixtoAKTime(c1);%UTC Timestamp adjusted for AK Timezone
c7=calculateTemperature(c4);%Temperature in Fahrenheit
c8=calculateFuelConsumed(c3,volumeRate);%Gallons of Fuel Consumed
c9=calculateFlowrate(r,c8,c1);%calculated rate of fuel consumption
c10=calculateHeatTransfer(c9,efficiency);

n=1;
while n<=r
    c11(n)=determineStatus(c2(n),UnitSelected);
    
    n=n+1;
end


%Sort data as struct, and then transform into a table
s=struct('Date_in_UnixTime_Format',c1,'Boiler_Status',c2,'Clicks',c3,'Thermister_Resistance',c4,'Date_UTC_Format',c5,'Date_AK_Time_Format',c6,'Calculated_Temperature',c7,'Fuel_Consumed',c8,'Flowrate',c9,'Heat_Transfer',c10,'DD',outputDate(c1),'Time',outputTime(c1),'MM',outputMonth(c1),'Theoretical_Fuel_Consumption',c11.');
t=struct2table(s);

%Set table property information
t.Properties.Description='Unit Deployment Data and Calculated Properties';
%t.Properties.VariableDescriptions={'Unix Timestamp' '0=high 1=high-medium 2=low-medium 3=low 4=heater off 5=monitor on' '' '' '' 'Adjusted for AK Timezone' 'Based on Steinhart-Hart Equation' 'Calculated from approximate volume per stroke and number of clicks' 'Interpolated from timestamp and calculated volume' 'Based on No.2 Fuel Oil LHV=137,000 BTUs' '' '' ''};
%t.Properties.VariableUnits={'' '' '' 'ohms' '' '' 'Fahrenheit' 'Gallons' 'Gallons/hr' 'BTUs/hr' '' '' ''};

%verify input is properly formatted
addRequired(p, 'filename', @ischar)
