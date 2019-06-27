#Python script to take the unified PuMA netCDF4 file and extract particular stoves into a product file with a specific yaml file

#Created: Thu Jun 20 20:48:05 2019
#By: Douglas Keller

import yaml
from netCDF4 import Dataset

unified_file = Dataset('../Data/puma_unified_data.nc','r') #Opening the central unified data
product_file = Dataset('../Data/puma_product_data.nc','w',format='NETCDF4') #Opening the output file

inv_file = input('Input the name of the inventory file for the data subset: ') #Asks for the user to input the name of the new yaml file with the particular inventory
file = open('../PuMA_Inventory/'+inv_file,'r') #Opening the inventory file of the stoves in the project
yams = yaml.load(file)
file.close()

stoves = [] #Making a list of the stove names
for stove in yams:
    stoves.append(stove)

for stove in stoves:
    
    product_file.createGroup(stove) #Creating a netCDF4 group for each stove
    
    product_file[stove].description = 'Stove type: ' + yams[stove]['Stove Type'] #Labelling the stove type
    product_file[stove].createDimension('location',1) #Creating dimensions for the variables to depend on
    product_file[stove].createDimension('time',None)
    
    product_file[stove].createVariable('lat','f4',('location')) #Creating the variables for the data collected
    product_file[stove].createVariable('lon','f4',('location'))    
    product_file[stove].createVariable('time','f8',('time'))
    product_file[stove].createVariable('state','i4',('time'))
    product_file[stove].createVariable('clicks','i4',('time'))
    product_file[stove].createVariable('fuel_consumption','f8',('time'))
    product_file[stove].createVariable('fuel_consumption_rate','f8',('time'))
    product_file[stove].createVariable('indoor_temp','f4',('time'))
    product_file[stove].createVariable('outdoor_temp','f4',('time'))
    product_file[stove].createVariable('delta_temp','f4',('time'))
    
    product_file[stove]['lat'].description = 'Latitude of the PUMA device location' #Creating descriptions and units in the netCDF4 file to make it more portable
    product_file[stove]['lon'].description = 'Longitude of the PUMA device location'
    product_file[stove]['time'].description = 'Timestamp of each PUMA device reading'
    product_file[stove]['time'].units = 'Time since 1970, 1, 1, 00:00:00 UTC (Unix time)'
    product_file[stove]['state'].description = 'State of the stove when powered on; depends on the stove type the PUMA device is attached to'
    product_file[stove]['state'].units = 'Integer units corresponding to power states; -1 indicates powered off'
    product_file[stove]['clicks'].description = 'Number of clicks the fuel pump solenoid makes when the stove turns on'
    product_file[stove]['clicks'].units = 'Number of clicks; -1 indicates stove powered off'
    product_file[stove]['fuel_consumption'].description = 'The amount of fuel consumed by the stove'
    product_file[stove]['fuel_consumption'].units = 'US gallons'
    product_file[stove]['fuel_consumption_rate'].description = 'The fuel consumption rate of the stove'
    product_file[stove]['fuel_consumption_rate'].units = 'US gallons per hour'
    product_file[stove]['indoor_temp'].description = 'Indoor temperature read by the thermistor monitored by the PUMA device'
    product_file[stove]['indoor_temp'].units = 'F'
    product_file[stove]['outdoor_temp'].description = 'Outdoor temperature interpolated using area temperature data from Snotel'
    product_file[stove]['outdoor_temp'].units = 'F'
    product_file[stove]['delta_temp'].description = 'Temperature difference between the indoor and outdoor temperatures'
    product_file[stove]['delta_temp'].units = 'F'
        
    product_file[stove]['lat'][:] = yams[stove]['Location'][0] #Filling the variables
    product_file[stove]['lon'][:] = yams[stove]['Location'][1]
    product_file[stove]['time'][:] = unified_file[stove]['time'][:]
    product_file[stove]['state'][:] = unified_file[stove]['state'][:]
    product_file[stove]['clicks'][:] = unified_file[stove]['clicks'][:]
    product_file[stove]['fuel_consumption'][:] = unified_file[stove]['fuel_consumption'][:]
    product_file[stove]['fuel_consumption_rate'][:] = unified_file['fuel_consumption_rate'][:]
    product_file[stove]['indoor_temp'][:] = unified_file[stove]['indoor_temp'][:]
    product_file[stove]['outdoor_temp'][:] = unified_file[stove]['outdoor_temp'][:]
    product_file[stove]['delta_temp'][:] = unified_file[stove]['delta_temp'][:]
    
product_file.close() #Closing the netCDF4 file and you're done!