"""
Temperature Functions for PuMA

By Doug Keller
"""

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
    """
    Returns the average daily temperature in an array.
    
    Arguments:
        t_datetime -- datetime object list
        outT -- outdoor temperature list
        
    Returns:
        T_ave -- average daily temperature array
        day -- list of tuples containing the year, month, and day of the averaged temperature e.g. [(2019,9,5),...]
        
    This function returns the daily temperature average based on the average of the daily high and low of the diurnal temperature swing. The time information is also returned in the day list.
    """
    
    day = []
    T_max = []
    T_min = []
    
    i = 0
    while i < len(t_datetime): #making the day array
        if (t_datetime[i].year,t_datetime[i].month,t_datetime[i].day) not in day:
            day.append((t_datetime[i].year,t_datetime[i].month,t_datetime[i].day))
        i += 1
    
    for i in range(len(day)):
        T_max.append(-999)
        T_min.append(999)
        
    i = 0
    while i < len(t_datetime): #finding the daily high and low
        for j in range(len(day)):
            if day[j] == (t_datetime[i].year,t_datetime[i].month,t_datetime[i].day):
                if T_max[j] < outT[i]:
                    T_max[j] = outT[i]
                if T_min[j] > outT[i]:
                    T_min[j] = outT[i]
        i += 1
    
    T_max = np.array(T_max)
    T_min = np.array(T_min)
    T_ave = (T_max + T_min)/2 #averaging the high and low to make the average temperature array
    
    return T_ave, day #output structure numpy array and [(year,month,day),...]

def monthly_average_temperature(year_month,t_datetime,temp):
    """
    Returns the average temperature array over a month.
    
    Arguments:
        year_month -- year and month tuple e.g. (2019,9)
        t_datetime -- datetime object list
        temp -- temp list
        
    Returns:
        the average temperature of the desired month.
        
    This function retures the average temperature of the temp list of the desired month given by the year_month tuple. Used for the monthly reports.
    """
    
    index = []
    for i in range(len(t_datetime)):
        if (t_datetime[i].year,t_datetime[i].month) == (year_month):
            index.append(i)
    
    return np.nanmean(np.array(temp)[index])