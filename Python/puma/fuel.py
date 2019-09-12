#Fuel Consumption Rate Functions for PuMA

#By Douglas Keller

import numpy as np
from netCDF4 import Dataset
import multiprocessing as mp
import puma.time as ptime

def gallons_consumed_per_month(year_month,t_datetime,gallons):
    
    gal_ind = []   
    for i in range(len(t_datetime)):
        if (t_datetime[i].year,t_datetime[i].month) == year_month:
            gal_ind.append(i)
    
    return np.sum(np.array(gallons)[gal_ind])
    
def gallons_consumed_per_month_mp(stove,year_month,t_datetime,gallons,result):
    
    gal_ind = []   
    for i in range(len(t_datetime)):
        if (t_datetime[i].year,t_datetime[i].month) == year_month:
            gal_ind.append(i)
    
    result.put((stove,np.sum(np.array(gallons)[gal_ind])))

def neighbor_gallons_consumed_per_month(year_month,uni_nc_file,neighbor_stoves):
    
    uni_nc = Dataset(uni_nc_file,'r')
    
    stove_dtime = []
    stove_gal = []
    for stove in neighbor_stoves:
        stove_dtime.append(ptime.timestamp2datetime(uni_nc[stove+'/Event/Clicks/time'][:]))
        stove_gal.append(uni_nc[stove+'/Event/Clicks/fuel_consumption'][:])
        
    result = mp.Manager().Queue()
    pool = mp.Pool(mp.cpu_count())        
    for i in range(len(neighbor_stoves)):
        pool.apply_async(gallons_consumed_per_month_mp,
                         args=(neighbor_stoves[i],year_month,stove_dtime[i],stove_gal[i],result))
    pool.close()
    pool.join()
    results = []
    
    while not result.empty():
        results.append(result.get())
    
    neighbor_gal = []
    for res in results:
        neighbor_gal.append(res[1])
    
    return np.nanmean(np.array(neighbor_gal))

def gallons_consumed_per_area(gallons,area):
    
    return gallons/area

def gallons_per_day_per_month(t_datetime,gallons):
    
    months = ptime.months_available(t_datetime)    
    gpm = []
    for m in months:
        gpm.append(gallons_consumed_per_month(m,t_datetime,gallons))
    
    gpd = []
    for i in range(len(gpm)):
        gpd.append(gpm[i]/ptime.days_available_in_month(months[i],t_datetime))
        
    return months, gpd

def gallons_per_heating_degree_day(gallons,hdd):
    
    gphdd = []
    for i in range(len(gallons)):
        gphdd.append(gallons[i]/hdd[i])
        
    return gphdd

def weather_adjusted_gallons_consumed_per_month(year_month,t_datetime,gphdd):
    
    gal_ind = []   
    for i in range(len(t_datetime)):
        if (t_datetime[i].year,t_datetime[i].month) == year_month:
            gal_ind.append(i)
    
    return np.sum(np.array(gphdd)[gal_ind])

def run_weather_adjusted_gallons_per_month(raw_t_datetime,t_datetime,gallons,hdd):
    
    gphdd = gallons_per_heating_degree_day(gallons,hdd)
    months = ptime.months_available(t_datetime)
    gphddpm = []
    for m in months:
        gphddpm.append(weather_adjusted_gallons_consumed_per_month(m,t_datetime,gphdd))
    
    return months, gphddpm
        
def weather_adjusted_gallons_per_day_per_month(raw_t_datetime,t_datetime,gallons,hdd):
    
    gphdd = gallons_per_heating_degree_day(gallons,hdd)
    months = ptime.months_available(t_datetime)
    gphddpm = []
    for m in months:
        gphddpm.append(weather_adjusted_gallons_consumed_per_month(m,t_datetime,gphdd))
    
    gphddpd = []
    for i in range(len(gphddpm)):
        if ptime.days_available_in_month(months[i],raw_t_datetime) <= 0:
            gphddpd.append(0)
        else:
            gphddpd.append(gphddpm[i]/ptime.days_available_in_month(months[i],raw_t_datetime))
        
    return months, gphddpd

def weather_adjusted_gallons_consumed_range(year_month,months,gphddpd):
    
    new_months = []
    new_gphddpd = []
    end = 0
    for i in range(len(months)):
        if months[i] == year_month:
            end = i
    
    i = 0
    while i <= end:
        new_months.append(months[i])
        new_gphddpd.append(gphddpd[i])
        i+=1
        
    return new_months, new_gphddpd

def find_neighbor_stoves(main_stove,good_stoves):
    
    neighbor_stoves = []
    for stove in good_stoves:
        if stove != main_stove:
            neighbor_stoves.append(stove)
    
    return neighbor_stoves

def good_neighbor_stoves(stove,month,stove_comp_months):
    
    good_stoves = []
    for scm in stove_comp_months:
        if month in scm[1]:
            good_stoves.append(scm[0])
            
    return good_stoves

def neighbor_area(neighbor_stoves,uni_nc_file):
    
    uni_nc = Dataset(uni_nc_file,'r')
    
    area = []
    for stove in neighbor_stoves:
        area.append(float(uni_nc[stove].getncattr('Square Footage')))
        
    return np.nanmean(np.array(area))