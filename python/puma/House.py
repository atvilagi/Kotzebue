# Project: fuelmeter-tools
# Created by: T. Morgan# Created on: 12/2/2019

class House:
    """
    Description: A house can be made up of 1 or more stoves, and contains metrics of all stoves it contains
    Attributes: 
        stoves--a list of stove objects associated with this house
        name -- the name of the house, typically begins with the neighborhood designation
        area -- teh square footage of the house
        location -- latitude and longitude of the house location
        report -- a Report object for the house
        reportCollection -- a collection of report objects associated with a house
        
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

        