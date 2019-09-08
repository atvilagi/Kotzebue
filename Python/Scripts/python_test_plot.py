#Created: Sun Jul 21 01:59:21 2019
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
    
stove = stoves[2]
print(stove)

time = uni_nc[stove+'/Event/Clicks']['time'][:]
clicks = uni_nc[stove+'/Event/Clicks']['clicks'][:]
gallons = uni_nc[stove+'/Event/Clicks']['fuel_consumption'][:]
gph = uni_nc[stove+'/Event/Clicks']['fuel_consumption_rate'][:]

plt.plot(clicks)
plt.show()

#### Plotting Problems ####

#stove = stoves[2]
#print(stove)
time = uni_nc[stove+'/Raw/']['time'][:]
t_datetime = pplot.timestamp2datetime(time)
#inT = uni_nc[stove]['indoor_temp'][:]
#outT = uni_nc[stove]['outdoor_temp'][:]
#gph = uni_nc[stove]['fuel_consumption_rate'][:]
#clicks = uni_nc[stove]['clicks'][:]
#cumclicks = uni_nc[stove]['cumulative_clicks'][:]
#
#months = pplot.months_available(t_datetime)
#print(months)
#
#cumclicks = np.array(cumclicks,dtype=np.float)
#
#for i in range(len(cumclicks)):
#    if cumclicks[i] == -1:
#        cumclicks[i] = np.nan
#plt.plot(t_datetime,cumclicks)
#plt.xlabel('Time',fontsize = 20)
#plt.ylabel('Cumulative Clicks',fontsize = 20)
#plt.title('Gaps in Data: Cumulative Clicks',fontsize = 40)
#gph,_,_ = pplot.brock_improved_despike(gph,2)
##plt.plot(gph)
#plt.show()

#### Plotting Heat Degree Days ####

#hdd = pplot.heat_degree_day(t_datetime,outT)
#pplot.plot_heating_degree_days(stove,t_datetime,gph,hdd,'test_hdd.png')

#### Plotting Polar #####

pplot.polar_flow_plot_per_month(stove,2019,2,t_datetime,gph,'test_pol.png')
pplot.polar_flow_plot_average_per_month(stove,2019,2,t_datetime,gph,30,'test_pol_ave.png')