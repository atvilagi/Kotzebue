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

def monthly_report(unified_nc_file,stove,year_month,begin_year_month,end_year_month,year_months,fuel_price,control_stoves,tip_no):

    try:
        os.mkdir(stove)
    except:
        pass
    
    uni_nc = Dataset(unified_nc_file,'r')
    stove_area = float(uni_nc[stove].getncattr('Square Footage'))
    uni_nc.close()
    
    t_datetime,outT,gallons,gph,t_t_datetime,t_inT,t_outT = pre_monthly_data(begin_year_month,year_month,unified_nc_file,stove)
    
    if stove == 'FBK017':
        
        t_inT = list(t_inT)
        t_outT = list(t_outT)
        outT = list(outT)
        gallons = list(gallons)
        gph = list(gph)
    
        t_datetime_x,outT_x,gallons_x,gph_x,t_t_datetime_x,t_inT_x,t_outT_x = pre_monthly_data(begin_year_month,end_year_month,unified_nc_file,'FBK018')
        
        t_datetime += t_datetime_x
        t_t_datetime += t_t_datetime_x
        
        t_inT_x = list(t_inT_x)
        t_outT_x = list(t_outT_x)
        outT_x = list(outT_x)
        gallons_x = list(gallons_x)
        gph_x = list(gph_x)
        
        t_inT += t_inT_x
        t_outT += t_outT_x
        outT += outT_x
        gallons += gallons_x
        gph += gph_x
        
        t_inT = np.array(t_inT)
        t_outT = np.array(t_outT)
        outT = np.array(outT)
        gallons = np.array(gallons)
        gph = np.array(gph)
        
        Stove_ID = 'FBK017-FBK018'
    else:
        Stove_ID = stove
        
    gphddpm,neighbor_area = calculated_monthly_data(unified_nc_file,stove,year_month,t_datetime,outT,gallons,control_stoves)

    days = ptime.days_in_month(year_month)

    Tip_No = tip_no
    
    InT_Ave = ptemp.monthly_average_temperature(year_month,t_t_datetime,t_inT)

    OutT_Ave = ptemp.monthly_average_temperature(year_month,t_t_datetime,t_outT)    

    Neighbor_Usage = pfuel.neighbor_gallons_consumed_per_month(year_month,unified_nc_file,control_stoves)
    
    Neighbor_Usage_per_Area = pfuel.gallons_consumed_per_area(Neighbor_Usage,neighbor_area)
    
    Total_Usage = pfuel.gallons_consumed_per_month(year_month,t_datetime,gallons)
    
    Total_Usage_per_Area = pfuel.gallons_consumed_per_area(Total_Usage,stove_area)

    Fuel_Price = fuel_price
    
    Total_Cost = Total_Usage*Fuel_Price
    
    Fuel_per_Day = Total_Usage/days

    Fuel_Cost_per_Day = Total_Cost/days
    
    if len(gphddpm) > 1:
        Prog_Usage = (gphddpm[-1] - gphddpm[-2])/gphddpm[-2]
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
    
    ptex.write_monthly_tex_var_file(year_month,Total_Usage,Total_Usage_per_Area,Fuel_Price,Fuel_per_Day,Total_Cost,Fuel_Cost_per_Day,Neighbor_Usage_per_Area,Prog_Usage,Stove_ID,InT_Ave,OutT_Ave,Tip_No)
    ptex.write_monthly_tex_report_file(stove,year_month,year_months)
    
    os.chdir('..')
    print(Stove_ID)
    
def pre_monthly_data(begin_year_month,end_year_month,unified_nc_file,stove):
    
    uni_nc = Dataset(unified_nc_file,'r')
    
    time = uni_nc[stove+'/Event/Clicks']['time'][:]
    t_datetime = ptime.timestamp2datetime(time)
    t_time = uni_nc[stove+'/Time']['time'][:]
    t_t_datetime = ptime.timestamp2datetime(t_time)
    
    index = wanted_data(begin_year_month,end_year_month,t_datetime)
    t_index = wanted_data(begin_year_month,end_year_month,t_t_datetime)
    
    time = time[index]
    t_datetime = t_datetime[index[0]:index[-1]+1]
    t_time = t_time[t_index]
    t_t_datetime = t_t_datetime[t_index[0]:t_index[-1]+1]
    
    t_inT = uni_nc[stove+'/Time']['indoor_temp'][t_index]
    t_outT = uni_nc[stove+'/Time']['outdoor_temp'][t_index]
    outT = uni_nc[stove+'/Event/Clicks']['outdoor_temp'][index]
    gallons = uni_nc[stove+'/Event/Clicks']['fuel_consumption'][index]
    gph = uni_nc[stove+'/Event/Clicks']['fuel_consumption_rate'][index]
    
    return t_datetime,outT,gallons,gph,t_t_datetime,t_inT,t_outT

def wanted_data(begin_year_month,end_year_month,t_datetime):
    
    index = []
    for i in range(len(t_datetime)):
        if begin_year_month <= (t_datetime[i].year,t_datetime[i].month) <= end_year_month:
            index.append(i)
            
    return index

def calculated_monthly_data(unified_nc_file,stove,year_month,t_datetime,outT,gallons,control_stoves):
    
    neighbor_area = pfuel.neighbor_area(control_stoves,unified_nc_file)
    
    hdd = ptemp.heat_degree_day(t_datetime,outT,65)
    gphddpm = pfuel.run_weather_adjusted_gallons_per_month(t_datetime,gallons,hdd)
    
<<<<<<< HEAD
    return gphddpm,neighbor_area
=======
    return gphddpm,neighbor_area
    
#def calculated_monthly_data(unified_nc_file,stove,year_month,t_datetime,t_t_datetime,outT,gallons):
#    
#    stove_comp_months = ptime.run_complete_months(unified_nc_file)
#    good_stoves = pfuel.good_neighbor_stoves(stove,year_month,stove_comp_months)
#    neighbor_stoves = pfuel.find_neighbor_stoves(stove,good_stoves)
#    neighbor_area = pfuel.neighbor_area(neighbor_stoves,unified_nc_file)
#    
#    hdd = ptemp.heat_degree_day(t_datetime,outT,65)
#    months,gphddpm = pfuel.run_weather_adjusted_gallons_per_month(t_t_datetime,t_datetime,gallons,hdd)
#    months,gphddpm = pfuel.weather_adjusted_gallons_consumed_range(year_month,months,gphddpm)
#    days_active = ptime.days_available_in_month(year_month,t_t_datetime)
#    
#    return hdd,gphddpm,neighbor_area,neighbor_stoves,days_active,months
>>>>>>> refs/remotes/origin/master
