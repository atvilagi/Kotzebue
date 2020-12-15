"""
Temperature Functions for PuMA

By Doug Keller
"""

import numpy as np
import pandas as pd

BASE = 65
def heat_degree_day(Tcolumn):
    """
    Returns a list of the heating degree day from an outdoor temperature list
    
    params:
        df is a pandas dataframe with datetime index and field named 'outT' which contains outdoor temperature in Fahrenheit
        base -- temperature base for the heating degree day value e.g. 65 for 65 degrees Fahrenheit
        column: the string name of the column containing temperature data
        
    Returns:
        hdd -- pandas dataframe of temperature and heating degree day values arranged by day
        
    This function provides the heating degree day value of a given list of outdoor temperature data
     (in Fahrenheit) with an accompanying datetime object list, needed for the definition of a heating degree day (https://www.weather.gov/key/climate_heat_cool).
    """
    Temp = Tcolumn.groupby(pd.Grouper(freq = 'D')).mean()
    hdd = BASE - Temp
    hdd.name='hdd'

    return hdd

def daily_average_temperature(df,column):
    '''Returns the average temperature over a day.

    param: df is a pandas dataframe with the column to average by day
    param: column is the string name of the temperature column to average by day

    Returns:
        dataframe of the average by day

    This functino returns a dataframe of the average value by day
    '''
    
    dailydf = df[column].resample('1D').ohlc()
    dailydf.index = dailydf.index.date #get rid of hours portion of datetime
    dailydf = dailydf.drop(['open', 'close'], 1)
    dailydf[column] = dailydf.mean(1)

    return dailydf

def monthly_average_temperature(df,column):
    """
    Returns the average temperature over a month.
    
    param: df is a pandas dataframe with the column to average by month
    param: column is the string name of the temperature column to average by month
        
    Returns:
        dataframe of the average by month
        
    This function returns the average temperature of the temp list of the desired month
    given by the year_month tuple. Used for the monthly reports.
    """

    monthlydf = df.groupby(df.index.to_period('M')).agg({column: 'mean'})
    
    return monthlydf