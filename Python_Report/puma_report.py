#PuMA plotting module

import numpy as np
import matplotlib.pyplot as plt
import pytz
from datetime import datetime
from calendar import monthrange
import scipy.stats as stats
from netCDF4 import Dataset
import multiprocessing as mp

#### Plotting Functions

def polar_flow_plot_average_per_month(stove,year_month,t_datetime,data,minutes,fname):
    
    index = []
    for i in range(len(t_datetime)):
        if (t_datetime[i].year,t_datetime[i].month) == (year_month):
            index.append(i)
        
    t,data = month_average_temperature(year_month,t_datetime[index[0]:index[-1]+1],
                           data[index[0]:index[-1]+1],minutes)
    
    t_theta = time2theta_time(t) + 5*np.pi/4
    data_theta = data
    t_theta = np.append(t_theta,t_theta[0])
    data_theta = np.append(data_theta,data_theta[0])
    
    polar_flow_plot(stove,year_month,t_datetime,data,t_theta,data_theta,fname)
    
def polar_flow_plot_per_month(stove,year_month,t_datetime,data,fname):
    
    index = []
    for i in range(len(t_datetime)):
        if (t_datetime[i].year,t_datetime[i].month) == year_month:
            index.append(i)
    
    t_theta = datetime2theta_time(t_datetime[index[0]:index[-1]+1])
    data_theta = data[index[0]:index[-1]+1]

    polar_flow_plot(stove,year_month,t_datetime,data,t_theta,data_theta,fname)
    
def polar_flow_plot(stove,year_month,t_datetime,data,t_theta,data_theta,fname):
    
    months = ['','January','February','March','April','May','June','July',
              'August','September','October','November','December']
    fig = plt.figure(figsize = (8,9))
    ax = fig.add_subplot(111, polar=True)
    plt.polar(t_theta,data_theta,label = 'gal/hr', linewidth = 3, color = 'aqua')
    plt.thetagrids((0,45,90,135,180,225,270,315), ('6:00','3:00','0:00','21:00',
                   '18:00','15:00','12:00','9:00'), fontsize = 20)
    plt.rgrids((np.nanmax(data)/3, 2*np.nanmax(data)/3, np.nanmax(data), 
                3.5*np.nanmax(data)/3), labels = (round((np.nanmax(data)/3),2), 
                round((2*np.nanmax(data)/3),2), round(np.nanmax(data),2),''),
                angle = -45, fontsize = 14)
    plt.suptitle('Flowrate Pattern $(gal/hr)$',fontsize = 38)
    plt.title('\n'+months[year_month[1]]+' '+str(year_month[0])+'\n', fontsize = 28)
    ax.tick_params(pad = 22)
    plt.tight_layout()
    plt.savefig(fname)

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
    
    months = ['','January','February','March','April','May','June','July',
              'August','September','October','November','December']
    plt.figure(figsize = (10,6))
    plt.plot(hdd,gph, 'bo', label = 'Data Points')
    plt.plot(lr_x,lr_y, 'r-', linewidth = 3, label = 'Linear Regression Line' + 
             '\ny = ' + str(round(linreg[0],6)) + 'x ' + slope + '\n$R^2$ = ' + 
             str(round(linreg[2]**2,2)))
    plt.legend(fontsize = 14)
    plt.title(stove + ' ' + months[beg_month] + ' ' + str(beg_year) + ' to ' + 
              months[end_month] + ' ' + str(end_year) + 
              '\nFuel Consumption Rate against Temperature Load\n',
              fontsize = 20)
    plt.xlabel('Heat Degree Day (base 65 $\degree$F)',fontsize = 16)
    plt.ylabel('Fuel Consumption Rate (gal/hr)', fontsize = 16)
    plt.tight_layout()
    plt.savefig(fname)

