"""
Script to create a monthly report for each stove of interest

By Douglas Keller
"""
    
import os
import sys

file_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(file_path,'..'))

import puma.report as preport
import puma.time as ptime
import yaml
import multiprocessing as mp
import csv

unified_nc_file = os.path.join(file_path,'..','..','data','netcdf','puma_unified_data.nc')
report_stoves_file = os.path.join(file_path,'..','..','data','yaml','puma-monthly-report-inventory.yml')
control_stoves_file = os.path.join(file_path,'..','..','data','yaml','puma-monthly-report-control-inventory.yml')

report_stoves = []
with open(report_stoves_file) as report_stoves_file:
    yams = yaml.load(report_stoves_file) #getting stoves that reports will be made for
    for i in yams:
        report_stoves.append(i)
    
control_stoves = []
with open(control_stoves_file) as control_stoves_file:
    yams = yaml.load(control_stoves_file) #getting stoves that reports will be made for
    for i in yams:
        control_stoves.append(i)
    
os.chdir(os.path.join(file_path,'..','..','reports','monthly')) #moving to the reports/monthly directory

year = int(input('Enter the year of the report: '))
month = int(input('Enter the month of the report: '))
fuel_price = float(input('Current price of fuel: '))
#year = 2019
#month = 9
#fuel_price = 3
year_month = (year,month) #year and month of the report to print

begin_year_month = (2019,9)
end_year_month = (2020,5)
year_months = ptime.years_months(begin_year_month,end_year_month)

for i in range(len(year_months)):
    if year_months[i] == year_month:
        tip_no = i

for stove in report_stoves:
    if stove == 'FBK018':
        report_stoves.remove(stove)
        
for stove in control_stoves:
    if stove == 'FBK015' or stove == 'FBK020':
        control_stoves.remove(stove)

neighbor_stoves = control_stoves + report_stoves

names = []
addresses = []
treatment_group_file = os.path.join(file_path,'..','..','data','tmp','Treatment_Group.csv')
with open(treatment_group_file,newline='') as csvfile:
    treatment_group = csv.reader(csvfile,delimiter='\t')
    for line in treatment_group:
        names.append(line[0])
        addresses.append(line[1])

j = 0
while j < len(report_stoves):
    if j not in [1]:
        neighbor_stoves_mod = neighbor_stoves
        neighbor_stoves_mod.remove(report_stoves[j])
        preport.monthly_report(unified_nc_file,report_stoves[j],year_month,begin_year_month,end_year_month,year_months,fuel_price,neighbor_stoves_mod,tip_no,names[j],addresses[j])
    j += 1