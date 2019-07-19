#This is the accompanying module file to go along with the doug_puma_run.py script; these are the functions utilized

#Created: Tue Jun 18 10:39:04 2019
#By: Douglas Keller

from netCDF4 import Dataset, num2date
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import csv
import os
import multiprocessing as mp
from scipy.interpolate import interp1d
import yaml

#### Text to netCDF files

def deltaT(indoorT, outdoorT): #Computes the difference in temperature of the indoor and outdoor temperatures
    
    return indoorT - outdoorT

def run_deltaT(intT, outT): #Runs the deltaT function for lists of indoor temp. and outdoor temp. of the same size
    
    dT = []
    for i in range(len(intT)):
        dT.append(round(deltaT(intT[i],outT[i]),2))
        
    return dT
    
def indoorT(thermistor): #Computes the indoor temperature from the thermistor value collected by the PUMA device
    
    if int(thermistor) == 0:
        return np.nan

    indoorT = round(((3.354*10**-3 + (2.56985*10**-4)*np.log(thermistor/10000) + #This is the function returning temp. from thermistor values; may return a NaN
                (2.620131*10**-6)*np.log( thermistor/10000)**2 + 
                (6.383091*10**-8)*np.log( thermistor/10000)**3)**-1 - 273.15)*1.8 + 32, 2)
    
    return indoorT

def run_indoorT(thermistor): #Computes the array of indoor temperatures from the PUMA device data
    
    inT = []
    for i in range(len(thermistor)):
        inT.append(indoorT(thermistor[i]))
        
    return inT
    
def outdoorT(air_temp,air_time,stove_time): #Computes the outdoor temperature for the area and time of interest

    if stove_time < air_time[0] or air_time[-1] < stove_time: #Checking if the desired point is in the outdoor temp. data
        
        return np.nan
    
    else:

        temp_interp = interp1d(air_time,air_temp) #Linearly interpolates the outdoor temp. when the indoor temp. is between hours
        
        return round(float(temp_interp(stove_time)),2)
    
def run_outdoorT(air_temp_file,stove_time): #Computes an array of outdoor temperature at the location specified in the netCDF file obtained from Snotel observations
    
    at_data = Dataset(air_temp_file,'r') #Assuming air temperature file from NRCS Snotel observations in netCDF form
    air_temp = at_data.variables['air_temperature'][:]
    at_time = at_data.variables['time'][:]
    
    outT = []
    for i in range(len(stove_time)):
        outT.append(outdoorT(air_temp,at_time,stove_time[i]))
    
    return outT
    
def pumatxt2data(stove_file): #Function that extracts the time, state, clicks, and thermistor data from the PUMA text files
    
    stove_file = open(stove_file,'r')
    
    stove_csv = csv.reader(stove_file, delimiter='\t') #Reading the file as a tab delimited file
    
    stove_data = [[],[],[],[]]
    
    for i in stove_csv:
        if len(i) == 4 and '' not in i:
            if i[1] == '5':
                pass
            else:
                for j in range(len(stove_data)):
                    stove_data[j].append(i[j])
    
    stove_file.close()
    
    stove_time = stove_data[0][1::]
    state = stove_data[1][1::]
    cumulative_clicks = stove_data[2][1::]
    thermistor = stove_data[3][1::]
    
    for i in range(len(stove_time)): #Replacing off states from 'X' to a numeric -1 for easier data processing later on
        stove_time[i] = float(stove_time[i]) #Keeping UTC time
        if state[i]=='X':
            state[i] = -1
            cumulative_clicks[i] = -1
        else:
            state[i] = int(state[i]) #Converting from string to int (or float further down)
            cumulative_clicks[i] = int(cumulative_clicks[i])
        thermistor[i] = float(thermistor[i])
        
    return stove_time, state, cumulative_clicks, thermistor

def file2data(stove_file,air_temp_file,result): #This function is the parallelized version of file2data function above; main difference is the multiprocess safe 'result' buffer
    #This runs the file2data function for each month directory in the yearly stove datasets; robust but slow, use the parallelized code
    stove_time, state, cumulative_clicks, thermistor = pumatxt2data(stove_file)
    outT = run_outdoorT(air_temp_file,stove_time)
    inT = run_indoorT(thermistor)
    dT = run_deltaT(inT,outT)
    stime = stove_time
    print(stove_file)
    result.put([stime, inT, outT, dT, state, cumulative_clicks])
    
def dir2data(air_temp_file): #This runs the file2data_mp function for each month directory in the yearly stove datasets

    file_list = [] #Making a list of the file names in each directory, only adding the text files, excluding the log.txt files
    for file in os.listdir():
        if file.endswith('.txt'):
            if not file.endswith('LOG.txt'):
                file_list.append(file)
    file_list.sort()
    
    result = mp.Manager().Queue() #Instantiating a multiprocess safe buffer (needed for multiprocessing)
    pool = mp.Pool(mp.cpu_count()) #Making a pool of processes (think of it as other initializations of python each running its own program)
    for file in file_list:
        pool.apply_async(file2data,args=(file,air_temp_file,result)) #Asynchronous running of the file2data_mp function on the text files
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

