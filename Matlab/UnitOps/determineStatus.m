%function to determine which theoretical Fuel Consumption rate to call
%based on boiler status 
function theoreticalFuelConsumption=determineStatus(boilerStatus, Unit)

StoveFuelConsumption=readtable('FuelConsumption.txt','ReadRowName',true);
switch boilerStatus
    case 0
        theoreticalFuelConsumption=StoveFuelConsumption.High({Unit});
    case 1
        theoreticalFuelConsumption=StoveFuelConsumption.HighMedium({Unit});
    case 2
        theoreticalFuelConsumption=StoveFuelConsumption.LowMedium({Unit});
    case 3
        theoreticalFuelConsumption=StoveFuelConsumption.Low({Unit});
    otherwise
        theoreticalFuelConsumption=0;
end