# Projet: fuelmeter-tools
# Created by: T.Morgan # Created on: 12/2/2019

import csv
class Stove:
    """
    Description: Stove attributes and processes
    Attributes: 
        location,area,stove_type
        
    """

    def __init__(self,name):
        self.location = [] #lat,long as list
        self.stove_type = None
        self.dataFolder
        self.rate = 0 #rate of fuel consumption per click
        self.name = name
    def __init__(self,name,location,stove_type):
        self.location = location
        self.stove_type = stove_type
        self.data_folder = None
        self.rate = 0
        self.name = name

    def lookupRate(self,stove_dict, fuel_click_file):
        '''
        looks up the rate of fuel consumption based on stove type
        :return: float rate
        '''

        fuel_click_file = open(fuel_click_file, 'r')
        with fuel_click_file as infile:
            reader = csv.reader(infile,delimiter=',')
            mydict = {rows[0]: rows[1] for rows in reader}

        return mydict[self.stove_type]

    def setRate(self,rate):
        self.rate = rate