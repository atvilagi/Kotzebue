#By: Doug
#Created: Fri Jul 19 15:38:17 2019

from netCDF4 import Dataset
import os

file_path = os.path.abspath(os.path.dirname(__file__))

new_nc = os.path.join(file_path,'..','Data','netCDF_Files','puma_unified_data.nc')
merged_file = Dataset(new_nc,'r',format='NETCDF4')

print(merged_file['ATV000'].getncattr('Location'))
print(merged_file['ATV000'])
