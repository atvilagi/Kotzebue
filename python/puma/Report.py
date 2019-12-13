#Functions for making reports
#created by T. Morgan 12/3/2019

import os
import pytz
import datetime

from netCDF4 import Dataset
import pandas as pd
import puma.plot as pplot
import puma.tex as ptex
import puma.fuel as pfuel
import puma.temperature as ptemp

# file_path = os.path.abspath(os.path.dirname(__file__))
# sys.path.append(os.path.join(file_path,'..'))

class Report:
    '''Report class contains metric attributes ported to the report document and the functions to generate them from a unified netcdf
    '''
    def __init__(self,start,end,title,nc,houses,fuel_price):
        '''

        :param start: datetime AKST for start of dateset to include in metric calculations
        :param end:  datetime AKST for end of dateset to include in metric calculations
        :param title: title to use to name pdf
        :param nc: Unified netcdf
        :param houses: A list of houses to calculate metrics for
        '''
        self.start = start #start date for the report period
        self.end = end  #end date for the report period
        self.titlePrefix = title #a prefix to destinguish this report from others for the same list of stoves
        self.houses = houses  # list of house objects with 1 or more stoves to include in metrics
        self.tip_no = 0 #tip number associated with a tip list
        self.name= "-".join([s.name for s in self.mergeStoves()]) #report name autogenerated from stove list
        self.unified_nc_file = nc #netcdf file containing data to use in report
        self.gallons = 0  #sum of all gallons consumed during report period
        self.total_clicks = 0   #total number of clicks recorded during report period (not meaining full for multi-stove households)
        self.total_cost=0   #total cost of fuel based on gallons (see below metric) and input fuel price
        self.ave_fuel_per_day = (0,0) #average and standard error of gallons per day during the report period
        self.gph = pd.Series()  #pandas series of average gallons per hour during report time period
        self.ave_gallons_by_hour = pd.Series() #average gallons per hour for each our in a 24 hour period
        self.ave_gph = (0,0)    #average and standard error of gallons per hour during report time period
        self.gallons_per_ft = 0     #total gallons (estimate or actual) for entire report time period per square ft
        self.neighbor_usage = 0     #total gallons used by entire neighborhood (exlcuding report houses)
        self.neighbor_usage_per_area = (0,0) #mean and standard deviation - should be CI and standard error
        self.ave_indoorT = (0,0)    #average indoor temperature for entire report time period
        self.ave_outdoorT = (0,0)   #average outdoor temperature for entire report time period
        self.fuel_price = fuel_price    #fuel price, set by user
        self.date_duration = 0      #time delta of the report time period
        self.days_monitored = (0,0) #tuple actual time and time in days covered by actual dataset (less than duration if there are missing values)
        self.neighborhood = []  #list of Houses in the neighborhood
        self.total_gallons = 0  #the total gallons consumed in the report time period. If dataset has missing data this value is extrapolated from average consumption rates
        self.gphddpm = pd.Series()  #gallons per hour per hdd by month for all months included in dataset (including prior to report period)
        self.cost_per_day=0     #average cost per day based on gallons (not extrapolated), days monitored and fuel price
        self.prog_usage = 0     #proportion of usage compared to previous time interval
        self.dataFlag = 0       #0, or 1. 1 indicates total gallons is an estimate because data was missing
    def mergeStoves(self):
        '''get a list of stoves to extract data from based the the stoves that are
        associated with each house included in report'''
        self.stoves = []
        self.stoves = [self.stoves + h.stoves for h in self.houses][0]
        return self.stoves
    def generateMetrics(self):
        '''create a dataframe for the report time period and generate report metrics based on the dataset'''
        self.area = sum([float(house.area) for house in self.houses])  # total area metrics are being calculated for
        self.report_duration = self.end - self.start
        #filter the dataset to the portion required for this report
        self.filtered_df,self.unfiltered_df = self.filterDataset()
        if len(self.filtered_df) > 0:
            self.date_duration = pd.to_timedelta(self.filtered_df.index[-1] - self.filtered_df.index[0],
                                                 unit='day')
            self.days_monitored  =self.getDaysMonitored() #this is actual duration that there is data for

            self.getTip() #set a tip to display

            self.ave_indoorT = self.getAveTemperature('inT') #average of indoor Temperature for report time period

            self.ave_outdoorT = self.getAveTemperature('outT') #average of outdoor Temperature for report time period

            self.gallons = self.filtered_df.fuel_consumption.sum() #recorded consumption in gallons

            self.gph = pfuel.gallonsPerHour(self.filtered_df.fuel_consumption) #gph for all hours in the month
            self.ave_gph = self.getAveGPH()  #overall average gph, and standard error
            self.ave_gallons_by_hour = self.getAveGPH_byHour() #average gph, and standard error by hour of day
            self.ave_fuel_per_day = self.getAveFuelPerDay() #average and standard error per day

            # days_monitored is a tuple, first arg is timedelta , sencond is days integer

            self.cost_per_day = self.ave_fuel_per_day[0] * self.fuel_price



            self.gphddpm = pfuel.weather_adjusted_gallons_consumed_per_month(self.unfiltered_df,'outT','fuel_consumption')

            # estimated total gallons takes into account days that were not monitored (no data)
            self.estimated_total_gallons = self.getEstimatedGallons()

            if len(self.gphddpm) > 1:
                #progress is defined as the difference between the last value and the previous value divided by the previous value
                #proportion of last value that the current value is
                self.prog_usage = (self.gphddpm.iloc[-1] - self.gphddpm.iloc[-2]) / self.gphddpm.iloc[-2]
            else:
                self.prog_usage = 0

            # if the monitored days is within 12 hours of the total report duration then use the actual total_gallons
            # otherwise produces a hdd corrected estimate.
            if (self.days_monitored[0] < (self.report_duration + datetime.timedelta(hours=12))) & (
                    self.days_monitored[0] > (self.report_duration - datetime.timedelta(hours=12))):
                self.total_gallons = self.gallons
            else:
                self.total_gallons = self.estimated_total_gallons
                self.dataFlag = 1 #if flag is one then gallons is an estimate and not measured value

            #metrics based on total gallons
            self.gallons_per_ft = self.total_gallons / self.area # use total gallons
            self.total_cost = self.total_gallons * self.fuel_price #estimated cost (actual if no missing data)

            if self.neighborhood:  # if a neighborhood is provided use it to create comparison metrics
                self.compareNeighbors()

        return
    def getAveTemperature(self, t_field):
        ave = self.filtered_df[t_field].mean()
        sem = self.filtered_df[t_field].sem()
        return ave, sem
    def getAveGPH_byHour(self):
        '''average gallons per hour for each hour interval in a day - hours 0-23
        :return pandas series with hour index'''
        m = self.gph.groupby(self.gph.index.hour).mean()
        # s = self.gph.groupby(self.gph.index.hour).sem()
        return m
    def getAveGPH(self):

        m = float(self.gph.mean())
        s = float(self.gph.sem())
        return (m,s)
    def getAveFuelPerDay(self):
        gpd,gpm = pfuel.gallons_per_day_and_per_month(self.filtered_df, 'fuel_consumption')
        ave_gpd = float(gpd.mean()) # average gpd, and standard error
        sem_gpd = float(gpd.sem())
        return (ave_gpd, sem_gpd)
    def make_report(self):
        '''function calls for generating tex report with figures'''
        if self.title != None: #if a title is provided the report will get created, otherwise it is just for metrics
            try:
                os.mkdir(self.name)
            except:
                pass

        self.generateMetrics()

        self.makePlots()

        self.writeReport()
    def makePlots(self):
        '''plots are specific ot report subclass'''
        pass
    def getGallonsPerHour(self):
        '''mean gallons per hour by hour
        :returns pandas series'''
        return self.filtered_df.fuel_consumption.groupby(self.filtered_df.index.to_period('H')).agg('mean','sem')
    def getTip(self):
        '''tips are report subclass specific'''
        pass
    def writeReport(self):
        '''report text and layout is subclass specific'''
        pass
    def compare2Neighbors(self):
        '''Generate neighborhood metrics based on Neighborhood defined in self.neighborhood
        self.houses are excluded from the neighborhood metrics'''
        self.neighbor_usage = self.neighborhood.getTotalGallons(self.houses)
        self.neighbor_usage_per_area = self.neighborhood.getMeanGallonsPerFt(self.houses) #self.houses are not included in neighborhood
        self.neighbor_area = self.neighborhood.getTotalArea(self.houses)
    def setNeighborhood(self,neighborhood):
        #setter for neighborhood
        self.neighborhood = neighborhood
    def getDaysMonitored(self):
        '''Calculate the atcual time that is contained in the dataset, and round
        to day cout. monitored days is the actual number of days we have usable data
        not the duration that the dataset is suppose to cover'
        :return timedelta, integer number of days with atleast 6 hours of data'''

        time = (pd.Series(self.filtered_df.index))
        time.index = self.filtered_df.index
        dailydf = time.groupby(time.index.to_period('D')).diff()
        dailydf = dailydf.groupby(dailydf.index.to_period('D')).sum() # daily sampling duration
        dailydf.dt.round('H') #round to nearest hours
        actualTime = dailydf.sum()
        days = len(dailydf[dailydf > pd.to_timedelta(0.25, unit='day')]) #threshhold of 6 hours of data to be included in metrics
        return actualTime,days
    def getEstimatedGallons(self):
        '''estimate gallons for days without data
          and sum both the actual and estimated to produce an estimated total
          :returns float value of total gallons for the report time period'''

        hdd = ptemp.heat_degree_day(self.filtered_df, 65, 'outT') #returns a series of hdd values by day with actual gallons used per day
        gpd = pfuel.gallons_per_day_and_per_month(self.filtered_df, 'fuel_consumption')[0] #the first value in the returned tuple is dataframe by day

        gpd_hdd = hdd.join(gpd,how='outer')
        gpd_hdd['gphdd'] = gpd_hdd['fuel_consumption'] / gpd_hdd['hdd']

        #decide on a fill method and fill missing values
        #if gpd_hdd isn't missing any hdd we can generate estimated gpd based on mean gphdd * hdd and sum the resulting value for each day
        if len(gpd_hdd[pd.isnull(gpd_hdd['fuel_consumption'])]) > 0:
            #missing stove data for some days
            if len(gpd_hdd[pd.isnull(gpd_hdd['hdd'])]) <= 0:
                #fill missing gpd with estimate from mean gphdd and actual hdd value
                ave_gphdd  = gpd_hdd['gphdd'].mean()
                #fill missing fuel consumption days with hdd * average gphdd
                gpd_hdd.loc[pd.isnull(gpd_hdd['fuel_consumption']),'fuel_consumption'] = ave_gphdd * gpd_hdd.loc[pd.isnull(gpd_hdd['fuel_consumption']),'hdd']
            else:
                # fill missing fuel consumption days with average fuel/day
                gpd_hdd.loc[pd.isnull(gpd_hdd['fuel_consumption']), 'fuel_consumption'] = self.ave_fuel_per_day[0]


        eg = gpd_hdd['fuel_consumption'].sum() #the total is the sum of all days (actual and estimated)

        return eg
    def filterDataset(self):
        '''
        Read in the unified netcdf and generate dataframes of the necessary report data

        :return: DataFrame filtered to report time period
        :return: DataFrame filtered to earliest possible date up to end of report time period
        '''

        #start with a netcdf file generated from Data.puma2unified
        uni_nc = Dataset(self.unified_nc_file,'r')
        if not self.stoves:
            self.mergeStoves()

        #list of dataframes generated from each stove read in
        def makeCombinedDataframe(s):
            event_df = pd.DataFrame({
                          'fuel_consumption': uni_nc[s + '/Event/Clicks']['fuel_consumption'][:],
                          'gph': uni_nc[s + '/Event/Clicks']['fuel_consumption_rate'][:],
                          'clicks': uni_nc[s + '/Event/Clicks']['clicks'][:],
                            'inT': uni_nc[s + '/Event/Clicks']['indoor_temp'][:],
                          'stove': [s] * len(uni_nc[s + '/Event/Clicks']['time'][:])
                          },
                         index=pd.to_datetime(uni_nc[s + '/Event/Clicks']['time'][:],utc=True))

            timed_df = pd.DataFrame({'outT': uni_nc[s + '/Time']['outdoor_temp'][:],
                            'inT': uni_nc[s + '/Time']['indoor_temp'][:],
                            'deltaT':uni_nc[s + '/Time']['delta_temp'][:],
                            'stove': [s] * len(uni_nc[s + '/Time']['time'][:])},
                                    index=pd.to_datetime(uni_nc[s + '/Time']['time'][:], utc=True))

            df = pd.concat([event_df,timed_df],axis=0)
            timezone = pytz.timezone('US/Alaska')
            df.index = df.index.tz_convert(timezone) #convert to Alaska time so report reflects metrics based on local conditions
            df = df.sort_index(0)

            return df

        filtered_df_list = [makeCombinedDataframe(s.name) for s in self.stoves]

        filtered_df = pd.concat(filtered_df_list)
        filtered_df = filtered_df.sort_index(0)
        return filtered_df[self.start:self.end], filtered_df['2019-09-01':self.end] #all records up to end date