def data_sort(data_list): #Sorts the stove data by putting the information into a tuple per timestamp and sorting by said timestamp
    
    data_sorted = []
    for i in range(len(data_list[0])):
        data_tuple = ()
        for j in range(len(data_list)):
            data_tuple += (data_list[j][i],)
        data_sorted.append(data_tuple)
    data_sorted.sort()
    
    return data_sorted

def remove_duplicates_list(dup_list): #Removes duplicate and NaN inflicted tuples in the data list recieved from the data_sort function
    
    fin_list = [(0,)]
    for item in dup_list:
        if item not in fin_list and not True in np.isnan(item) and item[0] != fin_list[-1][0]:
            fin_list.append(item)
    
    fin_list = fin_list[1::]
    
    return fin_list

def stove_data_polish(stove_data): #Runs both the data_sort function and the remove_duplicates_list function and then changes the list back to a list of lists [time,intT,outT,dT,status,clicks]
    
    stove_data_sorted = data_sort(stove_data)
    stove_data_fin = remove_duplicates_list(stove_data_sorted)
    
    stove_data_polished = []
    
    for i in stove_data:
        stove_data_polished.append([])
        
    for item in stove_data_fin:
        for i in range(len(stove_data_polished)):
            stove_data_polished[i].append(item[i])
            
    return stove_data_polished

def cumulative_clicks2clicks(cumulative_clicks):
    
    clicks = []
    last_click = -1
    for i in range(len(cumulative_clicks)):
        if cumulative_clicks[i] < 0:
            clicks.append(0)
        elif last_click < 0:
            last_click = cumulative_clicks[i]
            clicks.append(0)
        elif cumulative_clicks[i] - last_click > 0:
            clicks.append(cumulative_clicks[i]-last_click)
            last_click = cumulative_clicks[i]
        elif cumulative_clicks[i] - last_click < 0:
            last_click = cumulative_clicks[i]
            clicks.append(0)
        else:
            clicks.append(0)

    return clicks
            
def stove_rate(stove_dict,fuel_click_file): #Determines the stove fuel pump rate depending on the stove type
    
    fuel_click_file = open(fuel_click_file,'r')
    fuel_click = csv.reader(fuel_click_file, delimiter=',') #Reading the file as a comma delimited file
    
    for stove_type in fuel_click:
        if stove_type[0] == stove_dict['Stove Type']:
            rate = stove_type[1]
    
    return rate

def clicks2gallons(clicks,rate): #Determines the fuel pumped from the clicks counted by the PuMA device
    
    return clicks*rate

def run_clicks2gallons(clicks,state,stove_dict,fuel_click_file): #Runs the clicks to gallons function for the clicks array
    
    rate = stove_rate(stove_dict,fuel_click_file)
    gallons = []
    for i in range(len(state)):
        gallons.append(clicks2gallons(clicks[i],float(rate)))
    return gallons

def galperhour(gal,deltat): #Calculates the US gallons per hour
    
    return gal/deltat*3600

def run_galperhour(gallons,stime): #Runs the US gallons per hour calculation
    
    gph = []
    for i in range(len(gallons)):
        if i == 0:
            deltat = stime[1] - stime[0]
        else:
            deltat = stime[i] - stime[i-1]
        gph.append(galperhour(gallons[i],deltat))
        
    return gph

#### Data Packaging Metafunctions

