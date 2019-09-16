#Small script to run the puma text files to the unified netCDF4 file

#By Douglas Keller

import sys
import os

file_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(file_path,'..'))

import puma.data as pdata
import wget
from zipfile import ZipFile

snotel_file = os.path.join('..','..','data','temp','snotel.zip')

try:
    os.remove(snotel_file)
except:
    pass

try:
    wget.download('https://sensors.axds.co/stationsensorservice/getSensorNetcdf?stationid=11029&sensorid=6&jsoncallback=false&start_time=1430838000&end_time=1568239260',
                  out = snotel_file)
    
    with ZipFile(snotel_file,'r') as zip_file:
        zip_file.extractall(os.path.join('..','..','data','netcdf'))
        os.remove(os.path.join('..','..','data','netcdf','metadata.txt'))
        os.replace(os.path.join('..','..','data','netcdf','air_temperature.nc'),
                   os.path.join('..','..','data','netcdf','aoos_snotel_temp.nc'))
except:
    pass
    
try:
    pdata.puma_inv2yaml()
except:
    pass

os.remove(os.path.join('..','..','data','netcdf','puma_unified_data.nc'))
pdata.puma2uni_nc()