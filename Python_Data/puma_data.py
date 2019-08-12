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

def file2data(stove_file,result): #This function is the parallelized version of file2data function above; main difference is the multiprocess safe 'result' buffer
    #This runs the file2data function for each month directory in the yearly stove datasets; robust but slow, use the parallelized code
    stove_time, state, cumulative_clicks, thermistor = pumatxt2data(stove_file)
    stime = stove_time
    print(stove_file)
    result.put([stime, state, cumulative_clicks, thermistor])
    
def dir2data(): #This runs the file2data_mp function for each month directory in the yearly stove datasets

    file_list = [] #Making a list of the file names in each directory, only adding the text files, excluding the log.txt files
    for file in os.listdir():
        if file.endswith('.txt'):
            if not file.endswith('LOG.txt'):
                file_list.append(file)
    file_list.sort()
    
    result = mp.Manager().Queue() #Instantiating a multiprocess safe buffer (needed for multiprocessing)
    pool = mp.Pool(mp.cpu_count()) #Making a pool of processes (think of it as other initializations of python each running its own program)
    for file in file_list:
        pool.apply_async(file2data,args=(file,result)) #Asynchronous running of the file2data_mp function on the text files
    pool.close()
    pool.join()
    results = []
    
    while not result.empty(): #Extracting results from the multiprocessing
        results.append(result.get())
    
    data = [[],[],[],[]]
    
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

#### Time Arrays

def raw2time(air_temp_file,year_data):
    #Turning the raw data arrays into the time data arrays
    #year_data = [stime,state,cumulative_clicks,thermistor]
    stime = year_data[0]
    thermistor = year_data[3]
    
    outT = run_outdoorT(air_temp_file,stime)
    inT = run_indoorT(thermistor)
    dT = run_deltaT(inT,outT)
    
    time_data = [stime,inT,outT,dT]
    
    return time_data

#### Event Arrays
    
def raw_time2event(year_data,time_data,stove_type_dict,fuel_click_file):
    #Turning raw and time data arrays to event data arrays
    data = year_data[0:-1] + time_data[1::]
    event_data = []
    for i in range(len(data)):
        event_data.append([])
        
    for i in range(len(data[0])):
        if data[1][i] != -1:
            for j in range(len(data)):
                event_data[j].append(data[j][i])
    
    click_data = []
    clicks,click_state = cumulative_clicks2clicks(event_data[2],event_data[1])
    gallons = run_clicks2gallons(clicks,stove_type_dict,fuel_click_file)
    gph = run_galperhour(gallons,event_data[0])
    click_time = midpoint(event_data[0])
    click_inT = midpoint(event_data[3])
    click_outT = midpoint(event_data[4])
    click_dT = midpoint(event_data[5])
    
    click_data.append(click_time)
    click_data.append(clicks)
    click_data.append(click_state)
    click_data.append(click_inT)
    click_data.append(click_outT)
    click_data.append(click_dT)
    click_data.append(gallons)
    click_data.append(gph)
    
    return event_data, click_data #[stime,state,cumulative_clicks,inT,outT,dT] and [click_time,clicks,click_state,click_inT,click_outT,click_dT,gallons,gph]

def cumulative_clicks2clicks(cumulative_clicks,state):
    
    clicks = list(np.diff(cumulative_clicks))
    click_state = []
    for i in range(len(clicks)):
        click_state.append(state[i+1])

    return clicks, click_state
            
def stove_rate(stove_dict,fuel_click_file): #Determines the stove fuel pump rate depending on the stove type
    
    fuel_click_file = open(fuel_click_file,'r')
    fuel_click = csv.reader(fuel_click_file, delimiter=',') #Reading the file as a comma delimited file
    
    for stove_type in fuel_click:
        if stove_type[0] == stove_dict['Stove Type']:
            rate = stove_type[1]
    
    return rate

def clicks2gallons(clicks,rate): #Determines the fuel pumped from the clicks counted by the PuMA device
    
    return clicks*rate

def run_clicks2gallons(clicks,stove_dict,fuel_click_file): #Runs the clicks to gallons function for the clicks array
    
    rate = stove_rate(stove_dict,fuel_click_file)
    gallons = []
    for i in range(len(clicks)):
        gallons.append(clicks2gallons(clicks[i],float(rate)))
        
    return gallons

