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
        
def deltaT(indoorT, outdoorT): #Computes the difference in temperature of the indoor and outdoor temperatures
    
    return indoorT - outdoorT

def run_deltaT(intT, outT): #Runs the deltaT function for lists of indoor temp. and outdoor temp. of the same size
    
    dT = []
    for i in range(len(intT)):
        dT.append(round(deltaT(intT[i],outT[i]),2))
        
    return dT
    
def indoorT(thermistor): #Computes the indoor temperature from the thermistor value collected by the PUMA device
    
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

    if stove_time < air_time[0] and air_time[-1] < stove_time: #Checking if the desired point is in the outdoor temp. data
        
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
        if len(i) == 4:
            for j in range(len(stove_data)):
                stove_data[j].append(i[j])
    
    stove_file.close()
    
    stove_time = stove_data[0][1::]
    state = stove_data[1][1::]
    clicks = stove_data[2][1::]
    thermistor = stove_data[3][1::]
    
    for i in range(len(stove_time)): #Replacing off states from 'X' to a numeric -1 for easier data processing later on
        stove_time[i] = float(stove_time[i]) #Keeping UTC time
        if state[i]=='X':
            state[i] = -1
            clicks[i] = -1
        else:
            state[i] = int(state[i]) #Converting from string to int (or float further down)
            clicks[i] = int(clicks[i])
        thermistor[i] = float(thermistor[i])
        
    return stove_time, state, clicks, thermistor

def file2data(stove_file,air_temp_file): #Extracts the final data indoor temp., outdoor temp., and temp. difference and collates with the status, clicks, and time
    
    stove_time, state, clicks, thermistor = pumatxt2data(stove_file)
    outT = run_outdoorT(air_temp_file,stove_time)
    inT = run_indoorT(thermistor)
    dT = deltaT(inT,outT)
    stime = stove_time
    
    return stime, inT, outT, dT, state, clicks

def dir2data(air_temp_file): #This runs the file2data function for each month directory in the yearly stove datasets; robust but slow, use the parallelized code
    
    file_list = []
    for file in os.listdir():
        if file.endswith('.txt'):
            if not file.endswith('LOG.txt'):
                file_list.append(file)
    file_list.sort()
    pumas = [[],[],[],[],[],[]]
    for file in file_list:
        print(file)
        data = file2data(file,air_temp_file)
        for i in range(len(pumas)):
            pumas[i] += data[i]
            
    return pumas

def file2data_mp(stove_file,air_temp_file,result): #This function is the parallelized version of file2data function above; main difference is the multiprocess safe 'result' buffer
    
    stove_time, state, clicks, thermistor = pumatxt2data(stove_file)
    outT = run_outdoorT(air_temp_file,stove_time)
    inT = run_indoorT(thermistor)
    dT = run_deltaT(inT,outT)
    stime = stove_time
    print(stove_file)
    result.put([stime, inT, outT, dT, state, clicks])
    
def dir2data_mp(air_temp_file): #This runs the file2data_mp function for each month directory in the yearly stove datasets but IS NOT Windows SAFE

    file_list = []
    for file in os.listdir():
        if file.endswith('.txt'):
            if not file.endswith('LOG.txt'):
                file_list.append(file)
    file_list.sort()
    
    result = mp.Manager().Queue()
    pool = mp.Pool(mp.cpu_count())
    for file in file_list:
        pool.apply_async(file2data_mp,args=(file,air_temp_file,result))
    pool.close()
    pool.join()
    results = []
    
    while not result.empty():
        results.append(result.get())
    
    data = [[],[],[],[],[],[]]
    
    for i in range(len(results)):
        for j in range(len(data)):
            data[j] += results[i][j]

    return data

def data_sort(data_list): #Sorts the stove data by putting the information into a tuple per timestamp and sorting by said timestamp
    
    data_sorted = []
    for i in range(len(data_list[0])):
        data_sorted.append((data_list[0][i],data_list[1][i],data_list[2][i],data_list[3][i],data_list[4][i],data_list[5][i]))
    data_sorted.sort()
    
    return data_sorted

def remove_duplicates_list(dup_list): #Removes duplicate and NaN inflicted tuples in the data list recieved from the data_sort function
    
    fin_list = []
    for item in dup_list:
        if item not in fin_list and np.nan not in item:
            fin_list.append(item)
            
    return fin_list

def stove_data_polish(stove_data): #Runs both the data_sort function and the remove_duplicates_list function and then changes the list back to a list of lists [time,intT,outT,dT,status,clicks]
    
    stove_data_sorted = data_sort(stove_data)
    stove_data_fin = remove_duplicates_list(stove_data_sorted)
    
    stove_data_polished = [[],[],[],[],[],[]]
    for item in stove_data_fin:
        for i in range(len(stove_data_polished)):
            stove_data_polished[i].append(item[i])
            
    return stove_data_polished

