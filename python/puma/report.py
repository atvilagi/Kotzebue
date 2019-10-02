#Functions for making the reports

import os
import sys

file_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(file_path,'..'))

from netCDF4 import Dataset
import numpy as np
import puma.plot as pplot
import puma.time as ptime
import puma.tex as ptex
import puma.fuel as pfuel
import puma.temperature as ptemp

def monthly_report(unified_nc_file,stove,year_month,begin_year_month,end_year_month,year_months,fuel_price,control_stoves,tip_no,Name,Address):

    try:
        os.mkdir(stove)
    except:
        pass
    
    uni_nc = Dataset(unified_nc_file,'r')
    stove_area = float(uni_nc[stove].getncattr('Square Footage'))
    uni_nc.close()
    
    t_datetime,r_t_datetime,inT,outT,gallons,gph = pre_monthly_data(begin_year_month,year_month,unified_nc_file,stove)
    
    if stove == 'FBK017':
        
        inT = list(inT)
        outT = list(outT)
        gallons = list(gallons)
        gph = list(gph)
    
        t_datetime_x,r_t_datetime_x,inT_x,outT_x,gallons_x,gph_x = pre_monthly_data(begin_year_month,end_year_month,unified_nc_file,'FBK018')
        
        t_datetime += t_datetime_x
        r_t_datetime += r_t_datetime_x
        
        inT_x = list(inT_x)
        outT_x = list(outT_x)
        gallons_x = list(gallons_x)
        gph_x = list(gph_x)
        
        inT += inT_x
        outT += outT_x
        gallons += gallons_x
        gph += gph_x
        
        inT = np.array(inT)
        outT = np.array(outT)
        gallons = np.array(gallons)
        gph = np.array(gph)
        
        Stove_ID = 'FBK017-FBK018'
    else:
        Stove_ID = stove
        
    gphddpm,neighbor_area = calculated_monthly_data(unified_nc_file,stove,year_month,t_datetime,r_t_datetime,outT,gallons,control_stoves)

    days = ptime.days_in_month(year_month)

    Tip_No = tip_no
    
    InT_Ave = ptemp.monthly_average_temperature(year_month,t_datetime,inT)
    
    OutT_Ave = ptemp.monthly_average_temperature(year_month,t_datetime,outT)    

    Neighbor_Usage = pfuel.neighbor_gallons_consumed_per_month(year_month,unified_nc_file,control_stoves)
    
    Neighbor_Usage_per_Area = pfuel.gallons_consumed_per_area(Neighbor_Usage,neighbor_area)
    
    Total_Usage = pfuel.gallons_consumed_per_month(year_month,t_datetime,gallons)
    
    Total_Usage_per_Area = pfuel.gallons_consumed_per_area(Total_Usage,stove_area)

    Fuel_Price = fuel_price
    
    Total_Cost = Total_Usage*Fuel_Price
    
    Fuel_per_Day = Total_Usage/days

    Fuel_Cost_per_Day = Total_Cost/days
    
    if len(gphddpm) > 1:
        Prog_Usage = gphddpm[-1]/gphddpm[-2]
    else:
        Prog_Usage = 0
    
    for i in range(len(year_months)):
        try:
            gphddpm[i]
        except:
            gphddpm.append(0)
            
    os.chdir(stove)

    pplot.plot_bar_progress(year_months,gphddpm,Fuel_Price,'monthly_track_your_progress.png')
    pplot.plot_fuel_usage(year_month,Total_Usage_per_Area,Neighbor_Usage_per_Area,'monthly_fuel_usage.png')
    pplot.polar_flow_plot_average_per_month(stove,year_month,t_datetime,gph,60,'monthly_polar_plot.png')
    
    ptex.write_monthly_tex_var_file(year_month,Total_Usage,Fuel_Price,Fuel_per_Day,Total_Cost,Fuel_Cost_per_Day,Neighbor_Usage,Prog_Usage,Stove_ID,InT_Ave,OutT_Ave,Tip_No,Name,Address)
    ptex.write_monthly_tex_report_file()
    
    os.chdir('..')
    print(Stove_ID)
    
def pre_monthly_data(begin_year_month,end_year_month,unified_nc_file,stove):
    
    uni_nc = Dataset(unified_nc_file,'r')
    
    time = uni_nc[stove+'/Event/Clicks']['time'][:]
    t_datetime = ptime.timestamp2datetime(time)
    r_time = uni_nc[stove+'/Raw']['time'][:]
    r_t_datetime = ptime.timestamp2datetime(r_time)
    
    index = wanted_data(begin_year_month,end_year_month,t_datetime)
    r_index = wanted_data(begin_year_month,end_year_month,r_t_datetime)
    
    time = time[index]
    t_datetime = t_datetime[index[0]:index[-1]+1]
    r_time = r_time[r_index]
    r_t_datetime = r_t_datetime[r_index[0]:r_index[-1]+1]
    
    inT = uni_nc[stove+'/Event/Clicks']['indoor_temp'][index]
    outT = uni_nc[stove+'/Event/Clicks']['outdoor_temp'][index]
    gallons = uni_nc[stove+'/Event/Clicks']['fuel_consumption'][index]
    gph = uni_nc[stove+'/Event/Clicks']['fuel_consumption_rate'][index]
    
    return t_datetime,r_t_datetime,inT,outT,gallons,gph

def wanted_data(begin_year_month,end_year_month,t_datetime):
    
    index = []
    for i in range(len(t_datetime)):
        if begin_year_month <= (t_datetime[i].year,t_datetime[i].month) <= end_year_month:
            index.append(i)
            
    return index

def calculated_monthly_data(unified_nc_file,stove,year_month,t_datetime,r_t_datetime,outT,gallons,control_stoves):
    
    neighbor_area = pfuel.neighbor_area(control_stoves,unified_nc_file)
    
    hdd = ptemp.heat_degree_day(t_datetime,outT,65)
    gphddpm = pfuel.run_weather_adjusted_gallons_per_month(r_t_datetime,t_datetime,gallons,hdd)
    
    return gphddpm,neighbor_area
    
#def calculated_monthly_data(unified_nc_file,stove,year_month,t_datetime,r_t_datetime,outT,gallons):
#    
#    stove_comp_months = ptime.run_complete_months(unified_nc_file)
#    good_stoves = pfuel.good_neighbor_stoves(stove,year_month,stove_comp_months)
#    neighbor_stoves = pfuel.find_neighbor_stoves(stove,good_stoves)
#    neighbor_area = pfuel.neighbor_area(neighbor_stoves,unified_nc_file)
#    
#    hdd = ptemp.heat_degree_day(t_datetime,outT,65)
#    months,gphddpm = pfuel.run_weather_adjusted_gallons_per_month(r_t_datetime,t_datetime,gallons,hdd)
#    months,gphddpm = pfuel.weather_adjusted_gallons_consumed_range(year_month,months,gphddpm)
#    days_active = ptime.days_available_in_month(year_month,r_t_datetime)
#    
#    return hdd,gphddpm,neighbor_area,neighbor_stoves,days_active,months