def galperhour(gal,deltat): #Calculates the US gallons per hour
    
    return gal/deltat*3600
    
def run_galperhour(gallons,stime): #Runs the US gallons per hour calculation
    
    gph = []
    deltat = np.diff(stime)
    for i in range(len(gallons)):
        gph.append(galperhour(gallons[i],deltat[i]))
        
    return gph

#### Calculated Values
    
def midpoint(array):
    
    mid_array = []
    for i in range(len(array)-1):
        mid_array.append(np.mean(array[i:i+2]))
        
    return mid_array

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

#### Data Packaging Metafunctions

def nc_createVariables(nc_file,variables,unit_type,dependent_variable):
    #Creating variables in the netCDF4 file
    for i in range(len(variables)):
        nc_file.createVariable(variables[i],unit_type[i],(dependent_variable))
        
def nc_description_set(nc_file,variables,descriptions):
    #Creating descriptions in the netCDF4 file to make it more portable
    for i in range(len(variables)):
        nc_file[variables[i]].description = descriptions[i]
        
def nc_units_set(nc_file,variables,unit):
    #Creating units in the netCDF4 file to make it more portable
    for i in range(len(variables)):
        nc_file[variables[i]].units = unit[i]     

def fill_nc(nc_file,variables,data):
    #Filling the netCDF4 files
    for i in range(len(variables)):
        nc_file[variables[i]][:] = data[i]
        
def nc_transfer_variables(old_nc,new_nc,variables):
    #Transferring the variables from the old netCDF4 file to the new one
    for variable in variables:
        new_nc[variable][:] = old_nc[variable][:]
        