class MonthlyReport(Report):
    '''Monthly Report is a subclass of Report with custom functions for writing report text and calculating month specific metrics'''
    def __init__(self,start,end,title,nc,houses,fuel_price):
        super(MonthlyReport, self).__init__(start,end,title,nc,houses,fuel_price)
    def calculated_monthly_data(self):

        self.filtered_df.hdd = ptemp.heat_degree_day(pd.filtered_df,65)

        self.filtered_df.gphddpm = pfuel.run_weather_adjusted_gallons_per_month(pd.Series(self.filtered_df.index),self.filtered_df.gallons,self.filtered_df.hdd)

        return
    def isFirstMonth(self):
        try:
            tr = pd.date_range(self.unfiltered_df.index[0],self.unfiltered_df.index[-1],freq = 'M')
            if self.start > tr[1]:
                return False
            return True
        except:
            return True
    def writeReport(self):
        os.chdir(self.name)
        ptex.write_monthly_tex_var_file(pd.date_range(self.start, self.end, freq = 'D'),
                                        self.total_gallons,
                                        self.gallons_per_ft,
                                        self.fuel_price,
                                        self.ave_fuel_per_day[0],
                                        self.total_cost,
                                        self.cost_per_day,
                                        self.neighbor_usage_per_area[0],
                                        self.prog_usage,
                                        self.name,
                                        self.ave_indoorT[0],
                                        self.ave_outdoorT[0],
                                        self.tip_no,
                                        self.dataFlag,
                                        self.days_monitored[1]
                                        )

        #if this is the first report for the dataset don't compare to anything
        #otherwise compare to the previous month
        if self.isFirstMonth():
            ptex.write_monthly_tex_report_file(self.name, pd.date_range(self.start, self.end, freq = 'D'),None)
        else:
            ptex.write_monthly_tex_report_file(self.name, pd.date_range(self.start, self.end, freq='D'), pd.date_range(self.end, periods = 1,freq='M'))

        os.chdir('..')
    def getTip(self):
        self.getMonthlyTip()

    def getMonthlyTip(self):
        #assuming month 9 was tip 0
        self.tip_no = self.filtered_df.index[-1].month -9

    def makePlots(self):
        '''produces pngs of plots specific to this report'''
        os.chdir(self.name)
        pplot.plot_bar_progress(self.gphddpm,
                                'monthly_track_your_progress.png')
        if self.neighbor_usage_per_area !=0:

            pplot.plot_fuel_usage(self.gallons_per_ft, self.neighbor_usage_per_area[0], 'monthly_fuel_usage.png')
        if len(self.ave_gallons_by_hour)>0:
            pplot.polar_flow_plot_per_month_df(self.name,self.ave_gallons_by_hour,
                                                'monthly_polar_plot.png')
        os.chdir("..")