def plot_fuel_usage(year_month,your_gal,their_gal,fname):
    
    colors = ['springgreen','aqua']
    if your_gal > their_gal:
        colors = ['hotpink','aqua']
        
    months = ['','January','February','March','April','May','June','July',
              'August','September','October','November','December']
    plt.figure(figsize = (8,8))
    plt.subplot(111)
    plt.bar([1,2],[your_gal,their_gal],
            color = colors,width = .6)
    plt.suptitle('Fuel Usage $(gal/ft^2)$\n',fontsize = 38)
    plt.title('\n\n'+months[year_month[1]]+' '+str(year_month[0])+'\n', 
              fontsize = 28)
    plt.text(1,1.025*your_gal,str(round(your_gal,2)),
             horizontalalignment='center',fontsize=20)
    plt.text(2,1.025*their_gal,str(round(their_gal,2)),
             horizontalalignment='center',fontsize=20)
    plt.yticks([])
    plt.xticks([1,2],['You','Your Neighbor$^*$'],fontsize=20)
    plt.xlabel('\n* Your neighbor is the average of all the other Fairbanks\nhouseholds participating in this study.',
               fontsize = 14)
    plt.box(False)
    plt.tight_layout()
    plt.savefig(fname)

def year_month2datetime(year_month):
    
    return datetime(year_month[0],year_month[1],1,0,0,0)

def run_year_month2datetime(year_months):
    
    ymdtime = []
    for m in year_months:
        ymdtime.append(year_month2datetime(m))
        
    return ymdtime
    
def plot_bar_progress(year_months,gphddpd,fname):
    
    ymdtime = run_year_month2datetime(year_months)
    date = []
    for ym in ymdtime:
        date.append(ym.strftime('%b %y'))
    x = range(len(date))
    
    plt.figure(figsize = (12,6))
    plt.subplot(111)
    plt.bar(x,gphddpd,width = .6)
    for i in range(len(date)):
        if gphddpd[i] > 0:
            plt.text(x[i],1.025*gphddpd[i],str(round(gphddpd[i],4)),horizontalalignment='center',fontsize=18)
        else:
            plt.text(x[i],0.1*max(gphddpd),'No\nData',horizontalalignment='center',fontsize=18)
    plt.yticks([])
    plt.xticks(x,date,fontsize=18)
    plt.xlabel('Weather Adjusted Gallons per Day',fontsize = 20)
    plt.box(False)
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

def days_available(t_datetime):
    
    days = []
    for t in t_datetime:
        if (t.year,t.month,t.day) not in days:
            days.append((t.year,t.month,t.day))

    return days

def days_available_per_month(t_datetime):
    
    days = days_available(t_datetime)
    months = months_available(t_datetime)
    month_day = []
    for i in range(len(months)):
        month_day.append([months[i],0])
        for j in range(len(days)):
            if days[j][0:2] == months[i]:
                month_day[i][1] += 1
                
    return month_day

def days_available_in_month(year_month,t_datetime):
    
    month_day = days_available_per_month(t_datetime)
    for t in month_day:
        if t[0] == year_month:
            return t[1]
        
    return 0

def complete_months(stove,raw_time,result):
    
    t_datetime = timestamp2datetime(raw_time)
    days = days_available(t_datetime)
    months = months_available(t_datetime)
    
    temp = []
    for i in range(len(months)):
        temp.append([])
        for day in days:
            if day[0:2] == months[i]:
                temp[i].append(day)
    
    complete = []
    for i in range(len(temp)):
        last_day = monthrange(temp[i][-1][0],temp[i][-1][1])[1]
        if temp[i][0][2] == 1 and temp[i][-1][2] == last_day and len(temp[i]) == last_day:
            complete.append(temp[i][0][0:2])
    
    result.put((stove,complete))

def run_complete_months(uni_nc_file):
    
    uni_nc = Dataset(uni_nc_file,'r')
    stoves = list(uni_nc.groups)
    
    stoves_time = []
    for stove in stoves:
        stoves_time.append(uni_nc[stove+'/Raw/time'][:])
        
    result = mp.Manager().Queue()
    pool = mp.Pool(mp.cpu_count())        
    for i in range(len(stoves)):
        pool.apply_async(complete_months,args=(stoves[i],stoves_time[i],result))
    pool.close()
    pool.join()
    results = []
    
    while not result.empty():
        results.append(result.get())
        
    results.sort()
    
    return results

def good_neighbor_stoves(stove,month,stove_comp_months):
    
    good_stoves = []
    for scm in stove_comp_months:
        if month in scm[1]:
            good_stoves.append(scm[0])
            
    return good_stoves

#### Temperature Manipulation Functions

