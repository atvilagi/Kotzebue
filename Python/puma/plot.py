#PuMA Plotting Module

#By Douglas Keller

import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
import puma.time as ptime
import puma.temperature as ptemp
import puma.signal_processing as psp

#colors
#green [46,204,113]
#orange [230,126,34]
#blue [52,152,219]
#purple [155,89,182]
#red [231,76,60]

def polar_flow_plot_average_per_month(stove,year_month,t_datetime,data,minutes,fname):
    
    index = []
    for i in range(len(t_datetime)):
        if (t_datetime[i].year,t_datetime[i].month) == (year_month):
            index.append(i)
        
    t,data = ptemp.month_average_temperature(year_month,t_datetime[index[0]:index[-1]+1],
                           data[index[0]:index[-1]+1],minutes)
    
    t_theta = ptime.time2theta_time(t)
    data_theta = data
    t_theta = np.append(t_theta,t_theta[0])
    data_theta = np.append(data_theta,data_theta[0])
    
    polar_flow_plot(stove,year_month,t_datetime,data,t_theta,data_theta,fname)
    
def polar_flow_plot_per_month(stove,year_month,t_datetime,data,fname):
    
    index = []
    for i in range(len(t_datetime)):
        if (t_datetime[i].year,t_datetime[i].month) == year_month:
            index.append(i)
    
    t_theta = ptime.datetime2theta_time(t_datetime[index[0]:index[-1]+1])
    data_theta = data[index[0]:index[-1]+1]

    polar_flow_plot(stove,year_month,t_datetime,data,t_theta,data_theta,fname)
            
def polar_flow_plot(stove,year_month,t_datetime,data,t_theta,data_theta,fname):
    
    fig = plt.figure(figsize = (7,7), dpi = 200)
    ax = fig.add_subplot(111, polar=True)
    plt.polar([-5*np.pi/4,-5*np.pi/4],[0,3.5*np.nanmax(data)/3],linewidth = 4, color = [0,0,0])
    plt.polar([-np.pi/4,-np.pi/4],[0,3.5*np.nanmax(data)/3],linewidth = 4, color = [0,0,0])
    plt.polar(t_theta,data_theta, linewidth = 3, color = np.array([230,126,34])/255, label = '$gal/hr$')
    plt.thetagrids((0,45,90,135,180,225,270,315), ('6:00','3:00','12:00 AM','9:00',
                   '6:00','3:00','12:00 PM','9:00'), fontsize = 20)
    plt.rgrids((np.nanmax(data)/3, 2*np.nanmax(data)/3, np.nanmax(data), 
                3.5*np.nanmax(data)/3), labels = (round((np.nanmax(data)/3),2), 
                round((2*np.nanmax(data)/3),2), round(np.nanmax(data),2),''),
                angle = 90, fontsize = 14)
    plt.title('Hourly Fuel Consumption\n',fontsize = 28)
    ax.tick_params(pad = 14)
    plt.text(np.pi/4,np.nanmax(data)/6,'Night',fontsize = 14)
    plt.text(5*np.pi/4,np.nanmax(data)/3,'Day',fontsize = 14)
    plt.legend(bbox_to_anchor = (.35,.03),fontsize = 14)
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
    
    lr_x,lr_y,slope,intercept,rvalue = psp.linear_regression2line(hdd,gph)
    
    if intercept < 0:
        intercept = '- ' + str(round(np.abs(slope),6))
    else:
        intercept = '+ ' + str(round(slope,6))
    
    months = ['','January','February','March','April','May','June','July',
              'August','September','October','November','December']
    plt.figure(figsize = (10,6))
    plt.plot(hdd,gph, 'bo', label = 'Data Points')
    plt.plot(lr_x,lr_y, 'r-', linewidth = 3, label = 'Linear Regression Line' + 
             '\ny = ' + str(round(slope,6)) + 'x ' + intercept + '\n$R^2$ = ' + 
             str(round(rvalue**2,2)))
    plt.legend(fontsize = 14)
    plt.title(stove + ' ' + months[beg_month] + ' ' + str(beg_year) + ' to ' + 
              months[end_month] + ' ' + str(end_year) + 
              '\nFuel Consumption Rate against Temperature Load\n',
              fontsize = 20)
    plt.xlabel('Heat Degree Day (base 65 $\degree$F)',fontsize = 16)
    plt.ylabel('Fuel Consumption Rate (gal/hr)',fontsize = 16)
    plt.tight_layout()
    plt.savefig(fname)

def plot_fuel_usage(year_month,your_gal,their_gal,fname):
    
    colors = np.array([[46,204,113],[52,152,219]])/255
    bar_text_height = their_gal
    
    if your_gal > their_gal:
        colors = np.array([[231,76,60],[52,152,219]])/255
        bar_text_height = your_gal
        
    plt.figure(figsize = (9,6), dpi = 200)
    plt.subplot(111)
    plt.bar([1,2],[your_gal,their_gal],color = colors,width = .6)
    plt.title('Fuel Consumption\n',fontsize = 28)
    plt.text(1,your_gal + .05*bar_text_height,str(round(your_gal,4)) + ' $gal/ft^2$',
             horizontalalignment='center',fontsize=20)
    plt.text(2,their_gal + .05*bar_text_height,str(round(their_gal,4)) + ' $gal/ft^2$',
             horizontalalignment='center',fontsize=20)
    plt.yticks([])
    plt.xticks([1,2],['You','Your Neighbor$^*$'],fontsize=20)
    plt.xlabel('\n* Your neighbor is the average of all the other FNSB\nhouseholds participating in this study.',
               fontsize = 16)
    plt.box(False)
    plt.tight_layout()
    plt.savefig(fname)
    
def plot_bar_progress(year_months,gphddpm,fuel_price,fname):
    
    ymdtime = ptime.run_year_month2datetime(year_months)
    date = []
    for ym in ymdtime:
        date.append(ym.strftime('%b %y'))
    x = range(len(date))
    
    colors = np.array([155,89,182])/255
    
    plt.figure(figsize = (12,4))
    plt.subplot(111)
    plt.bar(x,gphddpm,width = .6,color = colors)
    for i in range(len(date)):
        if gphddpm[i] > 0:
            plt.text(x[i],(gphddpm[i]+.025*np.nanmax(gphddpm)),
                     str(round(gphddpm[i],4)),horizontalalignment='center',
                     fontsize=18)
            plt.text(x[i],(gphddpm[i]+.175*np.nanmax(gphddpm)),
                     '$ ' + str(round(fuel_price*gphddpm[i],2)),horizontalalignment='center',
                     fontsize=18)
        else:
            plt.text(x[i],0.1*max(gphddpm),'Data\nUnavailable',
                     horizontalalignment='center',fontsize=18)
    plt.yticks([])
    plt.xticks(x,date,fontsize=20)
    plt.xlabel('\nWeather Adjusted Gallons per Month',fontsize = 20)
    plt.box(False)
    plt.tight_layout()
    plt.savefig(fname)