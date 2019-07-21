#Created: Sun Jul 21 01:59:21 2019
#By: mach

from netCDF4 import Dataset
import matplotlib.pyplot as plt
import os
import numpy as np
from datetime import datetime
import pytz

file_path = os.path.abspath(os.path.dirname(__file__))

uni_nc_file = os.path.join(file_path,'..','Data','netCDF_Files','puma_unified_data.nc')
uni_nc = Dataset(uni_nc_file,'r')

stoves = list(uni_nc.groups)

timez = pytz.timezone('America/Anchorage')

for stove in stoves:
    
    time = uni_nc[stove]['time'][:]
    t = []
    for i in range(len(time)):
        t.append(datetime.fromtimestamp(time[i]))
        t[i] = timez.localize(t[i])
        
    inT = uni_nc[stove]['indoor_temp'][:]
    
    print(time,inT)
    
theta = np.linspace(0,2*np.pi,1000)
r = np.sin(theta)

theta_loc = np.linspace(0,2*np.pi,25)*180/np.pi
theta_loc = theta_loc[0:-1]
theta_lab = []
for i in range(24):
    theta_lab.append(str(i) + ':00')

# Figure out how to determine a new day in the datetime object for making the polar plots
# Then use the .seconds feature per 86400 seconds to determine a full day (or use datetime)
plt.polar(theta,r)
plt.thetagrids(theta_loc,labels = theta_lab)
plt.show()