#Created: Mon Aug 12 10:56:53 2019
#By: mach

from netCDF4 import Dataset
import matplotlib.pyplot as plt
import os
import numpy as np
from datetime import datetime
import pytz
import puma_plot as pplot
from pandas.plotting import register_matplotlib_converters

timeAK = pytz.timezone('America/Anchorage')

file_path = os.path.abspath(os.path.dirname(__file__))

uni_nc_file = os.path.join(file_path,'..','Data','netCDF_Files','puma_unified_data.nc')
uni_nc = Dataset(uni_nc_file,'r')

stoves = list(uni_nc.groups)
    
#stove = stoves[2]
for stove in stoves:
    print(stove)
    
    state = uni_nc[stove+'/Event/Clicks']['state'][:]
    time = uni_nc[stove+'/Event/Clicks']['time'][:]
    clicks = uni_nc[stove+'/Event/Clicks']['clicks'][:]
    gallons = uni_nc[stove+'/Event/Clicks']['fuel_consumption'][:]
    gph = uni_nc[stove+'/Event/Clicks']['fuel_consumption_rate'][:]
    
    tdate = []
    
    for i in range(len(time)):
        tdate.append(datetime.fromtimestamp(time[i]))
    
    clicks_pos = []
    clicks_neg = []
    for i in range(len(clicks)):
        if clicks[i] >= 0:
            clicks_pos.append(clicks[i])
            clicks_neg.append(np.nan)
        else:
            clicks_neg.append(clicks[i])
            clicks_pos.append(np.nan)
    
    figtitsize = 40
    titlesize = 28
    axissize = 20
    axsize = 18
    
    plt.figure(figsize=(25,20))
    plt.suptitle(stove,fontsize=figtitsize)
    plt.subplot(211)
    plt.plot(tdate,clicks_pos,marker='o',mec = 'b',color = 'b', markeredgewidth=5,linewidth=2,label='Positive Clicks')
    plt.plot(tdate,clicks_neg,marker='o',mec = 'r',markeredgewidth=5,linewidth=2,label='Negative Clicks')
    plt.legend(fontsize=axissize)
    plt.title('Clicks per Interval over Time',fontsize=titlesize)
    plt.xlabel('Time', fontsize = axissize)
    plt.ylabel('Clicks per Interval', fontsize = axissize)
    plt.xticks(fontsize=axsize)
    plt.yticks(fontsize=axsize)
    
    plt.subplot(212)
    plt.plot(tdate,gph,marker='o',mec = 'b',linestyle='',markeredgewidth=5,linewidth=2,label='Fuel Consumption')
    plt.legend(fontsize=axissize)
    plt.title('Gallons per Hour over Time',fontsize=titlesize)
    plt.xlabel('Time', fontsize = axissize)
    plt.ylabel('Gallons per Hour', fontsize = axissize)
    plt.xticks(fontsize=axsize)
    plt.yticks(fontsize=axsize)
    plt.savefig(stove+'_probs.png')
    plt.show()
    plt.figure(clear=True)