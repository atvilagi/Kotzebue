#PuMA plotting module

import numpy as np
import matplotlib.pyplot as plt
import pytz
from datetime import datetime
import scipy.stats as stats

#### Plotting Functions

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
    
    months = ['','January','February','March','April','May','June','July','August','September','October','November','December']
    fig = plt.figure(figsize = (8,10))
    ax = fig.add_subplot(111, polar=True)
    plt.polar(t_theta,data_theta,label = 'gal/hr', linewidth = 1.25)
    plt.thetagrids((0,45,90,135,180,225,270,315), ('6:00','3:00','0:00','21:00','18:00','15:00','12:00','9:00'), fontsize = 16)
    plt.rgrids((np.nanmax(data)/3, 2*np.nanmax(data)/3, np.nanmax(data), 3.5*np.nanmax(data)/3), labels = (round((np.nanmax(data)/3),2), round((2*np.nanmax(data)/3),2), round(np.nanmax(data),2),''), angle = -45, fontsize = 12)
    plt.legend(bbox_to_anchor = (.35,0.03),fontsize = 16)
    plt.title(stove + ' ' + months[month] + ' ' + str(year) + '\nHourly (HH:MM) Flowrate Patterns\n', fontsize = 20)
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

def plot_heating_degree_days(stove,t_datetime,gph,hdd,fname):
    
    beg_month = t_datetime[0].month
    beg_year = t_datetime[0].year
    end_month = t_datetime[-1].month
    end_year = t_datetime[-1].year
    
    bad = []
    gph = np.array(gph)
    hdd = np.array(hdd)
    for i in range(len(gph)):
        if gph[i] == 0:
            bad.append(i)

    gph = np.delete(gph,bad)
    hdd = np.delete(hdd,bad)
    
    linreg = stats.linregress(hdd,gph)
    
    def linear_regression2line(linreg,x):
        
        def line(linreg,x):
            return linreg[0]*x + linreg[1]
        
        x_line = np.array([np.nanmin(x),np.nanmax(x)])        
        y_line = np.array([line(linreg,x_line[0]),line(linreg,x_line[1])])
        
        return x_line, y_line
        
    lr_x,lr_y = linear_regression2line(linreg,hdd)
    
    if linreg[1] < 0:
        slope = '- ' + str(round(np.abs(linreg[1]),6))
    else:
        slope = '+ ' + str(round(linreg[1],6))
    
    months = ['','January','February','March','April','May','June','July','August','September','October','November','December']
    plt.figure(figsize = (10,6))
    plt.plot(hdd,gph, 'bo', label = 'Data Points')
    plt.plot(lr_x,lr_y, 'r-', linewidth = 3, label = 'Linear Regression Line' + '\ny = ' + str(round(linreg[0],6)) + 'x ' + slope + '\n$R^2$ = ' + str(round(linreg[2]**2,2)))
    plt.legend(fontsize = 14)
    plt.title(stove + ' ' + months[beg_month] + ' ' + str(beg_year) + ' to ' + months[end_month] + ' ' + str(end_year) + '\nFuel Consumption Rate against Temperature Load\n', fontsize = 20)
    plt.xlabel('Heat Degree Day (base 65 $\degree$F)',fontsize = 16)
    plt.ylabel('Fuel Consumption Rate (gal/hr)', fontsize = 16)
    plt.tight_layout()
    plt.savefig(fname)

#### Time Manipulation Functions
    
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

def months_available(t_datetime):
    
    months = []
    for t in t_datetime:
        if (t.year,t.month) not in months:
            months.append((t.year,t.month))
    
    return months

#### Temperature Manipulation Functions

def heat_degree_day(t_datetime,outT):
    
    T_ave,day = daily_average_temperature(t_datetime,outT)
    hdd = []
    for i in range(len(t_datetime)):
        for j in range(len(day)):
            if day[j] == (t_datetime[i].year,t_datetime[i].month,t_datetime[i].day):
                hdd.append(65 - outT[i])
    
    return hdd    

