# Metrics
## Heat Degree Day (hdd)
HDD a base value minus the mean of the daily high and low temperature. The base value is 65 and all temperatures are assumed to be in Fahrenheit. Current external temperature values come from SNOTEL.

## Days Monitored
Days monitored is a summary of the actual amount to time that data was being collected. It is calculated by summing the total time per day, over the report period. The returned metric is both in time delta and rounded to total days. To counted as a full day a there must be at least 6 hours of data.

## Total Gallons
The total gallons for a report time period OR if data is missing (Days Monitored is less than report time period) interpolation is used. If there is a hdd value for each day in the report period (no missing outside temperature data) then the fuel consumption for missing data days is calculated as the average gallons per hdd * the hdd for that day. If hdd is also missing then the average gallons per day is used to fill in missing values. 

## Consumption per Area
Consumption per area is calculated as total gallons / house area in square feet. An alternative and more statistically appropriate method would be to use the average gph / by square feet  * timespan of the dataset. This would provide a method for also getting standard error and confidence intervals for comparision with other house holds or neightborhoods.

## Total Cost
Total cost is calculated as the total gallons * price of fuel. Price of fuel is manually entered when the report is produced. 

## Average Gallons per Day
Average gallons per day is calculated by taking the mean of the sum of fuel consumed each day.

## Average Cost per Day 
Average cost per day is calculated by multiplying average gallons per day * price of fuel. Price of fuel is manually entered when the report is produced. 

## Average Indoor Temperature
Average indoor temperature is the average of all indoor temperature values collected at timed intervals for the duration of the report. If data is missing, this average is based on the available data. Temperature is in Fahrenheit and calcuated based on thermistor value.

## Average Outdoor Temperature 
Average outdoor temperature is the average of all outdoor temperature values collected at timed intervals for the duration of the report. If data is missing, this average is based on the available data. Temperature is in Fahrenheit and downloaded as hourly data from aoos_snotel.

## Hourly Fuel Consumption Rate
Hourly fuel consumption rate is the average gallons per hour for each hour of the day (0-23) for the entire report period. If data is missing these averages are calcuated based on the available data. 

## Gallons per HDD
Gallons per heat degree day is calculated as the mean of (fuel consumption per day (in gallons) / the HDD for that day) for all data during the report period. If days are missing either HDD or fuel consumption they are not used in the calculation. 