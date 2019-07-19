#Python script to take the unified PuMA netCDF4 file and extract particular stoves into a product file with a specific yaml file

#Created: Thu Jun 20 20:48:05 2019
#By: Douglas Keller

import yaml
from netCDF4 import Dataset
import os
import puma_data as pdata

def uni_nc2prod_nc():
    
    file_path = os.path.abspath(os.path.dirname(__file__))
    
    uni_nc = os.path.join(file_path,'..','Data','netCDF_Files','puma_unified_data.nc')
    unified_file = Dataset(uni_nc,'r') #Opening the central unified data
    
    new_nc = input('Input the name of the new netCDF file with the packaged data: ')
    prod_nc = os.path.join(file_path,'..','Data','netCDF_Files',new_nc)
    product_file = Dataset(prod_nc,'w',format='NETCDF4') #Opening the output file
    
    prod_nc_att = {'Contents':'netCDF file that contains the stoves in the fuel meter project, found in individual groups','Variables':'variables in each stove group are: time, cumulative clicks, clicks per interval, fuel consumption per interval, fuel consumption rate per interval, indoor temperature, outdoor temperature, temperature difference, stove status per interval'}
    product_file.setncatts(prod_nc_att)
    
    inv_file = input('Input the name of the inventory file for the data subset: ') #Asks for the user to input the name of the new yaml file with the particular inventory
    yaml_file = os.path.join(file_path,'..','Data','yaml_Files',inv_file)
    file = open(yaml_file,'r') #Opening the inventory file of the stoves in the project
    yams = yaml.load(file)
    file.close()
    
    name_list = [] #Making a list of the stove names
    for i in yams:
        name_list.append(i)
    
    new_nc = os.path.join(file_path,'..','Data','netCDF_Files','puma_unified_data.nc')
        
    stoves = [] #Making a list of the stove names
    for stove in yams:
        stoves.append(stove)
    
    for stove in stoves:
        
        product_file.createGroup(stove) #Creating a netCDF4 group for each stove
        
        product_file[stove].createDimension('time',None)
        
        product_file[stove].setncattr('Location',unified_file[stove].getncattr('Location'))
        product_file[stove].setncattr('Stove Type',unified_file[stove].getncattr('Stove Type'))
        product_file[stove].createVariable('time','f8',('time'))
        product_file[stove].createVariable('state','i4',('time'))
        product_file[stove].createVariable('clicks','i8',('time'))
        product_file[stove].createVariable('cumulative_clicks','i8',('time'))
        product_file[stove].createVariable('fuel_consumption','f8',('time'))
        product_file[stove].createVariable('fuel_consumption_rate','f8',('time'))
        product_file[stove].createVariable('indoor_temp','f4',('time'))
        product_file[stove].createVariable('outdoor_temp','f4',('time'))
        product_file[stove].createVariable('delta_temp','f4',('time'))
        
        product_file[stove]['time'].description = 'Timestamp of each PUMA device reading' #Creating descriptions and units in the netCDF4 file to make it more portable
        product_file[stove]['time'].units = 'Time since 1970, 1, 1, 00:00:00 UTC (Unix time)'
        product_file[stove]['state'].description = 'State of the stove when powered on; depends on the stove type the PUMA device is attached to'
        product_file[stove]['state'].units = 'Integer units corresponding to power states; -1 indicates powered off'
        product_file[stove]['clicks'].description = 'Number of clicks the fuel pump solenoid makes when the stove turns on per time interval'
        product_file[stove]['clicks'].units = 'Number of clicks'
        product_file[stove]['cumulative_clicks'].description = 'Number of cumulative clicks since PuMA installation the fuel pump solenoid makes when the stove turns on'
        product_file[stove]['cumulative_clicks'].units = 'Number of cumulative clicks; -1 indicates stove powered off'
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
    
        product_file[stove]['time'][:] = unified_file[stove]['time'][:]
        product_file[stove]['state'][:] = unified_file[stove]['state'][:]
        product_file[stove]['clicks'][:] = unified_file[stove]['clicks'][:]
        product_file[stove]['cumulative_clicks'][:] = unified_file[stove]['cumulative_clicks'][:]
        product_file[stove]['fuel_consumption'][:] = unified_file[stove]['fuel_consumption'][:]
        product_file[stove]['fuel_consumption_rate'][:] = unified_file[stove]['fuel_consumption_rate'][:]
        product_file[stove]['indoor_temp'][:] = unified_file[stove]['indoor_temp'][:]
        product_file[stove]['outdoor_temp'][:] = unified_file[stove]['outdoor_temp'][:]
        product_file[stove]['delta_temp'][:] = unified_file[stove]['delta_temp'][:]
        
    product_file.close() #Closing the netCDF4 file and you're done!
    
pdata.uni_nc2prod_nc()