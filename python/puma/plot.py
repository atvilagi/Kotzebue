"""
Plotting Module for PuMA

By Douglas Keller and T. Morgan
"""
import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
#from pandas.plotting import register_matplotlib_converters #this is here to shutup matplotlib warnings

"""
colors:
    
green [46,204,113]
orange [230,126,34]
blue [52,152,219]
purple [155,89,182]
red [231,76,60]
"""

def polar_flow_plot_per_month_df(label,data,fname):
    """
    Plots a polar flow plot of the hourly flow rate of a month.
    
    Arguments:
        label -- label to apply to plot title
        data -- a pandas Series with datetime index
        fname -- filename for the saved png
        
    Plots the hourly flow rate of a month of flow rate data in a polar plot and saves the plot to a png
    file with the polar_flow_plot function.
    """
    if len(data) < 24:
        fillData = pd.Series([0] * 24, pd.Index(range(0, 24, 1)))
        data1 = pd.concat([data, fillData], axis=1)
        data1.loc[pd.isnull(data1[0]), 0] = data1[1]
        data = data1.drop(1, axis=1)
        data = data.iloc[0:, 0]
    #each hour is 1/24 of 360 degrees (15 degrees)
    t_theta = np.radians([15] * (len(data) + 1)).cumsum()
    #daily average  = 360 degrees
    #hourly value is proportion of daily average scaled to 360 converted to radians
    dailyAve = data.sum()
    data_theta = np.radians((data/dailyAve) * 360)
    data_theta.loc[24] = data_theta.loc[0]
    t_theta[24] = t_theta[0]
    data_theta.index = t_theta

    polar_flow_plot(data,t_theta,data_theta, fname) #plotting using the polar_flow_plot function

def polar_flow_plot(data,t_theta,data_theta,fname):
    """
    Polar plot 
    """
    fig = plt.figure(figsize = (7,7), dpi = 200)
    ax = fig.add_subplot(111, polar=True)
    if data_theta.sum() > 0:
        #adding break line
        plt.polar([-5*np.pi/4,-5*np.pi/4],[0,3.5*np.nanmax(data_theta)/3],linewidth = 4, color = [0,0,0])
        #adding break line
        plt.polar([-np.pi/4,-np.pi/4],[0,3.5*np.nanmax(data_theta)/3],linewidth = 4, color = [0,0,0])
        plt.polar(t_theta,data_theta, linewidth = 3, color = np.array([230,126,34])/255, label = '$gal/hr$')
        plt.rgrids((np.nanmax(data_theta)/3, 2*np.nanmax(data_theta)/3, np.nanmax(data_theta),
                3.5*np.nanmax(data_theta)/3), labels = (round((np.nanmax(data)/3),2),
                round((2*np.nanmax(data)/3),2), round(np.nanmax(data),2),''),
                angle = 90, fontsize = 14)
        plt.text(np.pi / 4, np.nanmax(data_theta) / 3, 'Day', fontsize=14)
        plt.text(3.92699, np.nanmax(data_theta) / 3, 'Night', fontsize=14)
    plt.thetagrids((0,45,90,135,180,225,270,315), ('6:00','3:00','12:00 PM','9:00',
                   '6:00','3:00','12:00 AM','9:00'), fontsize = 20)
    plt.title('Hourly Fuel Consumption Rate\n',fontsize = 28)
    ax.tick_params(pad = 14)


    plt.legend(bbox_to_anchor = (.35,.03),fontsize = 14)
    plt.tight_layout()
    plt.savefig(fname)
    plt.close()

def plot_fuel_usage(your_gal,their_gal,fname):
    
    colors = np.array([[46,204,113],[52,152,219]])/255
    bar_text_height = their_gal
    
    if your_gal > their_gal:
        colors = np.array([[231,76,60],[52,152,219]])/255
        bar_text_height = your_gal
        
    plt.figure(figsize = (9,6), dpi = 200)
    plt.subplot(111)
    plt.bar([1,2],[your_gal,their_gal],color = colors,width = .6)
    plt.title('Fuel Consumption per Area\n',fontsize = 28)
    plt.text(1,your_gal + .05*bar_text_height,str(round(your_gal,4)) + ' $gal/ft^2$',
             horizontalalignment='center',fontsize=20)
    plt.text(2,their_gal + .05*bar_text_height,str(round(their_gal,4)) + ' $gal/ft^2$',
             horizontalalignment='center',fontsize=20)
    plt.yticks([])
    plt.xticks([1,2],['You','Your Neighbor$^*$'],fontsize=20)
    plt.xlabel('\n* Your neighbor is the average of other FNSB\nhouseholds participating in this study.',
               fontsize = 16)
    plt.box(False)
    plt.tight_layout()
    plt.savefig(fname)
    plt.close()



def plot_bar_progress(gphddpm, fname):
    '''

    :param gphddpm: pandas.Series with month period index and gallons per heat degree day per month
    :param fname: string filename with path
    :return:
    '''
    #ym.strftime('%b %y'))

    x = gphddpm[gphddpm > 0].index

    colors = np.array([155, 89, 182]) / 255

    plt.figure(figsize=(14, 6))
    plt.subplot(111)
    bars = plt.bar(x, gphddpm[gphddpm > 0], width=0.6, color=colors)
    for rect in bars:
        height = rect.get_height()
        if height > 0:
            plt.text(rect.get_x() + rect.get_width()/2, height, str(round(height,4)) + '\ngal/HDD*',
                     horizontalalignment='center', verticalalignment = 'bottom', fontsize=18)
        else:
            plt.text(rect.get_x() + rect.get_width()/2, height + (np.nanmax(gphddpm) * 0.5), 'No\nData',
                     horizontalalignment='center',verticalalignment = 'bottom', fontsize=18)
    plt.yticks([])
    xticks = [datetime.date(1900, j, 1).strftime('%B') for j in x]
    plt.xticks(x,xticks , fontsize=20)
    plt.xlabel('\nTemperature Adjusted Gallons per Month', fontsize=20)
    plt.box(False)
    plt.savefig(fname,bbox_inches='tight')
    plt.close()
