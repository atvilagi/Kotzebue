#Created: Wed Aug  7 18:26:59 2019
#By: mach

from netCDF4 import Dataset
import matplotlib.pyplot as plt
import os
import numpy as np
from datetime import datetime
import pytz
from pandas.plotting import register_matplotlib_converters
import puma_data as pdata

#pdata.puma2uni_nc()
#pdata.uni_nc2prod_nc()
#pdata.prod_nc2csv()

#timeAK = pytz.timezone('America/Anchorage')
#
#file_path = os.path.abspath(os.path.dirname(__file__))
#
#uni_nc_file = os.path.join(file_path,'..','Data','netCDF_Files','puma_unified_data.nc')
#test_file = os.path.join(file_path,'..','Data','netCDF_Files','test.nc')
#uni_nc = Dataset(uni_nc_file,'r')
#nc = Dataset(test_file,'r')
#
#stoves = list(uni_nc.groups)
#stove = stoves[0]
#
#u_nc = uni_nc[stove]
#
#groups = list(u_nc.groups)
#
#group = groups[2]
#
#unc = u_nc[group]
#    
##for var in unc.variables:
##    print(len(unc[var][:]))
##    for i in range(len(unc[var][:])):
##        print(unc[var][i])