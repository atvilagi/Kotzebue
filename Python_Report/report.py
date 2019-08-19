#File to create a monthly report
    
def monthly_report(unified_nc_file,stove,year_month):
    
    uni_nc = Dataset(unified_nc_file,'r')

    stove_comp_months = prep.run_complete_months(unified_nc_file)
    good_stoves = prep.good_neighbor_stoves(stove,year_month,stove_comp_months)
    neighbor_stoves = prep.find_neighbor_stoves(stove,good_stoves)
    
    time = uni_nc[mystove+'/Event/Clicks']['time'][:]
    dtime = prep.timestamp2datetime(time)
    rtime = uni_nc[mystove+'/Raw']['time'][:]
    rdtime = prep.timestamp2datetime(rtime)
    outT = uni_nc[mystove+'/Event/Clicks']['outdoor_temp'][:]
    gallons = uni_nc[mystove+'/Event/Clicks']['fuel_consumption'][:]
    gph = uni_nc[mystove+'/Event/Clicks']['fuel_consumption_rate'][:]
    days_active = prep.days_available_in_month(year_month,rdtime)
    hdd = prep.heat_degree_day(dtime,outT,65)
    months,gphddpd = prep.weather_adjusted_gallons_per_day_per_month(rdtime,dtime,gallons,hdd)
    months,gphddpd = prep.weather_adjusted_gallons_consumed_range(year_month,months,gphddpd)
    
    Neighbor_Usage = prep.neighbor_gallons_consumed_per_month(year_month,unified_nc_file,neighbor_stoves)
    Total_Usage = prep.gallons_consumed_per_month(year_month,dtime,gallons)
#    Fuel_Price = float(input('Current price of fuel: '))
    Fuel_Price = float(3.00)
    Total_Cost = Total_Usage*Fuel_Price
    Fuel_per_Day = Total_Usage/days_active
    Fuel_Cost_per_Day = Total_Cost/days_active
    Prog_Usage = gphddpd[-1]/gphddpd[-2]
    
    prep.plot_bar_progress(months,gphddpd,'monthly_track_your_progress.png')
    prep.plot_fuel_usage(year_month,Total_Usage,Neighbor_Usage,'monthly_fuel_usage.png')
#    retrieve square footage from the puma-inventory -> stove.getattrs
    prep.polar_flow_plot_average_per_month(stove,year_month,dtime,gph,45,'monthly_polar_plot.png')
    
    prep.write_monthly_tex_var_file(year_month,Total_Usage,Fuel_Price,Fuel_per_Day,Total_Cost,Fuel_Cost_per_Day,Neighbor_Usage,Prog_Usage)

    return dtime

from netCDF4 import Dataset
import matplotlib.pyplot as plt
import os
import numpy as np
from datetime import datetime
import puma_report as prep
from pandas.plotting import register_matplotlib_converters
from calendar import monthrange

file_path = os.path.abspath(os.path.dirname(__file__))
uni_nc_file = os.path.join(file_path,'..','Data','netCDF_Files','puma_unified_data.nc')

os.chdir(os.path.join(os.path.abspath(os.path.dirname(__file__)),'..','Reports','Monthly'))

uni_nc = Dataset(uni_nc_file,'r')
stoves = list(uni_nc.groups)
stove_comp_months = prep.run_complete_months(uni_nc_file)

year_month = (2019,4)

mystove = stoves[2]

dtime = monthly_report(uni_nc_file,mystove,year_month)