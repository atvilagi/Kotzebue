"""
Plotting Module for PuMA

By Douglas Keller and T. Morgan
"""
import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.interpolate import make_interp_spline, BSpline

colors = np.array([[255,16,16],[25, 179, 164],[255, 153, 0],[20, 28, 166],[94, 22, 119]])/255

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
    if (len(data) < 24) & (len(data) >0):
        fillData = pd.Series([0] * 24, pd.Index(range(0, 24, 1)))
        data1 = pd.concat([data, fillData], axis=1)
        data1.loc[pd.isnull(data1.iloc[:, 0]), 0] = data1.iloc[:1]
        #data1.loc[pd.isnull(data1['fuel_consumption']), 0] = data1[0]
        data = data1.iloc[:,0]

    elif (len(data) <= 0):
        data = pd.Series(np.zeros(24))
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
def seasonal_polar_flow_plot(ave_gal_by_hour_by_season,fname):
    seasons =[None,'Winter','Spring','Summer','Fall']
    fig = plt.figure(figsize=(7, 7), dpi=200)
    ax = fig.add_subplot(111, polar=True)
    dtMax = 0
    maxI = (1,0)
    dailyMax = max(ave_gal_by_hour_by_season['fuel_consumption'].groupby('season').sum())
    for season in set(ave_gal_by_hour_by_season.index.levels[0]):
        data = ave_gal_by_hour_by_season[np.in1d(ave_gal_by_hour_by_season.index.get_level_values(0), [season])]
        if (len(data) <= 24) & (len(data) > 0):
            fillData = pd.Series([0] * 24, pd.Index(range(0, 24, 1)))
            if len(data.index.levels) > 1:
                data.index = data.index.droplevel(0)
            data1 = pd.concat([data, fillData], axis=1)
            data1.loc[pd.isnull(data1['fuel_consumption']), 'fuel_consumption'] = data1.loc[pd.isnull(data1['fuel_consumption']),0]
            data = data1.iloc[:, 0]
        elif (len(data) <= 0):
            data = pd.Series(np.zeros(24))
        #each hour is 1/24 of 360 degrees (15 degrees)
        t_theta = np.radians([15] * (len(data) + 1)).cumsum()
        #daily average  = 360 degrees
        #hourly value is proportion of daily average scaled to 360 converted to radians

        data_theta = np.radians((data/dailyMax) * 360)
        #data_theta.index = data_theta.index.levels[1]
        data_theta.loc[24] = data_theta.loc[0]

        t_theta[24] = t_theta[0]
        data_theta.index = t_theta
        #data_theta = data_theta['fuel_consumption']

        if (data_theta.sum() > 0):

            plt.polar(t_theta, data_theta, linewidth=3, color=colors[season - 1], label=seasons[season])
            if np.nanmax(data_theta) > dtMax:
                dtMax = np.nanmax(data_theta)
                maxI = (season, int(np.where(data_theta == dtMax)[0][0]))

    plt.rgrids((dtMax / 3, 2 * dtMax / 3, dtMax,
                3.5 * dtMax / 3), labels=(float(round((ave_gal_by_hour_by_season.loc[maxI] / 3), 2)),
                                                          float(round((2 * ave_gal_by_hour_by_season.loc[maxI] / 3), 2)),
                                                          float(round(ave_gal_by_hour_by_season.loc[maxI], 2)), ''),
               angle=90, fontsize=14)
    plt.polar([-5 * np.pi / 4, -5 * np.pi / 4], [0, 3.5 * dtMax / 3], linewidth=4, color=[0, 0, 0])
    # adding break line
    plt.polar([-np.pi / 4, -np.pi / 4], [0, 3.5 * dtMax / 3], linewidth=4, color=[0, 0, 0])
    # plt.polar(t_theta, data_theta, linewidth=3, color=colors[season-1], label='$gal/hr$')
    plt.text(np.pi / 4, dtMax / 3, 'Night', fontsize=14)
    plt.text(3.92699, dtMax / 3, 'Day', fontsize=14)
    plt.thetagrids((0, 45, 90, 135, 180, 225, 270, 315), ('00:00', '03:00', '06:00', '09:00',
                                                          '12:00', '15:00', '18:00', '21:00'), fontsize=20)
    plt.title('Hourly Fuel Consumption Rate\n', fontsize=28)
    ax.tick_params(pad=14)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 - 0.1, box.width, box.height])
    # Put a legend to the right of the current axis
    plt.legend(bbox_to_anchor=(1.1, -0.1), fontsize=14,ncol=4)
    plt.tight_layout()
    plt.savefig(fname)
    plt.close('all')

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
    plt.close('all')

