"""
Time Manipulation Functions for PuMA

By Douglas Keller
"""

from datetime import datetime
import numpy as np
import pytz
import multiprocessing as mp
from calendar import monthrange
from netCDF4 import Dataset

def time2theta_time(t):
    """
    Convert seconds to daily radians.
    
    Arguments:
        t -- time in seconds
    
    Returns:
        daily radians
        
    Function that takes time in seconds and transforms them into radians with a 2 pi (full circle) equivalent to 86400 seconds (full day).
    """
    
    return np.pi/2 - t*2*np.pi/86400 #shifted so the top so that is 12:00 AM or 0:00 is at the top of a unit circle

def datetime2theta_time(t_datetime):
    """
    Convert datetime object list to daily radians numpy array.
    
    Arguments:
        t_datetime -- time in a datetime object list
        
    Returns:
        t_theta -- time in a daily radian numpy array
        
    Function that takes time in a datetime object list and transforms it into a daily radians numpy array using the time2theta_time function.
    """
    
    t = []
    for i in t_datetime: #converting datetime to seconds
        t.append(i.hour*24*3600 + i.minute*60 + i.second + i.microsecond/1e6)

    t = np.array(t)
    t_theta = time2theta_time(t) #conversion from seconds to radians
    
    return t_theta    

def timestamp2datetime(t_stamp):
    """
    Convert timestamp object list to datetime object list.
    
    Arguments:
        t_stamp -- time in a timestamp object list
        
    Returns:
        t_datetime -- time in a datetime object list
        
    Function that takes time in a timestamp object list (which is assumed to be UTC as per definition of the timestamp object) and converts it to a datetime object list with proper timezoning.
    """
    
    timeZ = pytz.timezone('UTC')
    timeAK = pytz.timezone('America/Anchorage')
    t_datetime = []
    for i in range(len(t_stamp)): #converting the t_stamp array to the datetime array with proper timezone info
        t_datetime.append(datetime.fromtimestamp(t_stamp[i]))
        t_datetime[i] = timeZ.localize(t_datetime[i])
        t_datetime[i] = t_datetime[i].astimezone(timeAK)

    return t_datetime

def months_available(t_datetime):
    """
    Finds months available in the datetime object list.
    
    Arguments:
        t_datetime -- time in a datetime object list
        
    Returns:
        months -- a list of tuples containing the months (by year) available e.g. [(2019,5),(2019,6),...]
        
    Function that finds the months that are available in the datetime object list, to determine which months have data, and then returns of list of tuples.
    """
    
    months = []
    for t in t_datetime: #determining available months and year
        if (t.year,t.month) not in months:
            months.append((t.year,t.month))
    
    return months #output structure is [(year,month),...]

def days_available(t_datetime):
    """
    Finds available days in a datetime object list.
    
    Arguments:
        t_datetime -- time in a datetime object list
        
    Returns:
        days -- a list of tuples containing the days (by month and year) available e.g. [(2019,5,1),(2019,6,2),...]
    
    Function that finds the days that are available in the datetime object list, to determine which days have data, and then returns the list of tuples.
    """
    
    days = []
    for t in t_datetime: #determining available days, months, and year
        if (t.year,t.month,t.day) not in days:
            days.append((t.year,t.month,t.day))

    return days #output structure is [(year,month,day),...]

def days_available_per_month(t_datetime):
    """
    Finds amount of available days per month in a datetime object list.
    
    Arguments:
        t_datetime -- time in a datetime object list
        
    Returns:
        month_day -- a list of lists of tuples and number of days (by month and year) available e.g. [[(2019,5),19],...]
    
    Function that determines the number of days available per month and year by calling the days_available and months_available functions with a given datetime object list.
    """
    
    days = days_available(t_datetime) #determining available days
    months = months_available(t_datetime) #determining available months
    
    month_day = []
    for i in range(len(months)): #counts days per month
        month_day.append([months[i],0])
        for j in range(len(days)):
            if days[j][0:2] == months[i]:
                month_day[i][1] += 1
                
    return month_day #output structure [[(year,month),days],...]

