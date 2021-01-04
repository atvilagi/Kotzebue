"""
Small script to run the puma text files to the unified netCDF4 file

By Douglas Keller
"""

import sys
import os
import warnings


#allowing relative sister path imports
file_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(file_path,'..'))

from puma.PumaData import PumaData
#from datetime import datetime
#import wget
#from zipfile import ZipFile

#TODO remove local test
#os.chdir('e:\\PUMA\\fuelmeter-tools\\') #temporary fix for testing locally
snotel_file = os.path.join('..','..','data','tmp','snotel.zip')
os.chdir(os.path.join(file_path,'..','..', 'data','tmp'))

if __name__ == '__main__':

    # try:
    #     os.remove(snotel_file)  # removing snotel file if it exists
    # except:
    #     pass
    # print(os.getcwd())
    # end_time = str(int(datetime.timestamp(datetime.utcnow())))
    # # file = wget.download(
    # #     'https://sensors.axds.co/stationsensorservice/getSensorNetcdf?stationid=11029&sensorid=6&jsoncallback=false&start_time=1430838000&end_time=' + end_time)  # downloads the snotel zipfile containing the temperature data
    # # os.replace(file, snotel_file)
    # #
    # # with ZipFile(snotel_file, 'r') as zip_file:  # expanding the zip file
    # #     zip_file.extractall(os.path.join('..', '..', 'data', 'netcdf'))
    # #     os.remove(os.path.join('..', '..', 'data', 'netcdf', 'metadata.txt'))
    # #     os.replace(os.path.join('..', '..', 'data', 'netcdf', 'air_temperature.nc'),
    # #                os.path.join('..', '..', 'data', 'netcdf', 'aoos_snotel_temp.nc'))
    #
    # try:
    #     PumaData.puma_inv2yaml()  # updating the inventory file
    # except:
    #     pass

    try:
        os.remove(os.path.join('..', '..', 'data', 'netcdf', 'puma_unified_data.nc'))
    except:
        pass

    #myData= PumaData("e:\\PUMA\\ftp-data")
    myData = PumaData() #using default data locations
    myData.puma2uni_nc()