def plot_annual_fuel_usage(gal_by_year,fname):
    plt.figure(figsize=(9, 6), dpi=200)
    WIDTH = 0.8
    adjWidth = WIDTH/len(list(set(gal_by_year.index.tolist())))
    textDrop = min(gal_by_year.min() * 0.12)
    plt.subplot(111)
    tickCollection = []
    for i,year in enumerate(list(set(gal_by_year.index.tolist()))):
        bars = plt.bar([year.year-(adjWidth * 0.5), year.year + (adjWidth * 0.5)],
                [gal_by_year.loc[year, 'you'],gal_by_year.loc[year, 'meanfuelPerMonthPerArea']],
                color=[colors[0],colors[2]], width=adjWidth,label=('you','neighbors'))

        plt.text(year.year-(adjWidth * 0.5), gal_by_year.loc[year, 'you'],
                        str(round(gal_by_year.loc[year, 'you'], 3)),
                        horizontalalignment='center', fontsize=20)
        plt.text(year.year +(adjWidth * 0.5), gal_by_year.loc[year, 'meanfuelPerMonthPerArea'],
                 str(round(gal_by_year.loc[year, 'meanfuelPerMonthPerArea'], 3)),
                 horizontalalignment='center', fontsize=20)
        tickCollection=tickCollection + [year.year-(adjWidth * 0.5), year.year + (adjWidth * 0.5)]
        plt.yticks([])

    plt.xticks(tickCollection, ['You', 'Your Neighbor$^*$'], fontsize=20)

    plt.ylabel('Average Monthly $gal/ft^2$',fontsize=20)
    plt.yticks([])
    plt.xticks([y.year for y in list(set(gal_by_year.index.tolist()))], [y.year for y in list(set(gal_by_year.index.tolist()))], fontsize=20)

    plt.box(True)
    #plt.legend(iter(bars), ('you', 'neighbor'), loc='upper center', fontsize=14)
    ax = plt.axes()
    box = ax.get_position()

    ax.set_position([box.x0, box.y0 + textDrop, box.width, box.height])
    # Put a legend to the right of the current axis
    plt.legend(iter(bars), ('you', 'neighbor'),loc='upper center',bbox_to_anchor=(0.5, -0.1),ncol=2)
    plt.tight_layout()
    plt.savefig(fname)
    plt.close('all')

def plot_fuel_usage(your_gal,their_gal,fname):
    bar_text_height = their_gal
    if your_gal > their_gal:

        bar_text_height = your_gal
        
    plt.figure(figsize = (9,6), dpi = 200)
    plt.subplot(111)
    plt.bar([1,2],[your_gal,their_gal],color = colors,width = .6)
    plt.text(1,your_gal + .05*bar_text_height,str(round(your_gal,4)) + ' $gal/ft^2$',
             horizontalalignment='center',fontsize=20)
    plt.text(2,their_gal + .05*bar_text_height,str(round(their_gal,4)) + ' $gal/ft^2$',
             horizontalalignment='center',fontsize=20)
    plt.yticks([])
    plt.xticks([1,2],['You','Your Neighbor$^*$'],fontsize=20)
    plt.box(False)
    plt.tight_layout()
    plt.savefig(fname)
    plt.close('all')
def plotActualvsEstimated(actual, estimated):

    plt.figure(figsize=(14, 6))

    fig, ax1 = plt.subplots()
    WIDTH = 0.8

    widthRatio = WIDTH/len(set(estimated.index.year))

    for j,y in enumerate(list(set(estimated.index.year))):
        for i,m in enumerate(list(set(estimated.index.month))):
            X = m - 0.5
            a = actual[(actual.index.month == m) & (actual.index.year == y)]
            e = estimated[(estimated.index.month== m) & (estimated.index.year == y)]
            bars = ax1.bar(X, e, width=0.5, color='red')

            bars = ax1.bar(X + 0.5, a, width=0.5,
                           color='blue')

    plt.box(False)
    plt.legend(bbox_to_anchor=(.73, 0.98), fontsize=14)
    plt.savefig("dataComparison.png", bbox_inches='tight')
    plt.close()

