"""
Small script to run the puma text files to the unified netCDF4 file

By Douglas Keller
"""

import sys
import os

file_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(file_path,'..'))

import puma.data as pdata
from datetime import datetime
import wget
from zipfile import ZipFile

snotel_file = os.path.join('..','..','data','tmp','snotel.zip')

try:
    os.remove(snotel_file) #removing snotel file if it exists
except:
    pass

try:
    end_time = str(int(datetime.timestamp(datetime.utcnow())))
    wget.download('https://sensors.axds.co/stationsensorservice/getSensorNetcdf?stationid=11029&sensorid=6&jsoncallback=false&start_time=1430838000&end_time='+end_time,
                  out = snotel_file) #downloads the snotel zipfile containing the temperature data
    
    with ZipFile(snotel_file,'r') as zip_file: #expanding the zip file
        zip_file.extractall(os.path.join('..','..','data','netcdf'))
        os.remove(os.path.join('..','..','data','netcdf','metadata.txt'))
        os.replace(os.path.join('..','..','data','netcdf','air_temperature.nc'),
                   os.path.join('..','..','data','netcdf','aoos_snotel_temp.nc'))
except:
    pass
    
try:
    pdata.puma_inv2yaml() #updating the inventory file
except:
    pass

try:
    os.remove(os.path.join('..','..','data','netcdf','puma_unified_data.nc'))
except:
    pass

pdata.puma2uni_nc() #making the unified netCDF4 file of PuMA data