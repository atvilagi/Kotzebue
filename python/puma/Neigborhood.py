# Projet: fuelmeter-tools
# Created by:T.Morgan # Created on: 12/3/2019
import numpy as np
class Neighborhood:
    """
    Description: A group of houses and associated metrics for that group of houses
    Attributes: 
        name, houses,reports
        
    """

    def __init__(self,name,houses):
        self.name = name
        self.houses = houses #list of House objects in a neighborhood
        self.reports = {} #a neighborhood has a collection of Reports on the houses contained

    def addReport(self,houseName,report):
        self.reports[houseName]=report

    def getTotalGallons(self,excludeHouses):
        tg = sum([r.total_gallons for k,r in self.reports.items() if k not in [h.name for h in excludeHouses]])
        return tg
    def getTotalArea(self,excludeHouses):
        area = sum([r.total_gallons for k, r in self.reports.items() if k not in [h.name for h in excludeHouses]])
        return area
    def getMeanGallonsPerFt(self,excludeHouses):
        mg =  np.mean([r.gallons_per_ft for k,r in self.reports.items() if k not in [h.name for h in excludeHouses]])
        std= np.std([r.gallons_per_ft for k, r in self.reports.items() if k not in [h.name for h in excludeHouses]])
        #TODO implement confidence intervals -stdev is not meaninful
        return mg,std



        