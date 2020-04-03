# Projet: fuelmeter-tools
# Created by: # Created on: 12/2/2019

class House:
    """
    Description: A house can be made up of 1 or more stoves, and contains metrics of all stoves it contains
    Attributes: 
        stoves,metrics
        
    """

    def __init__(self, name,area):
        self.stoves = [] #list of stoves contained within a house
        self.name = name
        self.area = area
        self.location = []  # lat,long as list
        self.report = None #a Report of house fuel related metrics for a specified time frame
        self.reportCollection = {} #collection of monthly reports

    def __init__(self, name,area,location,stoves):
        self.stoves = stoves #list of stoves contained within a house
        self.name = name
        self.area = area
        self.location = location # lat,long as list
        self.report = None #a Report of house fuel related metrics for a specified time frame

        