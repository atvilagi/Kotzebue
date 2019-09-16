#File to create a monthly report
    
import os
import sys

file_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(file_path,'..'))

from netCDF4 import Dataset
import puma.time as ptime
import puma.report as preport

uni_nc_file = os.path.join(file_path,'..','..','data','netcdf','puma_unified_data.nc')

os.chdir(os.path.join(os.path.abspath(os.path.dirname(__file__)),'..','..','reports','monthly'))

uni_nc = Dataset(uni_nc_file,'r')
stoves = list(uni_nc.groups)
stove_comp_months = ptime.run_complete_months(uni_nc_file)

year_month = (2019,4)
mystove = stoves[1]
begin_year_month = (2019,2)
end_year_month = (2019,5)
preport.monthly_report(uni_nc_file,mystove,year_month,begin_year_month,end_year_month)