def heat_degree_day(t_datetime,outT,base):
    
    T_ave,day = daily_average_temperature(t_datetime,outT)
    hdd = []
    for i in range(len(t_datetime)):
        for j in range(len(day)):
            if day[j] == (t_datetime[i].year,t_datetime[i].month,t_datetime[i].day):
                hdd.append(base - outT[i])
    
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

def day_average_temperature(t,x,minutes):
    
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
    
def month_average_temperature(year_month,t_datetime,data,minutes):
    
    index = []
    days = []
    for i in range(len(t_datetime)):
        if (t_datetime[i].year,t_datetime[i].month) == (year_month):
            if t_datetime[i].day not in days:
                days.append(i)
            index.append(i)
    
    t_ref = datetime(year_month[0],year_month[1],1,0,0,0)
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
    
    t_ave,data_ave = day_average_temperature(t_ave,data_ave,minutes)
    
    t_ave = np.array(t_ave)
    data_ave = np.array(data_ave)
    
    return t_ave, data_ave

#### Calculated Functions ####
    
def find_neighbor_stoves(main_stove,good_stoves):
    
    neighbor_stoves = []
    for stove in good_stoves:
        if stove != main_stove:
            neighbor_stoves.append(stove)
    
    return neighbor_stoves

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
        stove_dtime.append(timestamp2datetime(uni_nc[stove+'/Event/Clicks/time'][:]))
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

def gallons_per_day_per_month(t_datetime,gallons):
    
    months = months_available(t_datetime)    
    gpm = []
    for m in months:
        gpm.append(gallons_consumed_per_month(m,t_datetime,gallons))
    
    gpd = []
    for i in range(len(gpm)):
        gpd.append(gpm[i]/days_available_in_month(months[i],t_datetime))
        
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
        
def weather_adjusted_gallons_per_day_per_month(raw_t_datetime,t_datetime,gallons,hdd):
    
    gphdd = gallons_per_heating_degree_day(gallons,hdd)
    months = months_available(t_datetime)
    gphddpm = []
    for m in months:
        gphddpm.append(weather_adjusted_gallons_consumed_per_month(m,t_datetime,gphdd))
    
    gphddpd = []
    for i in range(len(gphddpm)):
        if days_available_in_month(months[i],raw_t_datetime) <= 0:
            gphddpd.append(0)
        else:
            gphddpd.append(gphddpm[i]/days_available_in_month(months[i],raw_t_datetime))
        
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

#### Tex File Functions
    
def write_monthly_tex_var_file(Year_Month,Total_Usage,Fuel_Price,Fuel_per_Day,Total_Cost,Fuel_Cost_per_Day,Neighbor_Usage,Prog_Usage):
    
    Percent_Usage = abs(1 - Total_Usage/Neighbor_Usage)
    if Total_Usage > Neighbor_Usage:
        ML = 'more'
    else:
        ML = 'less'
    
    if Prog_Usage > 1:
        PML = 'more'
    else:
        PML = 'less'
    
    Prog_Usage = abs(1 - Prog_Usage)
    
    with open('monthly_values.tex','w') as tex_file:
        
        months = ['','January','February','March','April','May','June','July',
              'August','September','October','November','December']
        
        lines = [r'\newcommand{\totalusage}{'+str(round(Total_Usage,3))+'}',
                 r'\newcommand{\fuelperday}{'+str(round(Fuel_per_Day,3))+'}',
                 r'\newcommand{\fuelprice}{'+str(round(Fuel_Price,2))+'}',
                 r'\newcommand{\totalcost}{'+str(round(Total_Cost,2))+'}',
                 r'\newcommand{\fuelcostperday}{'+str(round(Fuel_Cost_per_Day,2))+'}',
                 r'\newcommand{\neighborusage}{'+str(round(Neighbor_Usage,3))+'}',
                 r'\newcommand{\percentusage}{'+str(round(Percent_Usage*100,2))+'}',
                 r'\newcommand{\moreless}{'+ML+'}',
                 r'\newcommand{\reportmonth}{'+months[Year_Month[1]]+'}',
                 r'\newcommand{\reportyear}{'+str(Year_Month[0])+'}',
                 r'\newcommand{\progress}{'+str(round(Prog_Usage*100,2))+'}',
                 r'\newcommand{\progressmoreless}{'+PML+'}']
        
        for line in lines:
            tex_file.write(line)
            tex_file.write('\n')