def daily_average_temperature(t_datetime,outT):
    
    day = []
    T_max = []
    T_min = []
    
    i = 0
    while i < len(t_datetime):
        if (t_datetime[i].year,t_datetime[i].month,t_datetime[i].day) not in day:
            day.append((t_datetime[i].year,t_datetime[i].month,t_datetime[i].day))
        i += 1
    
    for i in range(len(day)):
        T_max.append(-999)
        T_min.append(999)
        
    i = 0
    while i < len(t_datetime):
        for j in range(len(day)):
            if day[j] == (t_datetime[i].year,t_datetime[i].month,t_datetime[i].day):
                if T_max[j] < outT[i]:
                    T_max[j] = outT[i]
                if T_min[j] > outT[i]:
                    T_min[j] = outT[i]
        i += 1
    
    T_max = np.array(T_max)
    T_min = np.array(T_min)
    T_ave = (T_max + T_min)/2
    
    return T_ave, day

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

#### Signal Processing Functions
    
def moving_median(f,N):
    
    mm = np.zeros(f.size)
    
    for i in range(f.size):
        if i < N:
            m = []
            for j in range(i+N+1):
                if np.isfinite(f[j]):
                    m.append(f[j])
            m = np.array(m)
            mm[i] = np.median(m)
        elif i+N > f.size-1:
            m = []
            for j in range(i-N,f.size):
                if np.isfinite(f[j]):
                    m.append(f[j])
            m = np.array(m)
            mm[i] = np.median(m)
        else:
            mm[i] = np.median(f[i-N:i+N+1][np.where(np.isfinite(f[i-N:i+N+1]))[0]])
        
    return mm

def brock_improved_despike(f,N):
    #Improved version of Brock's "A Nonlinear Filter to Remove Impulse Noise from Meteorological Data," 1986, JTECH
    
    def run_despike(f,f_med):
        
        dif = f - f_med
        dif_max = np.nanmax(dif) - np.nanmin(dif)
        dif_min = np.sort(np.abs(np.diff(dif)))
        dif_min = dif_min[np.where(dif_min>0)[0]]
        dif_min = 2*np.nanmin(dif_min)
        
        bin_max = int(dif_max//dif_min)
        
        spikes = 0
        spike_loc = []
        bin_count = 3
        while bin_count < bin_max:
            hist,bins = np.histogram(dif,bins=bin_count)
            
            dif_threshold = [bins[0],bins[-1]]
            zeros = np.where(hist==0)[0]
            if len(zeros) > 0:
                bins_mean = np.where(hist==max(hist))[0][0]
                
                zero_mid = zeros - bins_mean
                zero_gn = zero_mid[np.where(zero_mid<0)[0]]
                zero_lp = zero_mid[np.where(zero_mid>=0)[0]]
                
                if len(zero_gn) > 0:
                    zero_gn = max(zero_gn) + bins_mean
                    dif_threshold[0] = bins[zero_gn]
                
                if len(zero_lp) > 0:
                    zero_lp = min(zero_lp) + bins_mean
                    dif_threshold[1] = bins[zero_lp+1]
                
                for i in range(len(f)):
                    if dif[i] > dif_threshold[1]:
                        f[i] = f_med[i]
                        spike_loc.append(i)
                        spikes += 1
                    if dif[i] < dif_threshold[0]:
                        f[i] = f_med[i]
                        spike_loc.append(i)
                        spikes += 1
                
                bin_count = bin_max
            
            bin_count += 2
            
        return f, spikes, spike_loc
    
    f = np.array(f)
    f_med = moving_median(f,N)
    
    f,spikes,spike_loc = run_despike(f,f_med)
    spike = [spikes]
    spike_locs = spike_loc
    while spikes > 0:
        f,spikes,spike_loc = run_despike(f,f_med)
        spike.append(spikes)
        spike_locs += spike_loc
        
    return f,spike,spike_locs