"""
Script to create a monthly report for each stove of interest

T. Morgan
"""
    
import os
import sys
import pandas as pd
import pytz
import warnings
# warnings.simplefilter("error")
# warnings.simplefilter("ignore",SyntaxError)
# warnings.simplefilter("ignore",ImportWarning)

#allowing sister path imports
file_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(file_path,'..'))

from puma.Stove import Stove
from puma.House import House
from puma.Neigborhood import Neighborhood
from puma.MultiMonthReport import MultiMonthReport

import numpy as np



import puma.bash as pbash
import datetime
import yaml

unified_nc_file = os.path.join(file_path,'..','..','data','netcdf','puma_unified_data.nc')
stoves_file = os.path.join(file_path,'..','..','data','yaml','puma-inventory.yml')
houses_file = os.path.join(file_path,'..','..','data','yaml','puma-houses.yml')

with open(stoves_file) as stoveFile:
    yams = yaml.safe_load(stoveFile)


def makeStoves(stoveNameList):
    splitNames = stoveNameList.split(",") #make a list
    return [Stove(name,yams.get(name)['Stove Type']) for name in splitNames]



with open(houses_file) as report_houses_file:
    yamh = yaml.safe_load(report_houses_file)

    report_houses = [House(i,yamh.get(i)['Square Footage'],yamh.get(i)['Location'], makeStoves(yamh.get(i)['Stove'])) for i in yamh if yamh.get(i)['Report'] is True]
    control_houses = [House(i, yamh.get(i)['Square Footage'], yamh.get(i)['Location'], makeStoves(yamh.get(i)['Stove']))
                     for i in yamh if yamh.get(i)['Report'] is False]

report_houses = report_houses + control_houses
#TODO remove temporary filter for house FBK004
#report_houses = [house for house in report_houses if (house.name == 'FBK004') | (house.name == 'FBK044')]

#neighborhood = Neighborhood('FBK',report_houses + control_houses)
neighborhood = Neighborhood('FBK',report_houses.copy())
working_dir = os.path.join(file_path,'..','..','reports','multiyear') #moving to the reports/monthly directory

#check if the folder exists and make it if it doesn't
if not os.path.exists(working_dir):
    os.mkdir(working_dir)
os.chdir(working_dir)


startyear = 2018
startmonth = 1

lastyear = 2020
lastmonth = 4

timezone = pytz.timezone('US/Alaska')
startDate = datetime.datetime(startyear,startmonth,1,0,0,0,0)
startDate = timezone.localize(startDate,timezone)
if lastmonth == 12:
    lastmonth = 0
    lastyear += 1

endDate = datetime.datetime(lastyear,lastmonth + 1,1,0,0,0,0)
endDate = timezone.localize(endDate,timezone)

dateRange = pd.date_range(startDate, endDate, freq='D')

year_month = (lastyear,lastmonth) #year and month of the report to print

begin_year_month = (2018,9)
end_year_month = (2020,5)

excludeControlList = ['FBK015','FBK020']
try:
    [control_houses.remove(h) for h in control_houses if h.name in excludeControlList]
except:
    pass
monthly_fuel_price = pd.Series([3.5] *28,index=pd.date_range(startDate,endDate,freq='M'))
#for house in neighborhood.houses:
for house in report_houses:
    try:
        print("starting house: ", house.name)

        house.report = MultiMonthReport(startDate,endDate,None,unified_nc_file,[house],monthly_fuel_price)
        house.report.generateMetrics() #generate metrics but not text for report and control houses
        print("ending house: ", house.name)

    except Exception as e:
        print(e)
        print("failed stove: ", house.name)
        neighborhood.houses.remove(house)
        print("House dropped from neighborhood")
        os.chdir(working_dir)



#reports only have house metrics at this point
#add in neighborhood metrics
neighborhood.applyStatsModels()

for house in report_houses:
        try:
            house.report.setNeighborhood(neighborhood)
            house.report.compare2Neighbors()#report function to add neighborhood comparisons
        except Exception as e:
            print(e)
            print("unable to provide neighbor metrics for: ",house.name)
        finally:
            if not os.path.exists(house.name):
                os.mkdir(house.name)
            if house in neighborhood.houses:
                house.report.moveModelImages(house.name)
                house.report.makePlots()
                house.report.writeReport()


pbash.bash_multimonth_reports(dateRange)
print('bash file made')
