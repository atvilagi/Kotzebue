#A windows safe python script for collating the ACEP PuMA stove project data; it requires the accompanying doug_puma.py file to run the functions this script depends on

#Created: Tue Jun 18 23:56:10 2019
#By: Douglas Keller

def dir2data_mp(air_temp_file): #This runs the file2data_mp function for each month directory in the yearly stove datasets

    if __name__ == '__main__': #This makes the multiprocessing module safe for Windows to use (other OS don't require it to run properly)

        file_list = [] #Making a list of the file names in each directory, only adding the text files, excluding the log.txt files
        for file in os.listdir():
            if file.endswith('.txt'):
                if not file.endswith('LOG.txt'):
                    file_list.append(file)
        file_list.sort()
        
        result = mp.Manager().Queue() #Instantiating a multiprocess safe buffer (needed for multiprocessing)
        pool = mp.Pool(mp.cpu_count()) #Making a pool of processes (think of it as other initializations of python each running its own program)
        for file in file_list:
            pool.apply_async(puma.file2data,args=(file,air_temp_file,result)) #Asynchronous running of the file2data_mp function on the text files
        pool.close()
        pool.join()
        results = []
        
        while not result.empty(): #Extracting results from the multiprocessing
            results.append(result.get())
        
        data = [[],[],[],[],[],[]]
        
        for i in range(len(results)):
            for j in range(len(data)):
                data[j] += results[i][j]

    return data #Returning data as [time,intT,outT,dT,state,cumulative_clicks]

from netCDF4 import Dataset
import multiprocessing as mp
import yaml
import os
import pumapy as puma

file = open('../PuMA_Inventory/puma-inventory.yml','r') #Opening the inventory file of the stoves in the project
yams = yaml.load(file)
file.close()

name_list = [] #Making a list of the stove names
for i in yams:
    name_list.append(i)

air_temp_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),'../Data/aoos_snotel_temp.nc')
fuel_click_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),'../Data/FuelClickConversion.txt')

merged_file = Dataset('../Data/puma_unified_data.nc','w',format='NETCDF4') #Making a netCDF4 file for the final data product (netCDF4 allows for grouping, which is used per stove later)

os.chdir('../../ftp-data') #This function changes the active directory to the directory with all the stove data files in 'FBK000' format; this will need adjusting depending on where the stove files are stored relative to this script 
dir_list = os.listdir()
dir_list.sort()
stoves = []
for stove in dir_list: #Making a list of all the inventoried stoves
    if stove in name_list:
        stoves.append(stove)

print('Stove data collated:')
print(stoves)