def nc_transfer_attributes(old_nc,new_nc,attributes):
    #Transferring the attributes from the old netCDF4 file to the new one
    for att in attributes:
        new_nc.setncattr(att,old_nc.getncattr(att))
    
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
        
        #### Raw data section ####
        
        merged_file[stove].createGroup('Raw')
        merged_file[stove+'/Raw'].createDimension('time',None) #Creating dimensions for the variables to depend on
        
        raw_variables = ['time','state','cumulative_clicks','thermistor']
        
        raw_descriptions = ['Timestamp of each PUMA device reading',
                            'State of the stove when powered on; depends on the stove type the PuMA device is attached to',
                            'Number of cumulative clicks since PuMA installation the fuel pump solenoid makes when the stove turns on',
                            'Thermistor resistance of the indoor thermistor']
        
        raw_units = ['Time since 1970, 1, 1, 00:00:00 UTC (Unix time)',
                     'Integer units corresponding to power states; -1 indicates powered off',
                     'Number of cumulative clicks; -1 indicates stove powered off',
                     'Thermistor resistance (ohms)']
        
        raw_unit_types = ['f8','i4','i8','i8']
        
        nc_createVariables(merged_file[stove+'/Raw'],raw_variables,raw_unit_types,'time')
        nc_description_set(merged_file[stove+'/Raw'],raw_variables,raw_descriptions)
        nc_units_set(merged_file[stove+'/Raw'],raw_variables,raw_units)
        
        #### Time based data section ####
        
        merged_file[stove].createGroup('Time')
        merged_file[stove+'/Time'].createDimension('time',None)
        
        time_variables = ['time','indoor_temp','outdoor_temp','delta_temp']
        
        time_descriptions = ['Timestamp of each PUMA device reading',
                             'Indoor temperature read by the thermistor monitored by the PUMA device',
                             'Outdoor temperature interpolated using area temperature data from Snotel',
                             'Temperature difference between the indoor and outdoor temperatures']
        
        time_units = ['Time since 1970, 1, 1, 00:00:00 UTC (Unix time)',
                      'F','F','F']
        
        time_unit_types = ['f8','f4','f4','f4']
        
        nc_createVariables(merged_file[stove+'/Time'],time_variables,time_unit_types,'time')
        nc_description_set(merged_file[stove+'/Time'],time_variables,time_descriptions)
        nc_units_set(merged_file[stove+'/Time'],time_variables,time_units)
        
        #### Event based data section ####

        merged_file[stove].createGroup('Event/Raw')
        merged_file[stove].createGroup('Event/Clicks')
        merged_file[stove+'/Event/Raw'].createDimension('time',None)
        merged_file[stove+'/Event/Clicks'].createDimension('time',None)
        
        event_variables = ['time','state','cumulative_clicks','indoor_temp',
                           'outdoor_temp','delta_temp']
        
        event_descriptions = ['Timestamp of each PUMA device reading',
                              'State of the stove when powered on; depends on the stove type the PuMA device is attached to',
                              'Number of cumulative clicks since PuMA installation the fuel pump solenoid makes when the stove turns on',
                              'Indoor temperature read by the thermistor monitored by the PUMA device',
                              'Outdoor temperature interpolated using area temperature data from Snotel',
                              'Temperature difference between the indoor and outdoor temperatures']
        
        event_units = ['Time since 1970, 1, 1, 00:00:00 UTC (Unix time)',
                       'Integer units corresponding to power states; -1 indicates powered off',
                       'Number of cumulative clicks; -1 indicates stove powered off',
                       'F','F','F']
        
        click_variables = ['time','clicks','state','indoor_temp','outdoor_temp',
                           'delta_temp','fuel_consumption','fuel_consumption_rate']
        
        click_descriptions = ['Timestamp of the clicks per interval',
                              'Number of clicks the fuel pump solenoid makes when the stove turns on per time interval',
                              'State of the stove per interval of clicks',
                              'Indoor temperature per interval','Outdoor temperature per interval',
                              'Temperature difference per interval',
                              'The amount of fuel consumed by the stove','The fuel consumption rate of the stove']
        
        click_units = ['Time since 1970, 1, 1, 00:00:00 UTC (Unix time)','Number of clicks',
                       'Integer units corresponding to power states; -1 indicates powered off',
                       'F','F','F','US gallons','US gallons per hour']
        
        event_unit_types = ['f8','i4','i8','f4','f4','f4']
        
        click_unit_types = ['f8','i8','i4','f4','f4','f4','f8','f8']
        
        nc_createVariables(merged_file[stove+'/Event/Raw'],event_variables,event_unit_types,'time')
        nc_description_set(merged_file[stove+'/Event/Raw'],event_variables,event_descriptions)
        nc_units_set(merged_file[stove+'/Event/Raw'],event_variables,event_units)
        nc_createVariables(merged_file[stove+'/Event/Clicks'],click_variables,click_unit_types,'time')
        nc_description_set(merged_file[stove+'/Event/Clicks'],click_variables,click_descriptions)
        nc_units_set(merged_file[stove+'/Event/Clicks'],click_variables,click_units)
        
        os.chdir(stove) #Changing to the stove directory
        
        year_data = [[],[],[],[]] #Data buffer for all years
        
        for year in years:
            months = os.listdir(year) #Collecting all month directories in the year directory
            os.chdir(year) #Changing to the year directory
            
            month_data = [[],[],[],[]] #Data buffer for all months
    
            for month in months:
                os.chdir(month) #Changing to the month directory
                dir_data = dir2data() #Inputing the path to the outdoor temperature file and the running the function defined at the top of the script, extracting the data from the PUMA text files; this will need to be changed depending on the database structure and the location of the outdoor temperature file relative to this script
                for i in range(len(month_data)): #Collating the month data into the transcending all month buffer
                    month_data[i] += dir_data[i]
                os.chdir('..') #Leaving the month directory
    
            for i in range(len(year_data)): #Collating the year data into the transcending all year buffer
                year_data[i] += month_data[i]
            
            os.chdir('..') #Leaving the year directory
        
        year_data = stove_data_polish(year_data) #Sorting and removing duplicates and bad data from the data
        #year_data looks like [stime,state,cumulative_clicks,thermistor]
        
        fill_nc(merged_file[stove+'/Raw'],raw_variables,year_data)
        
        time_data = raw2time(air_temp_file,year_data)
        #time_data = [stime,inT,outT,dT]
        event_data,click_data = raw_time2event(year_data,time_data,yams[stove],fuel_click_file)
        #event_data = [stime,state,cumulative_clicks,inT,outT,dT]
        #click_data = [click_time,clicks,click_state,click_inT,click_outT,click_dT,gallons,gph]
        
        time_data = stove_data_polish(time_data)
        event_data = stove_data_polish(event_data)
        click_data = stove_data_polish(click_data)
        
        fill_nc(merged_file[stove+'/Time'],time_variables,time_data)
        fill_nc(merged_file[stove+'/Event/Raw'],event_variables,event_data)
        fill_nc(merged_file[stove+'/Event/Clicks'],click_variables,click_data)
        
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
        
    stoves = [] #Making a list of the stove names
    for stove in yams:
        stoves.append(stove)
    
    for stove in stoves:
        
        product_file.createGroup(stove) #Creating a netCDF4 group for each stove
        
        attributes = ['Location','Stove Type']
        
        nc_transfer_attributes(unified_file[stove],product_file[stove],attributes)

        #### Raw data section ####
        
        product_file[stove].createGroup('Raw')
        product_file[stove+'/Raw'].createDimension('time',None)
        
        raw_variables = ['time','state','cumulative_clicks','thermistor']
        
        raw_descriptions = ['Timestamp of each PUMA device reading',
                            'State of the stove when powered on; depends on the stove type the PuMA device is attached to',
                            'Number of cumulative clicks since PuMA installation the fuel pump solenoid makes when the stove turns on',
                            'Thermistor resistance of the indoor thermistor']
        
        raw_units = ['Time since 1970, 1, 1, 00:00:00 UTC (Unix time)',
                     'Integer units corresponding to power states; -1 indicates powered off',
                     'Number of cumulative clicks; -1 indicates stove powered off',
                     'Thermistor resistance (ohms)']
        
        raw_unit_types = ['f8','i4','i8','i8']
        
        nc_createVariables(product_file[stove+'/Raw'],raw_variables,raw_unit_types,'time')
        nc_description_set(product_file[stove+'/Raw'],raw_variables,raw_descriptions)
        nc_units_set(product_file[stove+'/Raw'],raw_variables,raw_units)
        
        nc_transfer_variables(unified_file[stove+'/Raw'],product_file[stove+'/Raw'],raw_variables)
        
        #### Time based data section ####
        
        product_file[stove].createGroup('Time')
        product_file[stove+'/Time'].createDimension('time',None)
        
        time_variables = ['time','indoor_temp','outdoor_temp','delta_temp']
        
        time_descriptions = ['Timestamp of each PUMA device reading',
                             'Indoor temperature read by the thermistor monitored by the PUMA device',
                             'Outdoor temperature interpolated using area temperature data from Snotel',
                             'Temperature difference between the indoor and outdoor temperatures']
        
        time_units = ['Time since 1970, 1, 1, 00:00:00 UTC (Unix time)',
                      'F','F','F']
        
        time_unit_types = ['f8','i4','i8','i8','f8','f8','f4','f4','f4']
        
        nc_createVariables(product_file[stove+'/Time'],time_variables,time_unit_types,'time')
        nc_description_set(product_file[stove+'/Time'],time_variables,time_descriptions)
        nc_units_set(product_file[stove+'/Time'],time_variables,time_units)
        
        nc_transfer_variables(unified_file[stove+'/Time'],product_file[stove+'/Time'],time_variables)
        
        #### Event based data section ####
        
        product_file[stove].createGroup('Event/Raw')
        product_file[stove].createGroup('Event/Clicks')
        
        product_file[stove+'/Event/Raw'].createDimension('time',None)

        
        product_file[stove+'/Event/Clicks'].createDimension('time',None)
        
        event_variables = ['time','state','cumulative_clicks','indoor_temp',
                           'outdoor_temp','delta_temp']
        
        event_descriptions = ['Timestamp of each PUMA device reading',
                              'State of the stove when powered on; depends on the stove type the PuMA device is attached to',
                              'Number of cumulative clicks since PuMA installation the fuel pump solenoid makes when the stove turns on',
                              'Indoor temperature read by the thermistor monitored by the PUMA device',
                              'Outdoor temperature interpolated using area temperature data from Snotel',
                              'Temperature difference between the indoor and outdoor temperatures']
        
        event_units = ['Time since 1970, 1, 1, 00:00:00 UTC (Unix time)',
                       'Integer units corresponding to power states; -1 indicates powered off',
                       'Number of cumulative clicks; -1 indicates stove powered off',
                       'F','F','F']
        
        click_variables = ['time','clicks','state','indoor_temp','outdoor_temp',
                           'delta_temp','fuel_consumption','fuel_consumption_rate']
        
        click_descriptions = ['Timestamp of the clicks per interval',
                              'Number of clicks the fuel pump solenoid makes when the stove turns on per time interval',
                              'State of the stove per interval of clicks',
                              'Indoor temperature per interval','Outdoor temperature per interval',
                              'Temperature difference per interval',
                              'The amount of fuel consumed by the stove','The fuel consumption rate of the stove']
        
        click_units = ['Time since 1970, 1, 1, 00:00:00 UTC (Unix time)','Number of clicks',
                       'Integer units corresponding to power states; -1 indicates powered off',
                       'F','F','F','US gallons','US gallons per hour']
        
        event_unit_types = ['f8','i4','i8','f4','f4','f4']
        
        click_unit_types = ['f8','i8','i4','f4','f4','f4','f8','f8']
        
        nc_createVariables(product_file[stove+'/Event/Raw'],event_variables,event_unit_types,'time')
        nc_description_set(product_file[stove+'/Event/Raw'],event_variables,event_descriptions)
        nc_units_set(product_file[stove+'/Event/Raw'],event_variables,event_units)
        nc_createVariables(product_file[stove+'/Event/Clicks'],click_variables,click_unit_types,'time')
        nc_description_set(product_file[stove+'/Event/Clicks'],click_variables,click_descriptions)
        nc_units_set(product_file[stove+'/Event/Clicks'],click_variables,click_units)
        
        nc_transfer_variables(unified_file[stove+'/Event/Raw'],product_file[stove+'/Event/Raw'],event_variables)
        nc_transfer_variables(unified_file[stove+'/Event/Clicks'],product_file[stove+'/Event/Clicks'],click_variables)
        
    product_file.close() #Closing the netCDF4 file and you're done!
    
    return stoves,prod_nc
            
