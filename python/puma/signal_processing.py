"""
Signal Processing Functions for PuMA

By Doug Keller
"""

import scipy.stats as stats
import numpy as np
from datetime import datetime
import pytz

def moving_median(f,N):
    """
    Returns the moving median array of an array.
    
    Arguments:
        f -- 1D numpy array of numbers
        N -- median filter order
        
    Returns:
        mm -- moving median filtered array
        
    This function is a moving median filter that runs over a window of 2N + 1 elements along an n element long array with the given N order. The window is centered on the n element and the median of the window replaces the n element. The elements within N elements of the end points are treated slightly differently with a reduced window size.
    """
    
    mm = np.zeros(f.size)
    
    for i in range(f.size): #running the median filter window
        if i < N:
            m = []
            for j in range(i+N+1):
                if np.isfinite(f[j]):
                    m.append(f[j])
            m = np.array(m)
            mm[i] = np.median(m)
        elif i+N > f.size-1:
            m = []
            for j in range(i-N,f.size):
                if np.isfinite(f[j]):
                    m.append(f[j])
            m = np.array(m)
            mm[i] = np.median(m)
        else:
            mm[i] = np.median(f[i-N:i+N+1][np.where(np.isfinite(f[i-N:i+N+1]))[0]])
        
    return mm

def linear_regression2line(x,y):
    """
    Returns the linear regression info and line from a given function.
    
    Arguments:
        x -- independent variable array
        y -- dependent variable array
        
    Returns:
        x_line -- beginning and end points of the x array
        y_line -- beginning and end points of the linear regression line based on the y array at the x_line locations
        slope -- slope of the linear regression line
        intercept -- intercept of the linear regression line
        rvalue -- r value of the linear regression line
        
    This function takes the dependent and independent arrays of a function set and produces the components and plot information of the linear regression of the data for easy plotting and labelling.
    """
    
    linreg = stats.linregress(x,y) #linear regression performed
    
    def line(linreg,x): #forming linear regression equation to be applied
        return linreg[0]*x + linreg[1]
    
    x_line = np.array([np.nanmin(x),np.nanmax(x)]) #setting the return values
    y_line = np.array([line(linreg,x_line[0]),line(linreg,x_line[1])])
    slope = linreg[0]
    intercept = linreg[1]
    rvalue = linreg[2]
    
    return x_line, y_line, slope, intercept, rvalue

def day_average(t_datetime,data,minutes):
    """
    Returns the day averaged data in "minutes" minute windows.
    
    Arguments:
        t_datetime -- datetime object list
        data -- list of the data to be averaged
        minutes -- number of minutes for a window
        
    Returns:
        t_datetime_ave -- averaged datetime object list
        data_ave -- averaged list of data
        
    This function takes a list of data and compresses into an overlapping day of data. Then the data is averaged over windows of info of length "minutes." This is used in the polar plots to look at the hourly variation over a month.
    """
    
    ave = np.linspace(0,86400,1440/minutes)
    t_datetime_ave = []
    data_ave = []
    for j in range(len(ave)-1): #making a list of windowed data
        data_ave.append([])
        data_ave.append((ave[j] + ave[j+1])/2)
        for i in range(len(t_datetime)):
            if ave[j] < t_datetime[i] < ave[j+1]:
                data_ave[j].append(data[i])
                
    temp = []
    for i in data_ave: #averaging the windowed data
        temp.append(np.nanmean(i))
    data_ave = temp
    
    return t_datetime_ave, data_ave

def month_average(year_month,t_datetime,data,minutes):
    """
        Returns the day averaged data in "minutes" minute windows.
    
    Arguments:
        year_month -- year and month tuple e.g. (2019,9)
        t_datetime -- datetime object list
        data -- list of the data to be averaged
        minutes -- number of minutes for a window
        
    Returns:
        t_datetime_ave -- averaged datetime object list
        temp_ave -- averaged list of data
        
    This function takes a list of data and compresses into an overlapping day of data by calling the day_average function over a month of data. Then the data is averaged over windows of info of length "minutes." This is used in the polar plots to look at the hourly variation over a month.
    """
    
    index = []
    days = []
    for i in range(len(t_datetime)):
        if (t_datetime[i].year,t_datetime[i].month) == (year_month):
            if t_datetime[i].day not in days:
                days.append(i)
            index.append(i)
    
    t_ref = datetime(year_month[0],year_month[1],1,0,0,0) #making reference datetime object
    timeAK = pytz.timezone('America/Anchorage')
    t_ref = timeAK.localize(t_ref)
    
    ave = []
    for i in index: #separating the t_datetime into days with the data
        ave.append(((t_datetime[i].timestamp() - t_ref.timestamp()) % 86400,data[i]))
        
    ave.sort()
    t_datetime_ave = []
    temp_ave = []
    for i in ave: 
        t_datetime_ave.append(i[0])
        temp_ave.append(i[1])
    
    t_datetime_ave = np.array(t_datetime_ave)
    temp_ave = np.array(temp_ave)
    
    t_datetime_ave,temp_ave = day_average(t_datetime_ave,temp_ave,minutes) #running the window averaging function
    
    t_datetime_ave = np.array(t_datetime_ave)
    temp_ave = np.array(temp_ave)
    
    return t_datetime_ave, temp_ave