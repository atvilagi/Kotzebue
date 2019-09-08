#Time Manipulation Functions for PuMA

#By Douglas Keller

from datetime import datetime
import numpy as np
import pytz
import multiprocessing as mp
from calendar import monthrange
from netCDF4 import Dataset

def time2theta_time(t):
    #expecting t in seconds
    
    return np.pi/2 - t*2*np.pi/86400 #shifted so the top of the plot is 12:00 AM

def datetime2theta_time(t_datetime):
    
    t = []
    for i in t_datetime:
        t.append(i.hour*24*3600 + i.minute*60 + i.second + i.microsecond/1e6)

    t = np.array(t)
    t_theta = time2theta_time(t)
    
    return t_theta    

def timestamp2datetime(t_stamp):
    
    timeZ = pytz.timezone('UTC')
    timeAK = pytz.timezone('America/Anchorage')
    t_datetime = []
    for i in range(len(t_stamp)):
        t_datetime.append(datetime.fromtimestamp(t_stamp[i]))
        t_datetime[i] = timeZ.localize(t_datetime[i])
        t_datetime[i] = t_datetime[i].astimezone(timeAK)

    return t_datetime

def months_available(t_datetime):
    
    months = []
    for t in t_datetime:
        if (t.year,t.month) not in months:
            months.append((t.year,t.month))
    
    return months

def days_available(t_datetime):
    
    days = []
    for t in t_datetime:
        if (t.year,t.month,t.day) not in days:
            days.append((t.year,t.month,t.day))

    return days

def days_available_per_month(t_datetime):
    
    days = days_available(t_datetime)
    months = months_available(t_datetime)
    month_day = []
    for i in range(len(months)):
        month_day.append([months[i],0])
        for j in range(len(days)):
            if days[j][0:2] == months[i]:
                month_day[i][1] += 1
                
    return month_day

def days_available_in_month(year_month,t_datetime):
    
    month_day = days_available_per_month(t_datetime)
    for t in month_day:
        if t[0] == year_month:
            return t[1]
        
    return 0

def complete_months(stove,raw_time,result):
    
    t_datetime = timestamp2datetime(raw_time)
    days = days_available(t_datetime)
    months = months_available(t_datetime)
    
    temp = []
    for i in range(len(months)):
        temp.append([])
        for day in days:
            if day[0:2] == months[i]:
                temp[i].append(day)
    
    complete = []
    for i in range(len(temp)):
        last_day = monthrange(temp[i][-1][0],temp[i][-1][1])[1]
        if temp[i][0][2] == 1 and temp[i][-1][2] == last_day and len(temp[i]) == last_day:
            complete.append(temp[i][0][0:2])
    
    result.put((stove,complete))

def run_complete_months(uni_nc_file):
    
    uni_nc = Dataset(uni_nc_file,'r')
    stoves = list(uni_nc.groups)
    
    stoves_time = []
    for stove in stoves:
        stoves_time.append(uni_nc[stove+'/Raw/time'][:])
        
    result = mp.Manager().Queue()
    pool = mp.Pool(mp.cpu_count())        
    for i in range(len(stoves)):
        pool.apply_async(complete_months,args=(stoves[i],stoves_time[i],result))
    pool.close()
    pool.join()
    results = []
    
    while not result.empty():
        results.append(result.get())
        
    results.sort()
    
    return results

def year_month2datetime(year_month):
    
    return datetime(year_month[0],year_month[1],1,0,0,0)

def run_year_month2datetime(year_months):
    
    ymdtime = []
    for m in year_months:
        ymdtime.append(year_month2datetime(m))
        
    return ymdtime