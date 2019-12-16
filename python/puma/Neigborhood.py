# Projet: fuelmeter-tools
# Created by:T.Morgan # Created on: 12/3/2019
import numpy as np
class Neighborhood:
    """
    Description: A group of houses and associated metrics for that group of houses
    Attributes: 
        name, houses
        
    """

    def __init__(self,name,houses):
        self.name = name
        self.houses = houses #list of House objects in a neighborhood

    def addHouse(self,house):
        self.houses.append(house)

    def getTotalGallons(self,excludeHouses):
        tg = sum([h.report.total_gallons for h in self.houses if h.name not in excludeHouses])
        return tg
    def getTotalArea(self,excludeHouses):
        area = sum([h.report.gallons_per_ft for h in self.houses if h.name not in excludeHouses])
        return area
    def getMeanGallonsPerFt(self,excludeHouses):
        mg =  np.mean([h.report.gallons_per_ft for h in self.houses if h.name not in excludeHouses])
        std= np.std([h.report.gallons_per_ft for h in self.houses if h.name not in excludeHouses])
        #TODO implement confidence intervals -stdev is not meaninful
        return mg,std



        