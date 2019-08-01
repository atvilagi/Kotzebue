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

#for stove in stoves:
#    print(stove)
#    time = uni_nc[stove]['time'][:]
#    t_datetime = pplot.timestamp2datetime(time)
#    inT = uni_nc[stove]['indoor_temp'][:]
#    gph = uni_nc[stove]['fuel_consumption_rate'][:]
#    clicks = uni_nc[stove]['clicks'][:]
#    cumclicks = uni_nc[stove]['cumulative_clicks'][:]
    
stove = stoves[2]
print(stove)
time = uni_nc[stove]['time'][:]
t_datetime = pplot.timestamp2datetime(time)
inT = uni_nc[stove]['indoor_temp'][:]
gph = uni_nc[stove]['fuel_consumption_rate'][:]
clicks = uni_nc[stove]['clicks'][:]
cumclicks = uni_nc[stove]['cumulative_clicks'][:]

for i in range(len(gph)):
    if gph[i] > 10:
        print('yikes')
        gph[i] = 0

months = pplot.months_available(t_datetime)
print(months)

#for i in range(len(clicks)):
#    print(time[i],cumclicks[i],clicks[i],gph[i])

pplot.polar_flow_plot_per_month(stove,2019,2,t_datetime,gph,'test.png')
pplot.polar_flow_plot_average_per_month(stove,2019,2,t_datetime,gph,30,'test2.png')

#for i in range(len(clicks)):
#    print(clicks[i],cumclicks[i],gph[i])

#### By day plot ####

#i,j = pplot.time_day_segment(time)
#
#t = time[i[0]:j[0]]
#inT_s = inT[i[0]:j[0]]
#gph_s = gph[i[0]:j[0]]
#
#t_s = pplot.time2timestamp(t)
#t_theta = pplot.time2theta_time(t)
#
#a = datetime(2019,2,15,0,0,0)
#a = timeAK.localize(a)
#b = t_stamp[0]
#c = a - b
#
#days,day_ind = pplot.time2days(t_s,a)
#
#t_day = t[day_ind[1]:day_ind[2]]
#t_theta = pplot.time2theta_time(t_day)
#inT_theta = inT_s[day_ind[1]:day_ind[2]]
#gph_theta = gph_s[day_ind[1]:day_ind[2]]
#
#plt.polar(t_theta,gph_theta)
#plt.show()

#### Test Plotting ####
    
#theta = np.linspace(0,2*np.pi,1000)
#r = np.sin(theta)
#
#theta_loc = np.linspace(0,2*np.pi,25)*180/np.pi
#theta_loc = theta_loc[0:-1]
#theta_lab = []
#for i in range(24):
#    theta_lab.append(str(i) + ':00')
#
## Figure out how to determine a new day in the datetime object for making the polar plots
## Then use the .seconds feature per 86400 seconds to determine a full day (or use datetime)
#plt.polar(theta,r)
#plt.thetagrids(theta_loc,labels = theta_lab)
#plt.show()