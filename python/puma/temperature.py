"""
Temperature Functions for PuMA

By Doug Keller
"""

import pytz
from datetime import datetime
import numpy as np

def heat_degree_day(t_datetime,outT,base):
    """
    Returns a list of the heating degree day from an outdoor temperature list
    
    Arguments:
        t_datetime -- datetime object list
        outT -- outdoor temperature list in Fahrenheit
        base -- temperature base for the heating degree day value e.g. 65 for 65 degrees Fahrenheit
        
    Returns:
        hdd -- list of heating degree day values
        
    This function provides the heating degree day value of a given list of outdoor temperature data (in Fahrenheit) with an accompanying datetime object list, needed for the definition of a heating degree day (https://www.weather.gov/key/climate_heat_cool).
    """
    
    T_ave,day = daily_average_temperature(t_datetime,outT) #finds the average of the minimum and maximum temperature during a given day
    hdd = []
    for i in range(len(t_datetime)): #determining the heating degree day per given datetime object
        for j in range(len(day)):
            if day[j] == (t_datetime[i].year,t_datetime[i].month,t_datetime[i].day):
                hdd.append(base - outT[i])
    
    return hdd

def daily_average_temperature(t_datetime,outT):
    
    day = []
    T_max = []
    T_min = []
    
    i = 0
    while i < len(t_datetime):
        if (t_datetime[i].year,t_datetime[i].month,t_datetime[i].day) not in day:
            day.append((t_datetime[i].year,t_datetime[i].month,t_datetime[i].day))
        i += 1
    
    for i in range(len(day)):
        T_max.append(-999)
        T_min.append(999)
        
    i = 0
    while i < len(t_datetime):
        for j in range(len(day)):
            if day[j] == (t_datetime[i].year,t_datetime[i].month,t_datetime[i].day):
                if T_max[j] < outT[i]:
                    T_max[j] = outT[i]
                if T_min[j] > outT[i]:
                    T_min[j] = outT[i]
        i += 1
    
    T_max = np.array(T_max)
    T_min = np.array(T_min)
    T_ave = (T_max + T_min)/2
    
    return T_ave, day

def day_average_temperature(t,x,minutes):
    
    ave = np.linspace(0,86400,1440/minutes)
    t_ave = []
    x_ave = []
    for j in range(len(ave)-1):
        x_ave.append([])
        t_ave.append((ave[j] + ave[j+1])/2)
        for i in range(len(t)):
            if ave[j] < t[i] < ave[j+1]:
                x_ave[j].append(x[i])
                
    temp = []
    for i in x_ave:
        temp.append(np.nanmean(i))
    x_ave = temp
    
    return t_ave, x_ave
    
def month_average_temperature(year_month,t_datetime,data,minutes):
    
    #data is temperature
    
    index = []
    days = []
    for i in range(len(t_datetime)):
        if (t_datetime[i].year,t_datetime[i].month) == (year_month):
            if t_datetime[i].day not in days:
                days.append(i)
            index.append(i)
    
    t_ref = datetime(year_month[0],year_month[1],1,0,0,0)
    timeAK = pytz.timezone('America/Anchorage')
    t_ref = timeAK.localize(t_ref)
    
    ave = []
    for i in index:
        ave.append(((t_datetime[i].timestamp() - t_ref.timestamp()) % 86400,data[i]))
        
    ave.sort()
    t_ave = []
    temp_ave = []
    for i in ave:
        t_ave.append(i[0])
        temp_ave.append(i[1])
    
    t_ave = np.array(t_ave)
    temp_ave = np.array(temp_ave)
    
    t_ave,temp_ave = day_average_temperature(t_ave,temp_ave,minutes)
    
    t_ave = np.array(t_ave)
    temp_ave = np.array(temp_ave)
    
    return t_ave, temp_ave

def monthly_average_temperature(year_month,t_datetime,temp):
    
    index = []
    for i in range(len(t_datetime)):
        if (t_datetime[i].year,t_datetime[i].month) == (year_month):
            index.append(i)
    
    return np.nanmean(np.array(temp)[index])