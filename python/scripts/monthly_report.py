"""
Script to create a monthly report for each stove of interest

By Douglas Keller and T. Morgan
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
from puma.Report import MonthlyReport



import puma.bash as pbash
import datetime
import yaml

unified_nc_file = os.path.join(file_path,'..','..','data','netcdf','puma_unified_data.nc')
report_stoves_file = os.path.join(file_path,'..','..','data','yaml','puma-monthly-report-inventory.yml')
control_stoves_file = os.path.join(file_path,'..','..','data','yaml','puma-monthly-report-control-inventory.yml')
report_houses_file = os.path.join(file_path,'..','..','data','yaml','puma-monthly-report-house-inventory.yml')
control_houses_file = os.path.join(file_path,'..','..','data','yaml','puma-monthly-report-control-house-inventory.yml')

with open(report_houses_file) as report_houses_file:
    yamh = yaml.load(report_houses_file)

    report_houses = [House(i,yamh.get(i)['Square Footage']) for i in yamh]
with open(report_stoves_file) as report_stoves_file:
    yams = yaml.load(report_stoves_file)
    for h in report_houses:
        stoves = h.name.split("-")
        h.stoves = [Stove(s, yams.get(s)['Location'], yams.get(s)['Stove Type']) for s in stoves]

with open(control_houses_file) as control_houses_file:
    yamh = yaml.load(control_houses_file)

    control_houses = [House(i, yamh.get(i)['Square Footage']) for i in yamh]
with open(control_stoves_file) as control_stoves_file:
    yams = yaml.load(control_stoves_file)
    for h in control_houses:
        # for now house names are the combined stove names - could use address
        stoves = h.name.split("-")
        h.stoves = [Stove(s, yams.get(s)['Location'], yams.get(s)['Stove Type']) for s in stoves]

working_dir = os.path.join(file_path,'..','..','reports','monthly') #moving to the reports/monthly directory

#check if the folder exists and make it if it doesn't
if not os.path.exists(working_dir):
    os.mkdir(working_dir)
os.chdir(working_dir)


year = int(input('Enter the year of the reports: '))
month = int(input('Enter the month of the reports: '))

timezone = pytz.timezone('US/Alaska')
startDate = datetime.datetime(year,month,1,0,0,0,0)
startDate = timezone.localize(startDate,timezone)
if month == 12:
    month = 0
    year += 1

endDate = datetime.datetime(year,month + 1,1,0,0,0,0)
endDate = timezone.localize(endDate,timezone)

dateRange = pd.date_range(startDate, endDate, freq='D')
fuel_price = float(input('Current price of fuel: '))
year_month = (year,month) #year and month of the report to print

begin_year_month = (2019,9)
end_year_month = (2020,5)

excludeControlList = ['FBK015','FBK020']
try:
    [control_houses.remove(h) for h in control_houses if h.name in excludeControlList]
except:
    pass


neighborhood = Neighborhood('FBK',report_houses + control_houses)


for house in neighborhood.houses:
    try:
        print("starting house: ", house.name)

        neighborhood.reports[house.name] = MonthlyReport(startDate,endDate,None,unified_nc_file,[house],fuel_price)
        neighborhood.reports[house.name].generateMetrics() #generate metrics but not text for report and control houses
        print("ending house: ", house.name)

    except Exception as e:
        print(e)
        print("failed stove: ", house.name)
        os.chdir(working_dir)


#reports only have house metrics at this point
#add in neighborhood metrics
for house in report_houses:
    try:
        neighborhood.reports[house.name].setNeighborhood(neighborhood)
        neighborhood.reports[house.name].compare2Neighbors()#report function to add neighborhood comparisons
    except Exception as e:
        print(e)
        print("unable to provide neighbor metrics for: ",house.name)
    finally:
        if not os.path.exists(house.name):
            os.mkdir(house.name)
        neighborhood.reports[house.name].makePlots()
        neighborhood.reports[house.name].writeReport()


#TODO remove test metric printing
for r in neighborhood.reports.keys():
    print(neighborhood.reports[r].name)
    print("total gallons: ",neighborhood.reports[r].total_gallons)
    print("gallons per ft: ", neighborhood.reports[r].gallons_per_ft)
    print("gallons per hdd: ",neighborhood.reports[r].gphddpm)
    print("neighborhood gallons: ",neighborhood.reports[r].neighbor_usage_per_area)
    print("report duration: ", neighborhood.reports[r].report_duration)
    print("monitored days: ", neighborhood.reports[r].days_monitored[1])


pbash.bash_monthly_reports(dateRange)
print('bash file made')