def plot_multiyear_bar_progress_with_temperature(gphddpm,monthlyMeanTemperature, fname):
    '''plots gallons per hour for each month and each year with mean monthy tempearture.
    Each year is its own series.'''

    gphddpm.loc[pd.isnull(gphddpm)] = 0
    monthlyMeanTemperature = monthlyMeanTemperature.interpolate()

    plt.figure(figsize=(14, 6))

    fig, ax1 = plt.subplots()
    WIDTH = 0.8

    widthRatio = WIDTH/len(set(gphddpm.index.year))
    for i,y in enumerate(list(set(gphddpm.index.year))):
        X = (gphddpm[gphddpm.index.year == y].index.month + (i+1) * widthRatio) - WIDTH *0.5
        bars = ax1.bar(X, gphddpm[gphddpm.index.year == y], width=widthRatio, color=colors[i])


    ax1.set_ylim(0, max(gphddpm) * 1.2)
    ax1.set_ylabel('\ngal/HDD', fontsize=14)
    # now monthly outside temperature
    axes2 = ax1.twinx()
    axes2.set_ylabel('Average Temperature $^\circ$F',fontsize=14)
    axes2.set_ylim(monthlyMeanTemperature.min(), monthlyMeanTemperature.max() * 1.1)
    l, r = [(2, 0)], [(2, 0)]
    for i,y in enumerate(list(set(gphddpm.index.year))):
        T = monthlyMeanTemperature[(pd.notnull(monthlyMeanTemperature)) & (monthlyMeanTemperature.index.year == y)].index.month.tolist()
        power = monthlyMeanTemperature[
            (pd.notnull(monthlyMeanTemperature)) & (monthlyMeanTemperature.index.year == y)]
        if (len(T) > 1):

             xnew = np.linspace(min(monthlyMeanTemperature[(pd.notnull(monthlyMeanTemperature)) & (
                         monthlyMeanTemperature.index.year == y)].index.month.tolist()), max(monthlyMeanTemperature[(
                                                                                                                        pd.notnull(
                                                                                                                            monthlyMeanTemperature)) & (
                                                                                                                                monthlyMeanTemperature.index.year == y)].index.month.tolist()),
                                len(monthlyMeanTemperature[(pd.notnull(monthlyMeanTemperature)) & (
                                            monthlyMeanTemperature.index.year == y)]) * 10)

             spl = make_interp_spline(T, power, k=3,bc_type=(l, r))  # type: BSpline
             smoothed = spl(xnew)
             line = axes2.plot(xnew,smoothed, label=y,c=colors[i])
        elif (len(T)==1):
            line = axes2.plot(T[0], power[0], label=y, c=colors[i])

    #xticks = [datetime.date(1900, j, 1).strftime('%b') for j in range(min(gphddpm.index.month), max(gphddpm.index.month) + 1)]
    xticks = [datetime.date(1900, j, 1).strftime('%b') for j in
              range(min(monthlyMeanTemperature.index.month), max(monthlyMeanTemperature.index.month) + 1)]
    plt.xticks([j for j in range(min(monthlyMeanTemperature.index.month), max(monthlyMeanTemperature.index.month) + 1)], xticks, fontsize=22, rotation=0)
    #plt.xlabel('\nTemperature Adjusted Gallons per Month', fontsize=22)

    plt.box(False)
    plt.legend(bbox_to_anchor=(.73, 0.98), fontsize=14)
    plt.savefig(fname, bbox_inches='tight')
    plt.close()

def plot_bar_progress(gphddpm, fname):
    '''

    :param gphddpm: pandas.Series with month period index and gallons per heat degree day per month
    :param fname: string filename with path
    :return:
    '''

    data = pd.DataFrame({'value':gphddpm.values,'month':gphddpm.index.month}, index = gphddpm.index)

    plt.figure(figsize=(14, 6))
    plt.subplot(111)
    WIDTH = 0.8
    widthRatio = WIDTH / len(set(data.index.year))
    for i, y in enumerate(list(set(gphddpm.index.year))):
        X = (data[data.index.year == y].index.month + (i + 1) * widthRatio) - WIDTH * 0.5
        bars = plt.bar(X, data.loc[data.index.year == y,'value'].values, width=widthRatio, color=colors[i])

        for rect in bars:
            height = rect.get_height()
            if height > 0:
                plt.text(rect.get_x() + rect.get_width()/2, height, str(round(height,3)),
                         horizontalalignment='center', verticalalignment = 'bottom', fontsize=12)
            else:
                plt.text(rect.get_x() + rect.get_width()/2, height + (np.nanmax(data) * 0.5), 'N\A',
                         horizontalalignment='center',verticalalignment = 'bottom', fontsize=12)
    plt.yticks([])
    xticks = [datetime.date(1900, h, 1).strftime('%b') for h in range(1,13)]
    plt.xticks([j for j in range(1, 13)], xticks, fontsize=18, rotation=90)
    plt.xlabel('\nTemperature Adjusted Gallons per Month', fontsize=22)
    plt.ylabel( '\ngal/HDD*',fontsize=22)
    plt.box(False)
    plt.savefig(fname)
    plt.close()
