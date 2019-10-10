from netCDF4 import Dataset

file = Dataset('../../data/netcdf/aoos_snotel_temp.nc','r')
print(file)