def puma2uni_nc():
    
    file_path = os.path.abspath(os.path.dirname(__file__))
    
    yaml_file = os.path.join(file_path,'..','Data','yaml_Files','puma-inventory.yml')
    file = open(yaml_file,'r') #Opening the inventory file of the stoves in the project
    yams = yaml.load(file)
    file.close()
    
    name_list = [] #Making a list of the stove names
    for i in yams:
        name_list.append(i)
    
    air_temp_file = os.path.join(file_path,'..','Data','netCDF_Files','aoos_snotel_temp.nc')
    fuel_click_file = os.path.join(file_path,'..','Data','text_Files','FuelClickConversion.txt')
    
    new_nc = os.path.join(file_path,'..','Data','netCDF_Files','puma_unified_data.nc')
    merged_file = Dataset(new_nc,'w',format='NETCDF4') #Making a netCDF4 file for the final data product (netCDF4 allows for grouping, which is used per stove later)
    
    new_nc_att = {'Contents':'netCDF file that contains the stoves in the fuel meter project, found in individual groups','Variables':'variables in each stove group are: time, cumulative clicks, clicks per interval, fuel consumption per interval, fuel consumption rate per interval, indoor temperature, outdoor temperature, temperature difference, stove status per interval'}
    merged_file.setncatts(new_nc_att)

    ftp_data = os.path.join(file_path,'..','..','ftp-data')
    os.chdir(ftp_data) #This function changes the active directory to the directory with all the stove data files in 'FBK000' format; this will need adjusting depending on where the stove files are stored relative to this script 
    
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
        merged_file[stove].setncatts(yams[stove])
        merged_file[stove].createDimension('time',None) #Creating dimensions for the variables to depend on
        
        merged_file[stove].createVariable('time','f8',('time'))
        merged_file[stove].createVariable('state','i4',('time'))
        merged_file[stove].createVariable('clicks','i8',('time'))
        merged_file[stove].createVariable('cumulative_clicks','i8',('time'))
        merged_file[stove].createVariable('fuel_consumption','f8',('time'))
        merged_file[stove].createVariable('fuel_consumption_rate','f8',('time'))
        merged_file[stove].createVariable('indoor_temp','f4',('time'))
        merged_file[stove].createVariable('outdoor_temp','f4',('time'))
        merged_file[stove].createVariable('delta_temp','f4',('time'))
        
        merged_file[stove]['time'].description = 'Timestamp of each PUMA device reading' #Creating descriptions and units in the netCDF4 file to make it more portable
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
                dir_data = dir2data(air_temp_file) #Inputing the path to the outdoor temperature file and the running the function defined at the top of the script, extracting the data from the PUMA text files; this will need to be changed depending on the database structure and the location of the outdoor temperature file relative to this script
                for i in range(len(month_data)): #Collating the month data into the transcending all month buffer
                    month_data[i] += dir_data[i]
                os.chdir('..') #Leaving the month directory
    
            for i in range(len(year_data)): #Collating the year data into the transcending all year buffer
                year_data[i] += month_data[i]
            
            os.chdir('..') #Leaving the year directory
        
        year_data = stove_data_polish(year_data) #Sorting and removing duplicates and bad data from the data
        
        clicks = cumulative_clicks2clicks(year_data[5])
        year_data.append(clicks)
        gallons = run_clicks2gallons(year_data[6],year_data[4],yams[stove],fuel_click_file)
        year_data.append(gallons)
        gph = run_galperhour(gallons,year_data[0])
        year_data.append(gph) #year_data now looks like [stime,inT,outT,dT,state,cumulative_clicks,clicks,gallons,gph]
        
        stove_data = year_data
    
        merged_file[stove]['time'][:] = stove_data[0] #Filling the variables
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
    
    return stoves,prod_nc

def prod_nc2csv():
    
    stoves,product_file_name = uni_nc2prod_nc()

    def stove_csv(stove,product_file_name):
    
        product_file = Dataset(product_file_name,'r') #Opening the product netcdf data file
        
        with open(stove + '.csv','w',newline='') as stove_file:
            
            stove_csv_file = csv.writer(stove_file, dialect='excel')
            
            stove_csv_file.writerow(['Stove Type'] + [product_file[stove].getncattr('Stove Type')] + #Stove description and location
                                    ['Latitude'] + [str(product_file[stove].getncattr('Location')[0])] + 
                                    ['Longitude'] + [str(product_file[stove].getncattr('Location')[1])] + [''] + [''] + [''])
            
            stove_csv_file.writerow([product_file[stove]['time'].description] + [product_file[stove]['state'].description] + #Descriptions
                                    [product_file[stove]['cumulative_clicks'].description] + [product_file[stove]['clicks'].description] + 
                                    [product_file[stove]['fuel_consumption'].description] + [product_file[stove]['fuel_consumption_rate'].description] + 
                                    [product_file[stove]['indoor_temp'].description] + [product_file[stove]['outdoor_temp'].description] + 
                                    [product_file[stove]['delta_temp'].description])
            
            stove_csv_file.writerow([product_file[stove]['time'].units] + [product_file[stove]['state'].units] + #Units
                                    [product_file[stove]['cumulative_clicks'].units] + [product_file[stove]['clicks'].units] +  
                                    [product_file[stove]['fuel_consumption'].units] + [product_file[stove]['fuel_consumption_rate'].units] +
                                    [product_file[stove]['indoor_temp'].units] + [product_file[stove]['outdoor_temp'].units] + 
                                    [product_file[stove]['delta_temp'].units]) 
                
            for i in range(len(product_file[stove]['time'][:])):
            
                stove_csv_file.writerow([str(product_file[stove]['time'][i])] + [str(product_file[stove]['state'][i])] + #Values
                                        [str(product_file[stove]['cumulative_clicks'][i])] + [str(product_file[stove]['clicks'][i])] + 
                                        [str(product_file[stove]['fuel_consumption'][i])] + [str(product_file[stove]['fuel_consumption_rate'][i])] + 
                                        [str(product_file[stove]['indoor_temp'][i])] + [str(product_file[stove]['outdoor_temp'][i])] + 
                                        [str(product_file[stove]['delta_temp'][i])])
        
            product_file.close() #Closing the netCDF4 file
            print(stove)
        
    file_path = os.path.abspath(os.path.dirname(__file__))
    
    csv_files = os.path.join(file_path,'..','Data','csv_Files')
    os.chdir(csv_files)
    
    pool = mp.Pool(mp.cpu_count()) #Making a pool of processes (think of it as other initializations of python each running its own program)
    for stove in stoves:
        pool.apply_async(stove_csv,args=(stove,product_file_name)) #Asynchronous running of the stove_csv function to create csv files
    pool.close()
    pool.join()