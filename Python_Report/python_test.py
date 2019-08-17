#Created: Sun Jul 21 01:59:21 2019
#By: mach

#time = uni_nc[stove+'/Event/Clicks']['time'][:]
#clicks = uni_nc[stove+'/Event/Clicks']['clicks'][:]
#gallons = uni_nc[stove+'/Event/Clicks']['fuel_consumption'][:]
#gph = uni_nc[stove+'/Event/Clicks']['fuel_consumption_rate'][:]
    
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import os
import numpy as np
from datetime import datetime
import puma_report as prep
from pandas.plotting import register_matplotlib_converters

file_path = os.path.abspath(os.path.dirname(__file__))
uni_nc_file = os.path.join(file_path,'..','Data','netCDF_Files','puma_unified_data.nc')
uni_nc = Dataset(uni_nc_file,'r')
stoves = list(uni_nc.groups)
stove_comp_months = prep.run_complete_months(uni_nc_file)

month = (2019,5)

mystove = stoves[2]

rtime = uni_nc[mystove+'/Raw/time'][:]
rdtime = prep.timestamp2datetime(rtime)
time = uni_nc[mystove+'/Event/Clicks']['time'][:]
dtime = prep.timestamp2datetime(time)
clicks = uni_nc[mystove+'/Event/Clicks']['clicks'][:]
gallons = uni_nc[mystove+'/Event/Clicks']['fuel_consumption'][:]
gph = uni_nc[mystove+'/Event/Clicks']['fuel_consumption_rate'][:]

gs = prep.good_neighbor_stoves(mystove,month,stove_comp_months)

ns = prep.find_neighbor_stoves(mystove,gs)

sumgal = prep.gallons_consumed_per_month(month,dtime,gallons)

nsg = prep.neighbor_gallons_consumed_per_month(month,uni_nc_file,ns)
print(nsg)