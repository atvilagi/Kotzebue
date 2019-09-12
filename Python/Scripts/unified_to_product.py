#Small script to run the unified netCDF4 file to the product netCDF4 file

#By Douglas Keller

import sys
import os

file_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(file_path,'..'))

import puma.data as pdata

pdata.uni_nc2prod_nc()