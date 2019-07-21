#By: Doug
#Created: Fri Jul 19 15:38:17 2019

from netCDF4 import Dataset
import os
import puma_data as pdata
import yaml

file_path = os.path.abspath(os.path.dirname(__file__))
#inv_file = input('Input the name of the inventory file for the data subset: ') #Asks for the user to input the name of the new yaml file with the particular inventory
yaml_file = os.path.join(file_path,'..','Data','yaml_Files','puma-inventory-marco_18-19.yml')
file = open(yaml_file,'r') #Opening the inventory file of the stoves in the project
yams = yaml.load(file)
file.close()

yams2 = {'FBK001':yams['FBK001'],'FBK002':yams['FBK002']}
yaml_file2 = os.path.join(file_path,'..','Data','yaml_Files','puma-inventory-test.yml')
file = open(yaml_file2,'w')
yaml.dump(yams2,file)
file.close()

#pdata.prod_nc2csv()
#
#file_path = os.path.abspath(os.path.dirname(__file__))
#
#new_nc = os.path.join(file_path,'..','Data','netCDF_Files','puma_unified_data.nc')
#merged_file = Dataset(new_nc,'r',format='NETCDF4')
#
#print(merged_file['ATV000'].getncattr('Location'))
#print(merged_file['ATV000'])
#print(merged_file)
