"""
Small script to run the product netCDF4 file to the csv files for distribution

By Douglas Keller
"""

import sys
import os

file_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(file_path,'..'))

import puma.data as pdata

pdata.prod_nc2csv()