def stove_csv(stove,group,product_file_name):
    
        product_file = Dataset(product_file_name,'r') #Opening the product netcdf data file
        
        def nc2csv_descriptions(nc):
    
            desc_list =  []
            for var in nc.variables:
                desc_list.append(nc[str(var)].description)
                
            return desc_list

        def nc2csv_units(nc):
            
            unit_list =  []
            for var in nc.variables:
                unit_list.append(nc[str(var)].units)
                
            return unit_list
        
        if '/' in group:
            group_name = group[0:5] + '_' + group[6::]
        else:
            group_name = group
            
        with open(stove + '_' + group_name + '.csv','w',newline='') as stove_file:
            
            stove_csv_file = csv.writer(stove_file, dialect='excel')
            
            group_dir = stove + '/' + group
            
            stove_csv_file.writerow(['Stove Type'] + [product_file[stove].getncattr('Stove Type')] + #Stove description and location
                                    ['Latitude'] + [str(product_file[stove].getncattr('Location')[0])] + 
                                    ['Longitude'] + [str(product_file[stove].getncattr('Location')[1])] + [''] + [''] + [''])
            
            desc = nc2csv_descriptions(product_file[group_dir])
            stove_csv_file.writerow(desc)
            
            unit = nc2csv_units(product_file[group_dir])
            stove_csv_file.writerow(unit) 
                
            for i in range(len(product_file[group_dir]['time'][:])):
                
                row = []
                for var in product_file[group_dir].variables:
                    row.append(str(product_file[group_dir][str(var)][i]))
                
                stove_csv_file.writerow(row)
        
            product_file.close() #Closing the netCDF4 file
            print(group_dir)
    
def prod_nc2csv():
    
    stoves,product_file_name = uni_nc2prod_nc()
        
    file_path = os.path.abspath(os.path.dirname(__file__))
    
    csv_files = os.path.join(file_path,'..','Data','csv_Files')
    os.chdir(csv_files)
    
    groups = ['Raw','Time','Event/Raw','Event/Clicks']
    
    pool = mp.Pool(mp.cpu_count()) #Making a pool of processes (think of it as other initializations of python each running its own program)
    for stove in stoves:
        for group in groups:
            pool.apply_async(stove_csv,args=(stove,group,product_file_name)) #Asynchronous running of the stove_csv function to create csv files
    pool.close()
    pool.join()