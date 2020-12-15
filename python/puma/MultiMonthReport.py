# Project: fuelmeter-tools
# Created by: # Created on: 5/7/2020
from pandas.tseries.offsets import MonthEnd
from puma.Report import Report
import pandas as pd
import numpy as np
import puma.plot as pplot
import puma.tex as ptex
import datetime

import os


class MultiMonthReport(Report):
    def __init__(self,start,end,title,nc,houses,monthly_fuel_price):
        super(MultiMonthReport, self).__init__(start,end,title,nc,houses,monthly_fuel_price)


    def getAveCostPerDay(self):
        '''calculates the average cost of fuel per day. If the attribute gph_hdd
        is available this will be used to calculate costs otherwise the attribute
        fuel_by_day is used.'''
        if 'gpd_hdd' not in self.__dict__:
            self.cost_per_day = self.getCostPerDay(self.fuel_by_day)
        else:
            self.cost_per_day = self.getCostPerDay(self.gpd_hdd)
        return self.cost_per_day.mean()
    def getCostPerDay(self,fuel_by_day):
        '''calculate cost for each day based on a fuel price for each day and fuel consumption for each day'''
        self.fuel_price.name = 'fuel_price'
        df = pd.concat([fuel_by_day, self.fuel_price.groupby(pd.Grouper(freq='D')).mean()], axis=1)
        df.fuel_price = df.fuel_price.ffill()  # filled for days that did not match
        return df.fuel_consumption * df.fuel_price
    def getEstimatedTotalGallons(self):
        '''calculates the total gallons used each month and sets the attribute gallons_by_month
        :return float total gallons for the entire report period'''
        self.gallons_by_month = self.calculateTotalGallonsByMonth()
        return self.gallons_by_month.sum()
    def getCostPerMonth(self):
        '''calculates the total cost of consumed fuel per month by summing cost per day for every day within a month'''
        if self.cost_per_day == None:
            if 'gpd_hdd' in self.__dict__:
                self.cost_per_day = self.getCostPerDay(self.gpd_hdd)
            else:
                self.cost_per_day = self.getCostPerDay(self.fuel_by_day)
        self.cost_per_month = self.cost_per_day.groupby(pd.Grouper(freq="M")).sum()
        return
    def getTotalCost(self):
        '''uses hdd corrected estimate of fuel consumption to estimate cost per day and aggregate to the entire report period.'''
        costPerDay = self.getCostPerDay(self.gpd_hdd)
        return costPerDay.sum()

    def calculateTotalGallonsByMonth(self):
        '''Calculates the total gallons consumed by month based on an average daily consumption rate for each month'''
        groupedDaily = self.filtered_df['fuel_consumption'].groupby(pd.Grouper(freq="D")).sum() #total gallons each day
        self.meanDailyByMonth = groupedDaily.groupby(pd.Grouper(freq='M')).agg(['mean','count']) #total daily gallons averaged over month
        self.meanDailyByMonth = self.meanDailyByMonth.loc[self.meanDailyByMonth['count'] >=15,'mean'] #drop months with fewer than 20 days of data
        estimatedTotalByMonth = self.meanDailyByMonth * self.meanDailyByMonth.index.days_in_month #use the average to calculate a total amount for the month
        return estimatedTotalByMonth
    def calculateMeanGallonsPerMonth(self):
        '''get the average gallons consumed for all months in the reporting period'''
        tgpm = self.calculateTotalGallonsByMonth()
        return tgpm.mean()
    def getGallonsPerFt(self):
        '''get the total gallons used in the report period per house area (square feet).
        sets the aveGPFByYear attribute which is the totalGPF for each year averaged over all years.
        :return float total gallons per house square footage for the report period'''
        totalGPF = super().getGallonsPerFt()
        AveDailyByYear = self.filtered_df['fuel_consumption'].groupby(pd.Grouper(freq='A')).mean()
        self.aveGPFByYear = AveDailyByYear/self.area
        return  totalGPF

    def makePlots(self):
        '''produces pngs of plots specific to this report'''
        os.chdir(self.name)
        outDoor =  self.ave_MonthlyoutdoorT['ave']

        pplot.plot_multiyear_bar_progress_with_temperature(self.gphddBym, outDoor[self.start:self.end],
                                    'monthly_track_your_progress.png')

        you = self.getMeanGallonsPerMonthPerAreaByYear()
        you.name = 'you'
        df = pd.concat([you, self.yearly_neighbor_ave_monthly_usage_per_area], join='inner', axis=1)
        pplot.plot_annual_fuel_usage(df, 'fuel_usage.png')
        gph = pd.DataFrame(self.gph,index = self.gph.index)
        gph['season'] = 0
        gph.loc[(gph.index.month >= 1) & (gph.index.month <= 3), 'season'] = 1
        gph.loc[(gph.index.month >= 4) & (gph.index.month <= 6), 'season'] = 2
        gph.loc[(gph.index.month >= 7) & (gph.index.month <= 9), 'season'] = 3
        gph.loc[(gph.index.month >= 10) & (gph.index.month <= 12), 'season'] = 4
        ave_gal_by_hour_by_season = gph.groupby([gph.season, gph.index.hour]).mean()
        pplot.seasonal_polar_flow_plot(ave_gal_by_hour_by_season,
                                                'seasonal_polar_plot.png')

        os.chdir("..")
        return

    def getAveCostPerYear(self):
        '''calculate the average cost per year based on the average daily cost for the report period'''
        return self.ave_cost_per_day * 365

    def getMeanGallonsPerMonthPerAreaByYear(self):
        gpmpa = self.calculateTotalGallonsByMonth()/self.area
        AverageGPMPerArea = gpmpa.groupby(pd.Grouper(freq='A')).mean()
        return AverageGPMPerArea
    def getYearlyNeigborhoodUsagePerArea(self):
        return self.neighborhood.getMeanMonthlyGPFByYear(self.houses)

    def getNeighborhoodUsagePerArea(self):
        return self.neighborhood.getUsageTable([])
    def compare2Neighbors(self):
        '''generate neighborhood metrics'''
        super().compare2Neighbors()
        self.yearly_neighbor_ave_monthly_usage_per_area, self.yearly_neighbor_usage_std_per_area =self.getYearlyNeigborhoodUsagePerArea()
        self.neighborhoodUsage = self.getNeighborhoodUsagePerArea()
        return
    def generateSummaryTable(self,cost):
        '''create a summary table of fuel usage, costs and temperatures by month'''
        combinedData = pd.concat([np.round(self.gallons_by_month,2), np.round(self.meanDailyByMonth,4), np.round(self.ave_MonthlyindoorT['ave'], 0), np.round(self.ave_MonthlyoutdoorT['ave'], 0)], axis=1)
        combinedData.columns = ['total_gal_by_month','ave_daily_by_month','ave_indoor_t_by_month','ave_outdoor_t_by_month']
        combinedData['ave_daily_cost_by_month'] = np.round(combinedData['ave_daily_by_month'] * cost,2)
        combinedData['total_cost_by_month'] = np.round(combinedData['total_gal_by_month'] * cost,2)
        self.estimatedCostByMonth = combinedData['total_cost_by_month']
        combinedData['month_year'] = [datetime.datetime.strftime(pd.to_datetime(i),format="%b %y") for i in combinedData.index]
        combinedData['total_cost_by_month'] = combinedData['total_cost_by_month'].map('\${:,.2f}'.format)
        combinedData['ave_daily_cost_by_month'] = combinedData['ave_daily_cost_by_month'].map('\${:,.2f}'.format)
        combinedData = combinedData[self.reportRange[0]:self.reportRange[-1]]
        combinedData = combinedData.astype(str)
        #combinedData = combinedData.astype(dtype=pd.StringDtype())

        subset = combinedData[['month_year','ave_daily_by_month','ave_daily_cost_by_month','total_gal_by_month', 'total_cost_by_month','ave_indoor_t_by_month','ave_outdoor_t_by_month']]

        myTable = [tuple(x) for x in subset.to_numpy()]
        return myTable
    def generateHighMonths(self):
        '''calculate which months are in the 90th percentile for fuel consumption for the entier report period based on gallons_by_month attribute
        :return list of string month names'''
        highValue = np.percentile(self.gallons_by_month, 90)
        highMonths = self.gallons_by_month[self.gallons_by_month > highValue].index.month
        return [datetime.datetime.strftime(datetime.datetime(2020, h, 1), format="%B") for h in highMonths]
    def generateMetrics(self):
        super().generateMetrics() #generate all the metrics used in monthly reports
        self.gpm = self.calculateMeanGallonsPerMonth() #gpm is an estimated average per month
        self.aveYearlyCost = self.getAveCostPerYear()
        firstIndex = self.filtered_df[pd.notnull(self.filtered_df['fuel_consumption'])].index[0]
        lastIndex = self.filtered_df[pd.notnull(self.filtered_df['fuel_consumption'])].index[-1] + MonthEnd(1)
        if lastIndex.month == firstIndex.month:
            lastIndex = lastIndex + pd.to_timedelta('1d')

        if firstIndex.hour == 2: #starting a sequence at 2 am will result in an error once day light savings time ends
            firstIndex = firstIndex + pd.to_timedelta('1 h')
        elif firstIndex.hour == 1:
            firstIndex = firstIndex + pd.to_timedelta('2 h')

        self.reportRange = pd.date_range(firstIndex, lastIndex, freq='D')

        #values reported in multiyear report
        self.summaryTable = self.generateSummaryTable(self.fuel_price.mean())
        self.highMonths = self.generateHighMonths()
        self.statsInput = self.getStatsInput()
        return
    def getStatsInput(self):
        '''generates a dataframe to be used for estimating temperature based fuel consumption'''
        df = pd.DataFrame({'stove':self.name,
                           'area':max([float(house.area) for house in self.houses]),
                           'latitude': min([float(house.location[0]) for house in self.houses]),
                            'longitude': min([float(house.location[1]) for house in self.houses]),
                            'fuel':self.fuel_by_day.copy(),'outdoorT':self.ave_DailyOutdoorT, 'indoorT':self.ave_DailyIndoorT},index=self.fuel_by_day.index)


        return df
    def writeReport(self):
        '''write the multiyear report tex file into the report directory for the specific house'''
        os.chdir(self.name)
        ptex.write_multimonth_tex_var_file(self.reportRange,
                                           self.total_gallons,  #total gallons for duration of study -eliminate
                                           self.getMeanGallonsPerMonthPerAreaByYear().mean(),  #mean monthly gallons per month per area
                                           self.ave_fuel_per_day[0],  #average gallons per day for entire study - eliminate
                                           self.total_cost,  # total cost dependent on estimate gallons used and price by month
                                           self.ave_cost_per_day,
                                           self.yearly_neighbor_ave_monthly_usage_per_area.mean(),  # mean overage fuel gallons per area for neighborhood
                                           self.prog_usage,
                                           self.name,
                                           self.ave_MonthlyindoorT['ave'],  #indoor temperature by month
                                           self.aveYearlyCost,  #average daily cost extrapolated to a year
                                           self.dataFlag,
                                           self.days_monitored[1],  #actual number of days we recieved data
                                           len(self.neighborhood.houses),
                                           self.highMonths, self.summaryTable,
                                           np.round(self.fuel_price.mean(),2)  #the average fuel price to report
                                           )


        ptex.write_multimonth_tex_report_file(self.name, pd.date_range(self.start, self.end, freq = 'D'))

        os.chdir('..')