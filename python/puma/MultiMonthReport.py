# Projet: fuelmeter-tools
# Created by: # Created on: 5/7/2020
from python.puma.Report import Report
import pandas as pd
import numpy as np
import python.puma.plot as pplot
import python.puma.tex as ptex
import datetime
#import python.puma.stats as stats
import os


class MultiMonthReport(Report):
    def __init__(self,start,end,title,nc,houses,monthly_fuel_price):
        super(MultiMonthReport, self).__init__(start,end,title,nc,houses,monthly_fuel_price)

    # def calculateMonthlyData(self):
    #     ranges = pd.DataFrame(index = pd.date_range(self.start,self.end,freq='M'))
    #     ranges['start'] = pd.Series(pd.to_datetime(ranges.index), index=ranges.index).apply(
    #         lambda dt: dt.replace(day=1))
    #     ranges['end'] = ranges['start'].apply(lambda st: st.replace(day=st.days_in_month))
    #
    #     for month,i in enumerate(ranges):
    #         self.collection.append()


    def getAveCostPerDay(self):
        if 'gpd_hdd' not in self.__dict__:
            self.cost_per_day = self.getCostPerDay(self.fuel_by_day)
        else:
            self.cost_per_day = self.getCostPerDay(self.gpd_hdd)
        return self.cost_per_day.mean()
    def getCostPerDay(self,fuel_by_day):
        self.fuel_price.name = 'fuel_price'
        #df = pd.concat([fuel_by_day, self.fuel_price], axis=1)
        df = pd.concat([fuel_by_day, self.fuel_price.groupby(self.fuel_price.index.to_period('D')).mean()], axis=1)
        df.fuel_price = df.fuel_price.ffill()  # filled for days that did not match

        return df.fuel_consumption * df.fuel_price
    def getEstimatedTotalGallons(self):
        self.gallons_by_month = self.calculateTotalGallonsByMonth()
        return self.gallons_by_month.sum()
    def getCostPerMonth(self):
        if self.cost_per_day == None:
            if 'gpd_hdd' in self.__dict__:
                self.cost_per_day = self.getCostPerDay(self.gpd_hdd)
            else:
                self.cost_per_day = self.getCostPerDay(self.fuel_by_day)
        self.cost_per_month = self.cost_per_day.groupby(pd.Grouper(freq="M")).sum()
    def getTotalCost(self, galByDay):
        #get a hdd corrected estimate
        costPerDay = self.getCostPerDay(galByDay)
        return costPerDay.sum()
    def compare2Neighbors(self):
        super().compare2Neighbors()
        self.meanMonthlyNeigborhoodGPFByYear,self.stdMonthlyNeigborhoodGPFByYear = self.neighborhood.getMeanMonthlyGPFByYear()

    def calculateTotalGallonsByMonth(self):
        '''Calculates the average gallons per day for each month'''
        groupedDaily = self.filtered_df['fuel_consumption'].groupby(pd.Grouper(freq="D")).sum() #total gallons each day
        self.meanDailyByMonth = groupedDaily.groupby(pd.Grouper(freq='M')).mean() #total daily gallons averaged over month
        estimatedTotalByMonth = self.meanDailyByMonth * self.meanDailyByMonth.index.days_in_month #use the average to calculate a total amount for the month
        return estimatedTotalByMonth
    def calculateMeanGallonsPerMonth(self):
        tgpm = self.calculateTotalGallonsByMonth()
        return tgpm.mean()
    def getGallonsPerFt(self):
        totalGPF = super().getGallonsPerFt()
        fbd = self.filtered_df['fuel_consumption'].groupby(self.filtered_df.index.to_period(freq='D')).sum()
        AveDailyByYear = self.filtered_df['fuel_consumption'].groupby(self.filtered_df.index.to_period(freq='A')).mean()
        self.aveGPFByYear = AveDailyByYear/self.area
        return  totalGPF

    def makePlots(self):
        '''produces pngs of plots specific to this report'''
        os.chdir(self.name)

        # #outDoor = pd.concat([self.ave_outdoorT[0],self.gphddpm], axis=1,join = 'outer')
        outDoor = self.ave_MonthlyoutdoorT['ave']
        if len(set(self.gphddBym.index.year))> 2:
            pplot.plot_multiyear_bar_progress_with_temperature(self.gphddBym, outDoor,
                                    'monthly_track_your_progress.png')
        else:
            pplot.plot_bar_progress(self.gphddBym, 'monthly_track_your_progress.png')

        if 'yearly_neighbor_usage_per_area' in self.__dict__:
            you = self.getMeanGallonsPerMonthPerAreaByYear()
            you.index = self.gallons_per_ft.index.year
            you.name = 'you'
            df = pd.concat([you, self.yearly_neighbor_ave_monthly_usage_per_area], join='inner', axis=1)
            pplot.plot_annual_fuel_usage(df, 'monthly_fuel_usage.png')

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
    def getAveCostPerYear(self):
        return self.ave_cost_per_day * 365

    def getMeanGallonsPerMonthPerAreaByYear(self):
        gpmpa = self.calculateTotalGallonsByMonth()/self.area
        AverageGPMPerArea = gpmpa.groupby(gpmpa.index.to_period('A')).mean()
        return AverageGPMPerArea
    def getYearlyNeigborhoodUsagePerArea(self):
        return self.neighborhood.getMeanMonthlyGPFByYear(self.houses)

    def getNeighborhoodUsagePerArea(self):
        return self.neighborhood.getUsageTable([])
    def compare2Neighbors(self):
        super().compare2Neighbors()
        self.yearly_neighbor_ave_monthly_usage_per_area, self.yearly_neighbor_usage_std_per_area =self.getYearlyNeigborhoodUsagePerArea()
        self.neighborhoodUsage = self.getNeighborhoodUsagePerArea()
        return
    def generateSummaryTable(self,cost):
        combinedData = pd.concat([np.round(self.gallons_by_month,2), np.round(self.meanDailyByMonth,4), np.round(self.ave_MonthlyindoorT['ave'], 0), np.round(self.ave_MonthlyoutdoorT['ave'], 0)], axis=1)
        combinedData.columns = ['total_gal_by_month','ave_daily_by_month','ave_indoor_t_by_month','ave_outdoor_t_by_month']
        combinedData['ave_daily_cost_by_month'] = np.round(combinedData['ave_daily_by_month'] * cost,2)
        combinedData['total_cost_by_month'] = np.round(combinedData['total_gal_by_month'] * cost,2)
        self.estimatedCostByMonth = combinedData['total_cost_by_month']
        combinedData['month_year'] = [datetime.datetime.strftime(pd.to_datetime(i),format="%b %y") for i in combinedData.index]
        combinedData = combinedData.astype(str)
        combinedData = combinedData.astype(dtype=pd.StringDtype())
        combinedData['total_cost_by_month'] = "\$" + combinedData['total_cost_by_month']
        combinedData['ave_daily_cost_by_month'] = "\$" + combinedData['ave_daily_cost_by_month']
        subset = combinedData[['month_year','ave_daily_by_month','ave_daily_cost_by_month','total_gal_by_month', 'total_cost_by_month','ave_indoor_t_by_month','ave_outdoor_t_by_month']]
        myTable = [tuple(x) for x in subset.to_numpy()]
        # myTable=[('Jan 19','3.5','7','1','9','2','46.8'),
        #          ('Feb 19', '3.0', '7', '1.8', '9', '2', '46.8')]
        return myTable
    def generateHighMonths(self):
        highMonths = ['January','February']
        highValue = np.percentile(self.gallons_by_month, 90)
        highMonths = self.gallons_by_month[self.gallons_by_month > highValue].index.month

        return [datetime.datetime.strftime(datetime.datetime(2020, h, 1), format="%B") for h in highMonths]
    def generateMetrics(self):
        super().generateMetrics()
        self.gpm = self.calculateMeanGallonsPerMonth() #gpm is an estimated average per month
        self.aveYearlyCost = self.getAveCostPerYear()
        if self.filtered_df.index[0].hour == 2:
            self.reportRange = pd.date_range((self.filtered_df.index[0] + pd.to_timedelta('1 h')), self.filtered_df.index[-1], freq = 'D')
        else:
            self.reportRange = pd.date_range(self.filtered_df.index[0], self.filtered_df.index[-1], freq='D')
        self.summaryTable = self.generateSummaryTable(self.fuel_price.mean())
        self.highMonths = self.generateHighMonths()
        self.statsInput = self.getStatsInput()
        return
    def getStatsInput(self):
        df = pd.DataFrame({'stove':self.name,
                           'area':max([float(house.area) for house in self.houses]),
                           'latitude': min([float(house.location[0]) for house in self.houses]),
                            'longitude': min([float(house.location[1]) for house in self.houses]),
                            'fuel':self.fuel_by_day.copy(),'outdoorT':self.ave_DailyOutdoorT, 'indoorT':self.ave_DailyIndoorT},index=self.fuel_by_day.index)


        return df
    def writeReport(self):
        os.chdir(self.name)
        #try:
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

        #if this is the first report for the dataset don't compare to anything
        #otherwise compare to the previous month
        ptex.write_multimonth_tex_report_file(self.name, pd.date_range(self.start, self.end, freq = 'D'))
        # except Exception as e:
        #     print("could not generate report for ", self.name)

        os.chdir('..')