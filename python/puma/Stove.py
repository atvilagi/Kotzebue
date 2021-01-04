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
        self.stoveType = None
        self.dataFolder
        self.rate = 0 #rate of fuel consumption per click
        self.name = name

    def __init__(self,name,stove_type, adjustment=[1],initiation=['1/1/2018']):
        self.stoveType = stove_type.split(",")
        self.dataFolder = None
        self.rate = 0
        self.name = name
        if initiation == None:
            initiation = ['1/1/2018']
        else:
            initiation = initiation.split(",")
        if adjustment == None:
            adjustment = ['1']
        elif type(adjustment) == float:
            adjustment = [str(adjustment)]
        else:
            adjustment = adjustment.split(",")
        self.initiation = initiation
        self.adjustment = adjustment #list of adjustments

    def lookupRate(self,stove_dict, fuel_click_file):
        '''
        looks up the rate of fuel consumption based on stove type
        :return: float rate
        '''

        fuel_click_file = open(fuel_click_file, 'r')
        with fuel_click_file as infile:
            reader = csv.reader(infile,delimiter=',')
            mydict = {rows[0]: rows[1] for rows in reader}

        return mydict[self.stoveType]

    def setRate(self,rate):
        self.rate = rate