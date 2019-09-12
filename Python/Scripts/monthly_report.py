#File to create a monthly report
    
def monthly_report(unified_nc_file,stove,year_month):
    
    try:
        os.mkdir(stove)
    except:
        pass
    
    uni_nc = Dataset(unified_nc_file,'r')

    stove_comp_months = ptime.run_complete_months(unified_nc_file)
    good_stoves = pfuel.good_neighbor_stoves(stove,year_month,stove_comp_months)
    neighbor_stoves = pfuel.find_neighbor_stoves(stove,good_stoves)
    
    time = uni_nc[stove+'/Event/Clicks']['time'][:]
    dtime = ptime.timestamp2datetime(time)
    rtime = uni_nc[stove+'/Raw']['time'][:]
    rdtime = ptime.timestamp2datetime(rtime)
    inT = uni_nc[stove+'/Event/Clicks']['indoor_temp'][:]
    outT = uni_nc[stove+'/Event/Clicks']['outdoor_temp'][:]
    gallons = uni_nc[stove+'/Event/Clicks']['fuel_consumption'][:]
    gph = uni_nc[stove+'/Event/Clicks']['fuel_consumption_rate'][:]

    Stove_ID = stove
    InT_Ave = ptemp.monthly_average_temperature(year_month,dtime,inT)
    OutT_Ave = ptemp.monthly_average_temperature(year_month,dtime,outT)
    days_active = ptime.days_available_in_month(year_month,rdtime)
    hdd = ptemp.heat_degree_day(dtime,outT,65)
    months,gphddpm = pfuel.run_weather_adjusted_gallons_per_month(rdtime,dtime,gallons,hdd)
    months,gphddpm = pfuel.weather_adjusted_gallons_consumed_range(year_month,months,gphddpm)
    neighbor_area = pfuel.neighbor_area(neighbor_stoves,unified_nc_file)
    
    Neighbor_Usage = pfuel.neighbor_gallons_consumed_per_month(year_month,unified_nc_file,neighbor_stoves)
    Neighbor_Usage_per_Area = pfuel.gallons_consumed_per_area(Neighbor_Usage,neighbor_area)
    Total_Usage = pfuel.gallons_consumed_per_month(year_month,dtime,gallons)
    Total_Usage_per_Area = pfuel.gallons_consumed_per_area(Total_Usage,float(uni_nc[stove].getncattr('Square Footage')))
#    Fuel_Price = float(input('Current price of fuel: '))
    Fuel_Price = float(3.00)
    Total_Cost = Total_Usage*Fuel_Price
    Fuel_per_Day = Total_Usage/days_active
    Fuel_Cost_per_Day = Total_Cost/days_active
    
    if len(gphddpm) > 1:
        Prog_Usage = gphddpm[-1]/gphddpm[-2]
    else:
        Prog_Usage = 'Not Enough Data'
    
    os.chdir(stove)
    
    pplot.plot_bar_progress(months,gphddpm,Fuel_Price,'monthly_track_your_progress.png')
    pplot.plot_fuel_usage(year_month,Total_Usage_per_Area,Neighbor_Usage_per_Area,'monthly_fuel_usage.png')
    pplot.polar_flow_plot_average_per_month(stove,year_month,dtime,gph,45,'monthly_polar_plot.png')
    
    ptex.write_monthly_tex_var_file(year_month,Total_Usage,Fuel_Price,Fuel_per_Day,Total_Cost,Fuel_Cost_per_Day,Neighbor_Usage,Prog_Usage,Stove_ID,InT_Ave,OutT_Ave)
    ptex.write_monthly_tex_report_file()
    
    os.chdir('..')
    
import os
import sys

file_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(file_path,'..'))

from netCDF4 import Dataset
import puma.plot as pplot
import puma.time as ptime
import puma.tex as ptex
import puma.fuel as pfuel
import puma.temperature as ptemp

uni_nc_file = os.path.join(file_path,'..','..','Data','netCDF_Files','puma_unified_data.nc')

os.chdir(os.path.join(os.path.abspath(os.path.dirname(__file__)),'..','..','Reports','Monthly'))

uni_nc = Dataset(uni_nc_file,'r')
stoves = list(uni_nc.groups)
stove_comp_months = ptime.run_complete_months(uni_nc_file)

year_month = (2019,4)
mystove = stoves[1]

monthly_report(uni_nc_file,mystove,year_month)