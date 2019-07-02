#Created: Fri Jun 28 18:16:37 2019
#By: mach

def stove_csv(stove,product_file_name):
    
    product_file = Dataset(product_file_name,'r') #Opening the product netcdf data file
    
    with open(stove + '_final.csv','w',newline='') as stove_file:
        
        stove_csv_file = csv.writer(stove_file, dialect='excel')
        
        stove_csv_file.writerow([product_file[stove].description] + [''] + #Stove description and location
                                [product_file[stove]['lat'].description] + [str(product_file[stove]['lat'][:])] + 
                                [product_file[stove]['lon'].description] + [str(product_file[stove]['lon'][:])] + [''] + [''] + [''])
        
        stove_csv_file.writerow([product_file[stove]['time'].description] + [product_file[stove]['state'].description] + #Descriptions
                                [product_file[stove]['cumulative_clicks'].description] + [product_file[stove]['clicks'].description] + 
                                [product_file[stove]['fuel_consumption'].description] + [product_file[stove]['fuel_consumption_rate'].description] + 
                                [product_file[stove]['indoor_temp'].description] + [product_file[stove]['outdoor_temp'].description] + 
                                [product_file[stove]['delta_temp'].description])
        
        stove_csv_file.writerow([product_file[stove]['time'].units] + [product_file[stove]['state'].units] + #Units
                                [product_file[stove]['cumulative_clicks'].units] + [product_file[stove]['clicks'].units] +  
                                [product_file[stove]['fuel_consumption'].units] + [product_file[stove]['fuel_consumption_rate'].units] +
                                [product_file[stove]['indoor_temp'].units] + [product_file[stove]['outdoor_temp'].units] + 
                                [product_file[stove]['delta_temp'].units]) 
            
        for i in range(len(product_file[stove]['time'][:])):
        
            stove_csv_file.writerow([str(product_file[stove]['time'][i])] + [str(product_file[stove]['state'][i])] + #Values
                                    [str(product_file[stove]['cumulative_clicks'][i])] + [str(product_file[stove]['clicks'][i])] + 
                                    [str(product_file[stove]['fuel_consumption'][i])] + [str(product_file[stove]['fuel_consumption_rate'][i])] + 
                                    [str(product_file[stove]['indoor_temp'][i])] + [str(product_file[stove]['outdoor_temp'][i])] + 
                                    [str(product_file[stove]['delta_temp'][i])])
    
        product_file.close() #Closing the netCDF4 file
        print(stove)
        
from netCDF4 import Dataset
import yaml
import os
import csv
import multiprocessing as mp

product_file_name = '../puma_product_data.nc' #Location of the product netcdf data file in relation to the csv files

inv_file = input('Input the name of the inventory file for the data subset: ') #Asks for the user to input the name of the new yaml file with the particular inventory
file = open('../PuMA_Inventory/'+inv_file,'r') #Opening the inventory file of the stoves in the project
yams = yaml.load(file)
file.close()

os.chdir('../Data/Final_csv_Files')

stoves = [] #Making a list of the stove names
for stove in yams:
    stoves.append(stove)

if __name__ == '__main__':
    
    pool = mp.Pool(mp.cpu_count()) #Making a pool of processes (think of it as other initializations of python each running its own program)
    for stove in stoves:
        pool.apply_async(stove_csv,args=(stove,product_file_name)) #Asynchronous running of the stove_csv function to create csv files
    pool.close()
    pool.join()