"""
The data class contains functions related to data manipulation and archiving
By T. Morgan
"""

from netCDF4 import Dataset
import numpy as np
import csv
import os
import multiprocessing as mp
import yaml
import pandas as pd
import pytz
import datetime


from puma.Stove import Stove

class PumaData:

    def __init__(self,ftp_dir =None, air_dir =None):
        self.df_dictionary = {}
        self.directory = os.path.abspath(os.path.dirname(__file__))
        if ftp_dir:
            self.ftp_dir = ftp_dir
        if air_dir:
            self.air_dir = air_dir

    @classmethod
    def puma_inv2yaml(cls):
        '''update the inventory file from csv file'''
        file_path = os.path.abspath(os.path.dirname(__file__))
        csv_file = os.path.join(file_path,'..','..','data','temp','PuMA Units + SIMS - Sheet1.csv')

        csv_data = []
        with open(csv_file,'r') as file:
            puma_csv_data = csv.reader(file, delimiter=',')

            for line in puma_csv_data:
                csv_data.append(line)

        inventory = {}
        for line in csv_data[1::]:
            if line[6] != 'ATV000':
                inventory[line[6]] = {'Stove Type': line[4],
                         'Location': [float(line[-2]), float(line[-1])],
                         'Square Footage': line[8]}

        inv_file = os.path.join(file_path,'..','..','data','yaml','puma-inventory.yml')

        with open(inv_file,'w') as file:
            file.write(yaml.dump(inventory))

    #### Text to netCDF files
    def pumatxt2data(self,stove_file):
        '''
        reads in a text file, creates a dataframe and adds that dataframe
        :param stove_file: string path to a standardized PUMA text file containing stove data (assumed to be formated from PUMA files)
        :return: pandas Dataframe created from input text file
        '''

        #read from csv file
        try:
            df = pd.read_csv(stove_file,delimiter='\t')
            df.columns = ['time', 'state', 'cumulative_clicks', 'thermistor']
            #df['filename'] = str(stove_file)
            #remove incomplete rows of data
            df = df.dropna(axis=0, how='any')

            #cumulative clicks and state set to NA for off states
            df.loc[df.state == 'X','cumulative_clicks'] = np.nan
            df.loc[df.state == 'X','state'] = np.nan
            df.loc[df.state == '5', 'cumulative_clicks'] = np.nan #state 5 indicates a reset to cum clicks = 0

            #make the time field and index and drop it as a column
            df['time'] = pd.to_datetime(df['time'],unit ='s', utc=True) #Time is recorded and stored as UTC time
            df = df.set_index(pd.to_datetime(df['time'].tolist(), utc=True),drop=False)
            df = df.astype({'state':float,'cumulative_clicks':float,'thermistor':float}) #set datatypes
            return df
        except Exception as e:
            print((f"error reading {stove_file}"))
            print(e)
            return None

    # def file2data(self, stove_file,result):
    #     '''read in a single file into a dataframe and store the result
    #     multi-processor safe method of reading in multiple files'''
    #     stove_df = self.pumatxt2data(stove_file)
    #     result.put(stove_df)
    #
    # def dir2data(self):
    #     '''reads in all files within a directory into a single dataframe'''
    #
    #     file_list = self.getStoveFiles()
    #
    #     result = mp.Manager().Queue()
    #     # # Instantiating a multiprocess safe buffer (needed for multiprocessing)
    #     pool = mp.Pool(mp.cpu_count())
    #     # #Making a pool of processes (think of it as other initializations of python
    #     # #each running its own program)
    #     for file in file_list:
    #          pool.apply_async(self.file2data,args=(file,result)) #Asynchronous running of the file2data_mp function on the text files
    #     pool.close()
    #     pool.join()
    #
    #     stove_df = pd.DataFrame()
    #
    #     while not result.empty():  # Extracting results from the multiprocessing
    #         if len(stove_df) < 1:
    #             stove_df = result.get()
    #         else:
    #             stove_df = stove_df.append(result.get()) #results is a list of dataframes for a given stove
    #
    #
    #     return stove_df

    def file2data(self, stove_file):
        '''read in a single file into a dataframe and store the result
        multi-processor safe method of reading in multiple files'''
        return self.pumatxt2data(stove_file)


    def dir2data(self):
        '''reads in all files within a directory into a single dataframe'''

        file_list = self.getStoveFiles()
        stove_df = pd.DataFrame()
        # #Making a pool of processes (think of it as other initializations of python
        # #each running its own program)
        for file in file_list:
            file_df = self.pumatxt2data(file) #Asynchronous running of the file2data_mp function on the text files
            if (file_df is not None):
                if len(stove_df) < 1:
                    stove_df =file_df
                else:
                    stove_df = stove_df.append(file_df) #results is a list of dataframes for a given stove

        return stove_df

    def stove_data_polish(self,df):
        #Runs both the data_sort function and the remove_duplicates_list function
        #and then changes the list back to a list of lists [time,intT,outT,dT,status,clicks]

        df = df.sort_index(axis=0)
        df = df.loc[~df.index.duplicated(keep='first')]

        return df

    #### Time Arrays

    def raw2time(self, air_df,df):
        '''Creates the temperature metrics.
        :param air_df is a dataframe of external air temperatures with datetime index
        :param df is a dataframe with thermistor values and a datetime index
        :return dataframe with all original data plus external temperature, indoor temperature and delta temperature'''
        #Creating temperature metrics
        df = self.outdoorT(air_df, df)  #outdoor temperature from external file
        df = self.indoorT(df)               #indoor temparture calculated from thermistor values
        df = self.deltaT(df)               #difference between in and out tempeartures
        return df

    #### Events


    def raw_time2event(self, df,stove):
        '''calculate metrics associated with event data.
        :param df is a dataframe with datetime index and cumulative click column
        :param stove is the name of a stove as described in the stove inventory yaml file
        :return the original dataframe with addition columns of gallons and clicks'''

        df = self.cumulative_clicks2clicks(df) #calculate the difference between clicks
        df = self.run_clicks2gallons(df,stove)
        df = self.galperhour(df)
        return df

    def cumulative_clicks2clicks(self,df):
        '''calculates the number of clicks between sequential click records
        :param df is a dataframe with cumulative_clicks column and datetime index
        :return original dataframe with additional clicks column'''
        #flag bad data and don't use it to calculate clicks

        df.loc[pd.notnull(df['cumulative_clicks']), 'clicks'] = (
                    df.loc[pd.notnull(df['cumulative_clicks'])]['cumulative_clicks'].shift(-1) -
                    df.loc[pd.notnull(df['cumulative_clicks'])]['cumulative_clicks']).shift()
        # negative clicks occurr when two input txt files condain overlapping dates, but different cumulative click values
        # the entire day with messed up values gets dropped
        badDays = df[df['clicks'] < 0].index
        for d in list(set(badDays.date)):
            baddate = d
            df = df[df.index.date != baddate]
        #clicks need to be recalculated then
        df.loc[pd.notnull(df['cumulative_clicks']), 'clicks'] = (
                df.loc[pd.notnull(df['cumulative_clicks'])]['cumulative_clicks'].shift(-1) -
                df.loc[pd.notnull(df['cumulative_clicks'])]['cumulative_clicks']).shift()

        df.loc[pd.notnull(df['cumulative_clicks']), 'timediff'] = ((
                df.loc[pd.notnull(df['cumulative_clicks'])]['time'].shift(-1) -
                df.loc[pd.notnull(df['cumulative_clicks'])]['time']).shift()) / pd.to_timedelta(1, 'h')



        df['clicksperhour'] = df['clicks'] / df['timediff']

        #outliers get dropped
        df=df[(df['clicksperhour'] <= df['clicksperhour'].mean() + (3 * df['clicksperhour'].std())) | (pd.isnull(df['cumulative_clicks']))]
        df = df.drop(['clicksperhour','timediff'], axis=1)

        df=df[df.state !=5] #get rid of state 5 now we don't need it anymore
        df.is_copy = False #suppress SettingWithCopyWarning - we know its a copy
        return df

    def clicks2gallons(self, df, rate):
        '''Determines the fuel pumped from the clicks counted by the PuMA device
        clicks is the difference in clicks between rows
        rate is read in as a string so cast to float
        :param df is a dataframe with clicks column
        :param rate is a string, int or float representing the number of gallons consumed per click
        :return original dataframe with additional gallons column'''
        df['gallons'] = df['clicks'] * float(rate)
        return df

    def run_clicks2gallons(self, df, stove):
        ''' Looks up stove rate and runs clicks2gallons function with the returned rate value
        :param df: a pandas dataframe with clicks column
        :param stove: A Stove object with attribute stove_type
        :return: original dataframe with additional gallons column
        '''
        rate = self.rate_dict[stove.stoveType]
        df = self.clicks2gallons(df,rate)
        return df

    def galperhour(self, df):
        '''Calculates the US gallons per hour
        :param df is a pandas dataframe with gallons column and datetime index
        :return original dataframe with additional gph column
        '''

        df['timedelta'] = df.index.to_series().diff().dt.seconds.div(60, fill_value=0) #in minutes
        df['gph'] = df['gallons']/(df['timedelta'] *60)
        return df

    def deltaT(self, df):
        '''Computes the difference in temperature of the indoor and outdoor temperatures'
        :param df is a dataframe with indoorT and outdoorT columns
        :returns original dataframe with additional deltaT column'''

        df['deltaT'] = df['indoorT'] -df['outdoorT']
        return df

    def indoorT(self, df):
        '''Computes the indoor temperature from the thermistor value collected by the
        PUMA device
        :param df is a dataframe with thermistor column
        :return original dataframe with additional indoorT column'''

        df.loc[df['thermistor']!= 0,'indoorT'] = round(((3.354*10**-3 + (2.56985*10**-4)*np.log(df.loc[df['thermistor']!= 0,'thermistor']/10000) + #This is the function returning temp. from thermistor values; may return a NaN
                    (2.620131*10**-6)*np.log( df.loc[df['thermistor']!= 0,'thermistor']/10000)**2 +
                    (6.383091*10**-8)*np.log( df.loc[df['thermistor']!= 0,'thermistor']/10000)**3)**-1 - 273.15)*1.8 + 32, 2)

        return df

    def outdoorT(self, air_df,df):
        '''Joins the outdoor temperature dataframe to the indoor timestamps
        If an indoor timestamp falls between outdoor temperatures linear interpolation is used to fill in the value
        All outdoor temperatures are retained even if there is now matching indoor timestamp.
        :param air_df is a dataframe of air temperatures with a datetime index
        :param df is a dataframe wiht datetime index
        :return original dataframe with additional outdoorT column
        '''

        df = df.join(air_df,how='outer') #outer join retains all air and df rows
        df['outT'] = df['outT'].interpolate(method='linear')
        df['outdoorT'] = round(df['outT'], 2)
        return df

    #### Data Packaging Metafunctions

    def nc_createVariables(self, nc_file,variables,unit_type,dependent_variable):
        #Creating variables in the netCDF4 file
        for i in range(len(variables)):
            nc_file.createVariable(variables[i],unit_type[i],(dependent_variable))

    def nc_description_set(self, nc_file,variables,descriptions):
        #Creating descriptions in the netCDF4 file to make it more portable
        for i in range(len(variables)):
            nc_file[variables[i]].description = descriptions[i]

    def nc_units_set(self,nc_file,variables,unit):
        #Creating units in the netCDF4 file to make it more portable
        for i in range(len(variables)):
            nc_file[variables[i]].units = unit[i]

    def fill_nc(self,nc_file,v,data):
        #Filling the netCDF4 files
        print(v)
        nc_file[v][:] = data[v].values

    def nc_transfer_variables(self,old_nc,new_nc,variables):
        #Transferring the variables from the old netCDF4 file to the new one
        for variable in variables:
            new_nc[variable][:] = old_nc[variable][:]

    def nc_transfer_attributes(self,old_nc,new_nc,attributes):
        #Transferring the attributes from the old netCDF4 file to the new one
        for att in attributes:
            new_nc.setncattr(att,old_nc.getncattr(att))

    def getFtpDirectory(self):
        '''returns a path to the set ftp directory or the default ftp directory if none was set'''
        try:
            return self.ftp_dir
        except AttributeError as e:
            return os.path.join(self.directory, '..', '..', '..', 'ftp-data')

    def makeRateDict(self):
        '''reads in the set fuel_click_file or a default fuel click file if none was set and converts it to a dictionary
        with stove type as key and rates as values.
        :return dictionary of rates by stove type'''
        try:
            self.fuel_click_file
        except AttributeError as e:
            self.fuel_click_file = os.path.join(self.directory, '..', '..', 'data', 'text', 'FuelClickConversion.txt')
        finally:
            rate_dict = self.generateRateDictionary(self.fuel_click_file)
        return rate_dict

    def getAirTemp(self,start,end):
        '''creates a dataframe of outdoor air temperature based on the specified airTempFile. If not is specified it uses a default file
        :param start the beginning date for air temperature
        :param end date for air temperature
        :return dataframe of air temperature in F with datetime index truncated to specified start and end dates (in utc Time)'''
        try:
            self.airTempFile
        except AttributeError as e:
            airTempFile = os.path.join(self.directory, '..', '..', 'data', 'netcdf', 'aoos_snotel_temp.nc')
        finally:
            at_data = Dataset(airTempFile, 'r')
            # Assuming air temperature file from NRCS Snotel observations in netCDF form
            air_temp = at_data.variables['air_temperature'][:]
            if 'C' in at_data['air_temperature'].units or 'c' in at_data[
                'air_temperature'].units:  # Checking the unit type if Celsius is used
                air_temp = air_temp * 9 / 5 + 32
            at_time = at_data.variables['time'][:]
            # complete dataframe of air temperature truncated to dataset duration
            # large time periods can be missing temperature data
            air_df = pd.DataFrame({'outT': air_temp, 'outTime': at_time},
                                  index=pd.to_datetime(at_time, unit='s', utc=True))  # using UTC time
            air_df = air_df[start:end]

        return air_df

    #### Scriptstyle Functions

    def puma2uni_nc(self):

        file_path = os.path.abspath(os.path.dirname(__file__))
        #contributing datasets
        self.rate_dict = self.makeRateDict()
        ftp_data = self.getFtpDirectory()
        yaml_file = os.path.join(file_path, '..', '..', 'data', 'yaml', 'puma-inventory.yml')
        stove_list, yams = self.getStoveList(yaml_file)

        #define the netcdf
        new_nc = os.path.join(self.directory,'..','..','data','netcdf','puma_unified_data.nc')
        merged_file = Dataset(new_nc,'w',format='NETCDF4') #Making a netCDF4 file for the final data product (netCDF4 allows for grouping, which is used per stove later)

        new_nc_att = {'Contents':'netCDF file that contains the stoves in the fuel meter project, found in individual groups','Variables':'variables in each stove group are: time, cumulative clicks, clicks per interval, fuel consumption per interval, fuel consumption rate per interval, indoor temperature, outdoor temperature, temperature difference, stove status per interval'}
        merged_file.setncatts(new_nc_att)

        #stepping into ftp_data folder
        os.chdir(ftp_data)
        dir_list = os.listdir()
        dir_list.sort()
        stoves = [s for s in stove_list if s.name in dir_list]
        print('Stove data collated:')
        print([s.name for s in stoves])
        #stoves = [s for s in stoves if s.name == 'FBK045']
        #read and merge all datafiles per stove
        for stove in stoves:
            merged_file.createGroup(stove.name)

            #Creating a netCDF4 group for each stove
            merged_file[stove.name].setncatts(yams[stove.name])

            #### Raw data section ####
            merged_file[stove.name].createGroup('Raw')
            merged_file[stove.name +'/Raw'].createDimension('time',None)

            raw_variables = ['time','state','cumulative_clicks','thermistor']

            raw_descriptions = ['Timestamp of each PUMA device reading',
                                'State of the stove when powered on; depends on the stove type the PuMA device is attached to',
                                'Number of cumulative clicks since PuMA installation the fuel pump solenoid makes when the stove turns on',
                                'Thermistor resistance of the indoor thermistor']

            raw_units = ['Time since 1970, 1, 1, 00:00:00 UTC (Unix time)',
                         'Integer units corresponding to power states; -1 indicates powered off',
                         'Number of cumulative clicks; -1 indicates stove powered off',
                         'Thermistor resistance (ohms)']

            raw_unit_types = ['f8','i4','i8','i8']

            self.nc_createVariables(merged_file[stove.name+'/Raw'],raw_variables,raw_unit_types,'time')
            self.nc_description_set(merged_file[stove.name+'/Raw'],raw_variables,raw_descriptions)
            self.nc_units_set(merged_file[stove.name+'/Raw'],raw_variables,raw_units)

            #### Time based data section ####

            merged_file[stove.name].createGroup('Time')
            merged_file[stove.name+'/Time'].createDimension('time',None)

            time_variables = ['time','indoor_temp','outdoor_temp','delta_temp']

            time_descriptions = ['Timestamp of each PUMA device reading',
                                 'Indoor temperature read by the thermistor monitored by the PUMA device',
                                 'Outdoor temperature interpolated using area temperature data from Snotel',
                                 'Temperature difference between the indoor and outdoor temperatures']

            time_units = ['Time since 1970, 1, 1, 00:00:00 UTC (Unix time)',
                          'F','F','F']

            time_unit_types = ['f8','f4','f4','f4']

            self.nc_createVariables(merged_file[stove.name+'/Time'],time_variables,time_unit_types,'time')
            self.nc_description_set(merged_file[stove.name+'/Time'],time_variables,time_descriptions)
            self.nc_units_set(merged_file[stove.name+'/Time'],time_variables,time_units)

            #### Event based data section ####
            merged_file[stove.name].createGroup('Event/Raw')
            merged_file[stove.name].createGroup('Event/Clicks')
            merged_file[stove.name+'/Event/Raw'].createDimension('time',None)
            merged_file[stove.name+'/Event/Clicks'].createDimension('time',None)

            event_variables = ['time','state','cumulative_clicks','indoor_temp',
                               'outdoor_temp','delta_temp']

            event_descriptions = ['Timestamp of each PUMA device reading',
                                  'State of the stove when powered on; depends on the stove type the PuMA device is attached to',
                                  'Number of cumulative clicks since PuMA installation the fuel pump solenoid makes when the stove turns on',
                                  'Indoor temperature read by the thermistor monitored by the PUMA device',
                                  'Outdoor temperature interpolated using area temperature data from Snotel',
                                  'Temperature difference between the indoor and outdoor temperatures']

            event_units = ['Time since 1970, 1, 1, 00:00:00 UTC (Unix time)',
                           'Integer units corresponding to power states; -1 indicates powered off',
                           'Number of cumulative clicks; -1 indicates stove powered off',
                           'F','F','F']

            click_variables = ['time','clicks','state','indoor_temp','outdoor_temp',
                               'delta_temp','fuel_consumption','fuel_consumption_rate']

            click_descriptions = ['Timestamp of the clicks per interval',
                                  'Number of clicks the fuel pump solenoid makes when the stove turns on per time interval',
                                  'State of the stove per interval of clicks',
                                  'Indoor temperature per interval','Outdoor temperature per interval',
                                  'Temperature difference per interval',
                                  'The amount of fuel consumed by the stove','The fuel consumption rate of the stove']

            click_units = ['Time since 1970, 1, 1, 00:00:00 UTC (Unix time)','Number of clicks',
                           'Integer units corresponding to power states; -1 indicates powered off',
                           'F','F','F','US gallons','US gallons per hour']

            event_unit_types = ['f8','i4','i8','f4','f4','f4']

            click_unit_types = ['f8','i8','i4','f4','f4','f4','f8','f8']

            self.nc_createVariables(merged_file[stove.name+'/Event/Raw'],event_variables,event_unit_types,'time')
            self.nc_description_set(merged_file[stove.name+'/Event/Raw'],event_variables,event_descriptions)
            self.nc_units_set(merged_file[stove.name+'/Event/Raw'],event_variables,event_units)
            self.nc_createVariables(merged_file[stove.name+'/Event/Clicks'],click_variables,click_unit_types,'time')
            self.nc_description_set(merged_file[stove.name+'/Event/Clicks'],click_variables,click_descriptions)
            self.nc_units_set(merged_file[stove.name+'/Event/Clicks'],click_variables,click_units)

            os.chdir(stove.name) #Changing to the stove directory
            print(f"Loading data for {stove.name} {datetime.datetime.now()}")
            # recursively read the stove data into a dataframe
            stove_data = self.dir2data()
            print(f"Completed loading data for {stove.name} {datetime.datetime.now()}")
            os.chdir('..')
            print(stove.name)
            [self.fill_nc(merged_file[stove.name+'/Raw'],v, stove_data) for v in raw_variables]
            #make the end date the end of the month
            mytimezone = pytz.timezone('UTC')
            enddate = mytimezone.localize(max(stove_data.index).to_period('M').to_timestamp())

            #add in air_temperature for timed records
            air_temp = self.getAirTemp(min(stove_data.index),enddate)

            stove_data = self.raw2time(air_temp,stove_data)
            #becomes copy here

            #fill in event data metrics
            stove_data = self.raw_time2event(stove_data,stove)
            #remove duplicate indices, incomplete rows of data and sort
            stove_data = self.stove_data_polish(stove_data)
            stove_data.columns = ['time', 'state', 'cumulative_clicks', 'thermistor', 'outT', 'outTime', 'outdoor_temp',
                              'indoor_temp', 'delta_temp', 'clicks', 'fuel_consumption', 'timedelta',
                              'fuel_consumption_rate']

            #time determined data is the portion of data without cumulative click values
            #these values can be identified as records with NA for cumulative_clicks (this will include temperature only records)
            #as a cautionary note both temperature and stove data can be missing chunks of time
            #if there is no stove time, temperature timestamp is used as a substitute
            # stove_data['time'] = stove_data['time'].dt.tz.localize(mytimezone)
            stove_data['time'] = (stove_data['time'] - datetime.datetime(1970, 1, 1, tzinfo=pytz.timezone('UTC'))).dt.total_seconds()
            stove_data.loc[pd.isnull(stove_data['time']),'time'] = stove_data.loc[pd.isnull(stove_data['time']),'outTime']
            print(stove.name)
            [self.fill_nc(merged_file[stove.name+'/Time'],v,stove_data[pd.isnull(stove_data['cumulative_clicks'])]) for v in time_variables]

            #events are records with cumulative click values
            [self.fill_nc(merged_file[stove.name+'/Event/Clicks'],v,stove_data[pd.notnull(stove_data['cumulative_clicks'])]) for v in click_variables]

        merged_file.close() #Closing the netCDF4 file


    def getStoveList(self,yaml_file):
        '''creates a list of Stove objects created from attributes in the specified yaml file
        :param the file path to a yaml file contiaining stove information
        :return list of Stove objects
        :return dictionary from yaml file'''

        with open(yaml_file, 'r') as file:
            # Opening the inventory file of the stoves in the project
            yams = yaml.load(file)

        stove_list = []
        # Making a list of the stove names
        for i in yams:
            stove_list.append(Stove(i,yams.get(i)['Stove Type']))
        return stove_list,yams

    def getStoveFiles(self):
        #assumes function is getting called from the stove directory - all files found assumed to belong to same stove
        # traverse stove directory, and list directories as dirs and files as files
        txtfiles = []

        for root, dirs, files in os.walk(os.getcwd()):
            for file in files:
                if (file[-3:] == 'txt') & (file[-7:] != 'LOG.txt'):
                    txtfiles.append(os.path.join(root,file))

        return txtfiles


    def uni_nc2prod_nc(self):

        file_path = os.path.abspath(os.path.dirname(__file__))

        uni_nc = os.path.join(file_path,'..','..','data','netcdf','puma_unified_data.nc')
        unified_file = Dataset(uni_nc,'r') #Opening the central unified data

        new_nc = input('Input the name of the new netCDF file with the packaged data: ')
        prod_nc = os.path.join(file_path,'..','..','data','netcdf',new_nc)
        product_file = Dataset(prod_nc,'w',format='NETCDF4') #Opening the output file

        prod_nc_att = {'Contents':'netCDF file that contains the stoves in the fuel meter project, found in individual groups','Variables':'variables in each stove group are: time, cumulative clicks, clicks per interval, fuel consumption per interval, fuel consumption rate per interval, indoor temperature, outdoor temperature, temperature difference, stove status per interval'}
        product_file.setncatts(prod_nc_att)

        inv_file = input('Input the name of the inventory file for the data subset: ') #Asks for the user to input the name of the new yaml file with the particular inventory
        yaml_file = os.path.join(file_path,'..','..','data','yaml',inv_file)
        file = open(yaml_file,'r')
        #Opening the inventory file of the stoves in the project
        yams = yaml.load(file)
        file.close()

        name_list = []
        #Making a list of the stove names
        for i in yams:
            name_list.append(i)

        stoves = []
        #Making a list of the stove names
        for stove in yams:
            stoves.append(stove)

        for stove in stoves:

            product_file.createGroup(stove)
            #Creating a netCDF4 group for each stove

            attributes = ['Location','Stove Type','Square Footage']

            self.nc_transfer_attributes(unified_file[stove],product_file[stove],attributes)

            #### Raw data section ####

            product_file[stove].createGroup('Raw')
            product_file[stove+'/Raw'].createDimension('time',None)

            raw_variables = ['time','state','cumulative_clicks','thermistor']

            raw_descriptions = ['Timestamp of each PUMA device reading',
                                'State of the stove when powered on; depends on the stove type the PuMA device is attached to',
                                'Number of cumulative clicks since PuMA installation the fuel pump solenoid makes when the stove turns on',
                                'Thermistor resistance of the indoor thermistor']

            raw_units = ['Time since 1970, 1, 1, 00:00:00 UTC (Unix time)',
                         'Integer units corresponding to power states; -1 indicates powered off',
                         'Number of cumulative clicks; -1 indicates stove powered off',
                         'Thermistor resistance (ohms)']

            raw_unit_types = ['f8','i4','i8','i8']

            self.nc_createVariables(product_file[stove+'/Raw'],raw_variables,raw_unit_types,'time')
            self.nc_description_set(product_file[stove+'/Raw'],raw_variables,raw_descriptions)
            self.nc_units_set(product_file[stove+'/Raw'],raw_variables,raw_units)

            self.nc_transfer_variables(unified_file[stove+'/Raw'],product_file[stove+'/Raw'],raw_variables)

            #### Time based data section ####

            product_file[stove].createGroup('Time')
            product_file[stove+'/Time'].createDimension('time',None)

            time_variables = ['time','indoor_temp','outdoor_temp','delta_temp']

            time_descriptions = ['Timestamp of each PUMA device reading',
                                 'Indoor temperature read by the thermistor monitored by the PUMA device',
                                 'Outdoor temperature interpolated using area temperature data from Snotel',
                                 'Temperature difference between the indoor and outdoor temperatures']

            time_units = ['Time since 1970, 1, 1, 00:00:00 UTC (Unix time)',
                          'F','F','F']

            time_unit_types = ['f8','i4','i8','i8','f8','f8','f4','f4','f4']

            self.nc_createVariables(product_file[stove+'/Time'],time_variables,time_unit_types,'time')
            self.nc_description_set(product_file[stove+'/Time'],time_variables,time_descriptions)
            self.nc_units_set(product_file[stove+'/Time'],time_variables,time_units)

            self.nc_transfer_variables(unified_file[stove+'/Time'],product_file[stove+'/Time'],time_variables)

            #### Event based data section ####

            product_file[stove].createGroup('Event/Raw')
            product_file[stove].createGroup('Event/Clicks')

            product_file[stove+'/Event/Raw'].createDimension('time',None)


            product_file[stove+'/Event/Clicks'].createDimension('time',None)

            event_variables = ['time','state','cumulative_clicks','indoor_temp',
                               'outdoor_temp','delta_temp']

            event_descriptions = ['Timestamp of each PUMA device reading',
                                  'State of the stove when powered on; depends on the stove type the PuMA device is attached to',
                                  'Number of cumulative clicks since PuMA installation the fuel pump solenoid makes when the stove turns on',
                                  'Indoor temperature read by the thermistor monitored by the PUMA device',
                                  'Outdoor temperature interpolated using area temperature data from Snotel',
                                  'Temperature difference between the indoor and outdoor temperatures']

            event_units = ['Time since 1970, 1, 1, 00:00:00 UTC (Unix time)',
                           'Integer units corresponding to power states; -1 indicates powered off',
                           'Number of cumulative clicks; -1 indicates stove powered off',
                           'F','F','F']

            click_variables = ['time','clicks','state','indoor_temp','outdoor_temp',
                               'delta_temp','fuel_consumption','fuel_consumption_rate']

            click_descriptions = ['Timestamp of the clicks per interval',
                                  'Number of clicks the fuel pump solenoid makes when the stove turns on per time interval',
                                  'State of the stove per interval of clicks',
                                  'Indoor temperature per interval','Outdoor temperature per interval',
                                  'Temperature difference per interval',
                                  'The amount of fuel consumed by the stove','The fuel consumption rate of the stove']

            click_units = ['Time since 1970, 1, 1, 00:00:00 UTC (Unix time)','Number of clicks',
                           'Integer units corresponding to power states; -1 indicates powered off',
                           'F','F','F','US gallons','US gallons per hour']

            event_unit_types = ['f8','i4','i8','f4','f4','f4']

            click_unit_types = ['f8','i8','i4','f4','f4','f4','f8','f8']

            self.nc_createVariables(product_file[stove+'/Event/Raw'],event_variables,event_unit_types,'time')
            self.nc_description_set(product_file[stove+'/Event/Raw'],event_variables,event_descriptions)
            self.nc_units_set(product_file[stove+'/Event/Raw'],event_variables,event_units)
            self.nc_createVariables(product_file[stove+'/Event/Clicks'],click_variables,click_unit_types,'time')
            self.nc_description_set(product_file[stove+'/Event/Clicks'],click_variables,click_descriptions)
            self.nc_units_set(product_file[stove+'/Event/Clicks'],click_variables,click_units)

            self.nc_transfer_variables(unified_file[stove+'/Event/Raw'],product_file[stove+'/Event/Raw'],event_variables)
            self.nc_transfer_variables(unified_file[stove+'/Event/Clicks'],product_file[stove+'/Event/Clicks'],click_variables)

        product_file.close()
        #Closing the netCDF4 file and you're done!

        return stoves,prod_nc

    def stove_csv(self,stove,group,product_file_name):

            product_file = Dataset(product_file_name,'r')
            #Opening the product netcdf data file

            def nc2csv_descriptions(nc):

                desc_list =  []
                for var in nc.variables:
                    desc_list.append(nc[str(var)].description)

                return desc_list

            def nc2csv_units(nc):

                unit_list =  []
                for var in nc.variables:
                    unit_list.append(nc[str(var)].units)

                return unit_list

            if '/' in group:
                group_name = group[0:5] + '_' + group[6::]
            else:
                group_name = group

            with open(stove + '_' + group_name + '.csv','w',newline='') as stove_file:

                stove_csv_file = csv.writer(stove_file, dialect='excel')

                group_dir = stove + '/' + group

                stove_csv_file.writerow(['Stove Type'] + [product_file[stove].getncattr('Stove Type')] + #Stove description and location
                                        ['Latitude'] + [str(product_file[stove].getncattr('Location')[0])] +
                                        ['Longitude'] + [str(product_file[stove].getncattr('Location')[1])] +
                                        ['Square Footage'] + [str(product_file[stove].getncattr('Square Footage'))] + [''])

                desc = nc2csv_descriptions(product_file[group_dir])
                stove_csv_file.writerow(desc)

                unit = nc2csv_units(product_file[group_dir])
                stove_csv_file.writerow(unit)

                for i in range(len(product_file[group_dir]['time'][:])):

                    row = []
                    for var in product_file[group_dir].variables:
                        row.append(str(product_file[group_dir][str(var)][i]))

                    stove_csv_file.writerow(row)

                product_file.close()
                #Closing the netCDF4 file
                print(group_dir)

    def generateRateDictionary(self,csvpath):
        rate_dict = {}
        with open(csvpath, 'r') as csvfile:
            text = csv.reader(csvfile, delimiter=',')
            for row in text:
                rate_dict[row[0]]=row[1]
        return rate_dict

    def prod_nc2csv(self):

        stoves,product_file_name = self.uni_nc2prod_nc()

        file_path = os.path.abspath(os.path.dirname(__file__))

        csv_files = os.path.join(file_path,'..','..','data','csv')
        os.chdir(csv_files)

        groups = ['Raw','Time','Event/Raw','Event/Clicks']

        pool = mp.Pool(mp.cpu_count())
        #Making a pool of processes (think of it as other initializations of python
        #each running its own program)
        for stove in stoves:
            for group in groups:
                pool.apply_async(self.stove_csv,args=(stove,group,product_file_name))
                #Asynchronous running of the stove_csv function to create csv files
        pool.close()
        pool.join()


    def puma2csv(self):
        self.puma2uni_nc()
        self.prod_nc2csv()
