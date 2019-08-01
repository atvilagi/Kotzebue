#PuMA plotting module

import numpy as np
import matplotlib.pyplot as plt
import pytz
from datetime import datetime

def months_available(t_datetime):
    
    months = []
    for t in t_datetime:
        if (t.year,t.month) not in months:
            months.append((t.year,t.month))
    
    return months

def day_average(t,x,minutes):
    
    ave = np.linspace(0,86400,1440/minutes)
    t_ave = []
    x_ave = []
    for j in range(len(ave)-1):
        x_ave.append([])
        t_ave.append((ave[j] + ave[j+1])/2)
        for i in range(len(t)):
            if ave[j] < t[i] < ave[j+1]:
                x_ave[j].append(x[i])
                
    temp = []
    for i in x_ave:
        temp.append(np.nanmean(i))
    x_ave = temp
    
    return t_ave, x_ave
    
def month_average(year,month,t_datetime,data,minutes):
    
    index = []
    days = []
    for i in range(len(t_datetime)):
        if (t_datetime[i].year,t_datetime[i].month) == (year,month):
            if t_datetime[i].day not in days:
                days.append(i)
            index.append(i)
    
    t_ref = datetime(year,month,1,0,0,0)
    timeAK = pytz.timezone('America/Anchorage')
    t_ref = timeAK.localize(t_ref)
    
    ave = []
    for i in index:
        ave.append(((t_datetime[i].timestamp() - t_ref.timestamp()) % 86400,data[i]))
        
    ave.sort()
    t_ave = []
    data_ave = []
    for i in ave:
        t_ave.append(i[0])
        data_ave.append(i[1])
    
    t_ave = np.array(t_ave)
    data_ave = np.array(data_ave)
    
    t_ave,data_ave = day_average(t_ave,data_ave,minutes)
    
    t_ave = np.array(t_ave)
    data_ave = np.array(data_ave)
    
    return t_ave, data_ave

def polar_flow_plot_average_per_month(stove,year,month,t_datetime,data,minutes,fname):
    
    index = []
    for i in range(len(t_datetime)):
        if (t_datetime[i].year,t_datetime[i].month) == (year,month):
            index.append(i)
        
    t,data = month_average(year,month,t_datetime[index[0]:index[-1]+1],data[index[0]:index[-1]+1],minutes)
    
    t_theta = time2theta_time(t) + 5*np.pi/4
    data_theta = data
    t_theta = np.append(t_theta,t_theta[0])
    data_theta = np.append(data_theta,data_theta[0])
    
    polar_flow_plot(stove,year,month,t_datetime,data,t_theta,data_theta,fname)
    
def polar_flow_plot(stove,year,month,t_datetime,data,t_theta,data_theta,fname):
    
    months = ['January','February','March','April','May','June','July','August','September','October','November','December']
    fig = plt.figure(figsize = (8,10))
    ax = fig.add_subplot(111, polar=True)
    plt.polar(t_theta,data_theta,label = 'gal/hr', linewidth = 1.25)
    plt.thetagrids((0,45,90,135,180,225,270,315), ('6:00','3:00','0:00','21:00','18:00','15:00','12:00','9:00'), fontsize = 16)
    plt.rgrids((np.nanmax(data)/3, 2*np.nanmax(data)/3, np.nanmax(data), 3.5*np.nanmax(data)/3), labels = (round((np.nanmax(data)/3),2), round((2*np.nanmax(data)/3),2), round(np.nanmax(data),2),''), angle = -45, fontsize = 12)
    plt.legend(bbox_to_anchor = (.35,0.03),fontsize = 16)
    plt.title(stove + ' ' + months[month] + ', ' + str(year) + '\nDaily (HH:MM) Flowrate Patterns\n', fontsize = 20)
    ax.tick_params(pad = 15)
    plt.tight_layout()
    plt.savefig(fname)
    
def polar_flow_plot_per_month(stove,year,month,t_datetime,data,fname):
    
    index = []
    for i in range(len(t_datetime)):
        if (t_datetime[i].year,t_datetime[i].month) == (year,month):
            index.append(i)
    
    t_theta = datetime2theta_time(t_datetime[index[0]:index[-1]+1])
    data_theta = data[index[0]:index[-1]+1]

    polar_flow_plot(stove,year,month,t_datetime,data,t_theta,data_theta,fname)
    
def time2theta_time(t):
    #expecting t in seconds
    t_theta = -t*2*np.pi/86400 - 3*np.pi/4 #shifted so the top of the plot is 0:00
    
    return t_theta

def datetime2theta_time(t_datetime):
    
    t = []
    for i in t_datetime:
        t.append(i.timestamp())
        
    t = np.array(t)
    t_theta = time2theta_time(t)
    
    return t_theta    

def timestamp2datetime(t_stamp):
    
    timeZ = pytz.timezone('UTC')
    timeAK = pytz.timezone('America/Anchorage')
    t_datetime = []
    for i in range(len(t_stamp)):
        t_datetime.append(datetime.fromtimestamp(t_stamp[i]))
        t_datetime[i] = timeZ.localize(t_datetime[i])
        t_datetime[i] = t_datetime[i].astimezone(timeAK)

    return t_datetime