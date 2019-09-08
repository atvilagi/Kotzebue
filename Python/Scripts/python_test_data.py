#Created: Wed Sep  4 17:19:05 2019
#By: mach
    
import sys
import os

file_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(file_path,'..'))

from netCDF4 import Dataset
import matplotlib.pyplot as plt
import puma.data as pdata
import puma.temperature as ptemp
import puma.signal_processing as psp
import puma.time as ptime

uni_nc_file = os.path.join(file_path,'..','..','Data','netCDF_Files','puma_unified_data.nc')
uni_nc = Dataset(uni_nc_file,'r')

stoves = list(uni_nc.groups)

p = 0
m = 0
for stove in stoves:
    
    test_data = uni_nc[stove + '/Event/Clicks']
    
    clicks = test_data['clicks'][:]
    pos = pdata.positive_clicks(clicks)
    
    g = test_data['fuel_consumption'][pos]
    dT = test_data['delta_temp'][pos]
    
    lx,ly,slope,inter,r = psp.linear_regression2line(dT,g)
    plt.plot(dT,g,'o')
    plt.plot(lx,ly)
    plt.show()
    print(slope)
    if slope > 0:
        p += 1
    else:
        m += 1

print(p,m)
    
    #outT = test_data['outdoor_temp'][pos]
    #t = test_data['time'][pos]
    #dtime = ptime.timestamp2datetime(t)
    #hdd = ptemp.heat_degree_day(dtime,outT,65)
    #
    #lx,ly,_,_,_ = psp.linear_regression2line(hdd,gph)
    #plt.plot(hdd,gph,'o')
    #plt.plot(lx,ly)
    #plt.show()