def days_available_in_month(year_month,t_datetime):
    """
    Returns amount of available days per month for a given year and month from a datetime object list.
    
    Arguments:
        year_month -- tuple of desired year and month e.g. (year,month)
        t_datetime -- time in a datetime object list
        
    Returns:
        count of days
        
    Function that determines the number of available days (with data) per year and month with a given year and month from a datetime object list by calling the days_available_per_month function.
    """
    
    month_day = days_available_per_month(t_datetime) #determining day count per month
    
    for t in month_day: #returning the day count for a given year and month, if it exists
        if t[0] == year_month:
            return t[1]
        
    return 0

def complete_months(stove,raw_time,result):
    """
    Multiprocess ready function returning the number of complete months in a dataset.
    
    Arguments:
        stove -- identity of desired stove
        raw_time -- time in a timestamp object list
        result -- process immune queue
        
    This function is a multiprocess ready function that takes a timestamp object list and extracting the complete months in a dataset where all the days of the month have some data. This function is expected to be called by the run_complete_months function.
    """
    
    t_datetime = timestamp2datetime(raw_time) #getting the t_datetime object list
    days = days_available(t_datetime) #days available per month and year
    months = months_available(t_datetime) #months available per year
    
    temp = []
    for i in range(len(months)): #placing the day count in a temporary list
        temp.append([])
        for day in days:
            if day[0:2] == months[i]:
                temp[i].append(day)
    
    complete = []
    for i in range(len(temp)): #determining the complete months in the data
        last_day = monthrange(temp[i][-1][0],temp[i][-1][1])[1]
        if temp[i][0][2] == 1 and temp[i][-1][2] == last_day and len(temp[i]) == last_day:
            complete.append(temp[i][0][0:2])
    
    result.put((stove,complete)) #pushing the result into a process safe queue in the form of (stove,complete_month_list)

def run_complete_months(uni_nc_file):
    """
    Multiprocessed function that returns the months that have complete data for a stove.
    
    Arguments:
        uni_nc_file -- string of the filename containing the unified netCDF file of the unified stove dataset
        
    Returns:
        results -- list of tuples of stove and complete months e.g. [(FBK003,[5,6,7]),...]
        
    A multiprocessed function that returns the number of months that have a complete set of data for all the stoves in the uni_nc_file.
    """
    
    uni_nc = Dataset(uni_nc_file,'r')
    stoves = list(uni_nc.groups)
    
    stoves_time = []
    for stove in stoves: 
        stoves_time.append(uni_nc[stove+'/Raw/time'][:])
        
    result = mp.Manager().Queue()
    pool = mp.Pool(mp.cpu_count())        
    for i in range(len(stoves)): #running complete_months function for all the stoves
        pool.apply_async(complete_months,args=(stoves[i],stoves_time[i],result))
    pool.close()
    pool.join()
    results = []
    
    while not result.empty(): #popping the results out of the process safe queue and into a list
        results.append(result.get())
        
    results.sort()
    
    return results #output structure [(stove,complete_month_list),...]

def year_month2datetime(year_month):
    """
    Returns the datetime object of the given year month tuple.
    
    Arguments:
        year_month -- tuple containing the desired year and month
        
    Returns:
        t_datetime -- datetime object
        
    Function that takes a given year and month tuple and returns a datetime object of that given year and month at the beginning of the month.
    """
    
    timeAK = pytz.timezone('America/Anchorage')
    t_datetime = timeAK.localize(datetime(year_month[0],year_month[1],1,0,0,0))
    
    return t_datetime

def run_year_month2datetime(year_months):
    """
    Returns a list of datetime objects of the given list of tuples of desired years and months.
    
    Arguments:
        year_months -- a list of tuples of year and months e.g. [(2019,9),...]
    
    Returns:
        ymdtime -- a list of datetime objects
        
    Function that runs the year_month2datetime function for a list of desired year and month tuples and returns a list of datetime objects at the beginning of each given month.
    """
    
    ymdtime = []
    for m in year_months: #running the year_month2datetime function for the given year month tuples
        ymdtime.append(year_month2datetime(m))
        
    return ymdtime

def days_in_month(year_month):
    """
    """
    
    return monthrange(year_month[0],year_month[1])[1]

def years_months(begin_year_month,end_year_month):
    
    year_months = []
    
    y = begin_year_month[0]
    m = begin_year_month[1]
    while y <= end_year_month[0]:
        while m <= 12:
            if (y,m) <= end_year_month:
                year_months.append((y,m))
                m += 1
            else:
                m = 13
        m = 1
        y += 1
        
    return year_months
                    
                
    
        