for stove in stoves:
    
    years = os.listdir(stove) #Collecting all the year directories per stove directory
    
    merged_file.createGroup(stove) #Creating a netCDF4 group for each stove
    merged_file[stove].description = 'Stove type: ' + yams[stove]['Stove Type'] #Labelling the stove type
    merged_file[stove].createDimension('location',1) #Creating dimensions for the variables to depend on
    merged_file[stove].createDimension('time',None)
    
    merged_file[stove].createVariable('lat','f4',('location')) #Creating the variables for the data collected
    merged_file[stove].createVariable('lon','f4',('location'))    
    merged_file[stove].createVariable('time','f8',('time'))
    merged_file[stove].createVariable('state','i4',('time'))
    merged_file[stove].createVariable('clicks','i8',('time'))
    merged_file[stove].createVariable('cumulative_clicks','i8',('time'))
    merged_file[stove].createVariable('fuel_consumption','f8',('time'))
    merged_file[stove].createVariable('fuel_consumption_rate','f8',('time'))
    merged_file[stove].createVariable('indoor_temp','f4',('time'))
    merged_file[stove].createVariable('outdoor_temp','f4',('time'))
    merged_file[stove].createVariable('delta_temp','f4',('time'))
    
    merged_file[stove]['lat'].description = 'Latitude of the PUMA device location' #Creating descriptions and units in the netCDF4 file to make it more portable
    merged_file[stove]['lon'].description = 'Longitude of the PUMA device location'
    merged_file[stove]['time'].description = 'Timestamp of each PUMA device reading'
    merged_file[stove]['time'].units = 'Time since 1970, 1, 1, 00:00:00 UTC (Unix time)'
    merged_file[stove]['state'].description = 'State of the stove when powered on; depends on the stove type the PuMA device is attached to'
    merged_file[stove]['state'].units = 'Integer units corresponding to power states; -1 indicates powered off'
    merged_file[stove]['cumulative_clicks'].description = 'Number of cumulative clicks since PuMA installation the fuel pump solenoid makes when the stove turns on'
    merged_file[stove]['cumulative_clicks'].units = 'Number of cumulative clicks; -1 indicates stove powered off'
    merged_file[stove]['clicks'].description = 'Number of clicks the fuel pump solenoid makes when the stove turns on per time interval'
    merged_file[stove]['clicks'].units = 'Number of clicks'
    merged_file[stove]['fuel_consumption'].description = 'The amount of fuel consumed by the stove'
    merged_file[stove]['fuel_consumption'].units = 'US gallons'
    merged_file[stove]['fuel_consumption_rate'].description = 'The fuel consumption rate of the stove'
    merged_file[stove]['fuel_consumption_rate'].units = 'US gallons per hour'
    merged_file[stove]['indoor_temp'].description = 'Indoor temperature read by the thermistor monitored by the PUMA device'
    merged_file[stove]['indoor_temp'].units = 'F'
    merged_file[stove]['outdoor_temp'].description = 'Outdoor temperature interpolated using area temperature data from Snotel'
    merged_file[stove]['outdoor_temp'].units = 'F'
    merged_file[stove]['delta_temp'].description = 'Temperature difference between the indoor and outdoor temperatures'
    merged_file[stove]['delta_temp'].units = 'F'
    
    os.chdir(stove) #Changing to the stove directory
    
    year_data = [[],[],[],[],[],[]] #Data buffer for all years
    
    for year in years:
        months = os.listdir(year) #Collecting all month directories in the year directory
        os.chdir(year) #Changing to the year directory
        
        month_data = [[],[],[],[],[],[]] #Data buffer for all months

        for month in months:
            os.chdir(month) #Changing to the month directory
            dir_data = dir2data_mp(air_temp_file) #Inputing the path to the outdoor temperature file and the running the function defined at the top of the script, extracting the data from the PUMA text files; this will need to be changed depending on the database structure and the location of the outdoor temperature file relative to this script
            for i in range(len(month_data)): #Collating the month data into the transcending all month buffer
                month_data[i] += dir_data[i]
            os.chdir('..') #Leaving the month directory

        for i in range(len(year_data)): #Collating the year data into the transcending all year buffer
            year_data[i] += month_data[i]
        
        os.chdir('..') #Leaving the year directory
    
    year_data = puma.stove_data_polish(year_data) #Sorting and removing duplicates and bad data from the data
    
    clicks = puma.cumulative_clicks2clicks(year_data[5])
    year_data.append(clicks)
    gallons = puma.run_clicks2gallons(year_data[6],year_data[4],yams[stove],fuel_click_file)
    year_data.append(gallons)
    gph = puma.run_galperhour(gallons,year_data[0])
    year_data.append(gph) #year_data now looks like [stime,inT,outT,dT,state,cumulative_clicks,clicks,gallons,gph]
    
    stove_data = year_data

    merged_file[stove]['lat'][:] = yams[stove]['Location'][0] #Filling the variables
    merged_file[stove]['lon'][:] = yams[stove]['Location'][1]
    merged_file[stove]['time'][:] = stove_data[0]
    merged_file[stove]['state'][:] = stove_data[4]
    merged_file[stove]['cumulative_clicks'][:] = stove_data[5]
    merged_file[stove]['clicks'][:] = stove_data[6]
    merged_file[stove]['fuel_consumption'][:] = stove_data[7]
    merged_file[stove]['fuel_consumption_rate'][:] = stove_data[8]
    merged_file[stove]['indoor_temp'][:] = stove_data[1]
    merged_file[stove]['outdoor_temp'][:] = stove_data[2]
    merged_file[stove]['delta_temp'][:] = stove_data[3]
    
    os.chdir('..') #Leaving the stove directory
    
merged_file.close() #Closing the netCDF4 file and you're done!
