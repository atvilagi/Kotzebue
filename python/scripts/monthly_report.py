"""
Script to create a monthly report for each stove of interest

By Douglas Keller
"""
    
import os
import sys

file_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(file_path,'..'))

import puma.report as preport
import yaml
import multiprocessing as mp

uni_nc_file = os.path.join(file_path,'..','..','data','netcdf','puma_unified_data.nc')
report_stoves_file = os.path.join(file_path,'..','..','data','yaml','puma-monthly-report-inventory.yml')

report_stoves = []
yams = yaml.load(report_stoves_file) #getting stoves that reports will be made for
for i in yams:
    report_stoves.append(i)
    
os.chdir(os.path.join(os.path.abspath(os.path.dirname(__file__)),'..','..','reports','monthly')) #moving to the reports/monthly directory

year = int(input('Enter the year of the report: '))
month = int(input('Enter the month of the report: '))
year_month = (year,month) #year and month of the report to print

begin_year_month = (2019,9)
end_year_month = (2020,5)

pool = mp.Pool(mp.cpu_count()) 
for stove in report_stoves: #creating a report for each desired stove in multiple processes
    pool.apply_async(preport.monthly_report,args=(uni_nc_file,stove,year_month,begin_year_month,end_year_month)) 
pool.close()
pool.join()