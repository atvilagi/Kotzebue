# Project: fuelmeter-tools
# Created by:T.Morgan # Created on: 12/3/2019
import numpy as np
import pandas as pd
#import puma.stats as stats
import os
class Neighborhood:
    """
    Description: A group of houses and associated metrics for that group of houses
    Attributes: 
        name-- name of the neighborhood. Generally a prefix also associated with house names.
        houses--list of houses belongint to a neightobrood.
        
    """

    def __init__(self,name,houses):
        self.name = name
        self.houses = houses #list of House objects in a neighborhood

    def addHouse(self,house):
        '''add a house to the neighborhood'''
        self.houses.append(house)

    def getTotalGallons(self,excludeHouses):
        '''get the total gallons consumed in a neighborhood for a report period
        :param: excludeHouses -- a list of houses that won't be included in the sum'''
        tg = sum([h.report.total_gallons for h in self.houses if (h.name not in excludeHouses) & (h.report is not None)])
        return tg
    def getTotalArea(self,excludeHouses):
        '''get the sum square footage for all houses combined in the neighborhood, except for houses in the excludeHouses list
        :param: excludeHouses -- a list of houses that won't be included in the sum'''
        area = sum([h.report.area for h in self.houses if (h.name not in excludeHouses) & (h.report is not None)])
        return area

    def applyStatsModels(self):
        '''calls statistical models run in R to model fuel consumption in relation to indoor
        and outdoor temperature and seperately model fuel consumption based on location.
        Two seperate R scripts are used, one for spatial modeling, one for temperature.'''
        import subprocess
        #R is used for modeling with gamms and glmms

        self.writeNeigborhoodStatsInput() #write a combined text file for all houses
        processPath = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','R')      #path to R scripts
        rscript = "model_data.r"
        rsource = os.path.join(processPath, rscript)
        subprocess.call(["RScript",rsource]) #images are placed in report folders
        #subprocess.call(["C:\\Program Files\\R\\R-4.0.0\\bin\\x64\\RScript", "--vanilla", rsource],shell=True)  # images are placed in report folders

        # generate the glmm spatial pngs

        rscript = "spatial_model.R"
        rsource = os.path.join(processPath, rscript)
        subprocess.call(["RScript", rsource])
        #subprocess.call(["C:\\Program Files\\R\\R-4.0.0\\bin\\x64\\RScript", "--vanilla", rsource], shell=True)

        return

    def writeNeigborhoodStatsInput(self):
        '''coellesces necessary data for stats models into a csv file'''
        filename = 'multiStoveInput.csv'
        with open(os.path.join(*[os.getcwd(),"..","..","data","text"],filename), "w+") as outfile:
            outfile.write("date," + ",".join(self.houses[0].report.statsInput.columns))
            outfile.write("\n")

        for h in self.houses:
            try:
                h.report.statsInput.to_csv(os.path.join(*[os.getcwd(),"..","..","data","text"],filename), mode='a', header=False)
            except Exception as e:
                print(h.name)
                print(e)
        return

    def getUsageTable(self,excludeHouses):
        '''Generates a data frame with location information and fuel consumption for each house in the neightborhood
        excludeHouses are not included in the dataframe'''
        newdf = pd.DataFrame(data=None, columns=['house', 'lat','long','fuel'])
        houses = [{'house':h.name,'lat':h.location[1],'long':h.location[0], 'fuel':h.report.getMeanGallonsPerMonthPerAreaByYear().mean()} for h in self.houses if (h.name not in excludeHouses) & (h.report is not None)]
        for h in houses:
            newdf = newdf.append(h, ignore_index=True)
        return newdf
    def getMeanGallonsPerFt(self,excludeHouses):
        '''Generate metrics for average fuel consumption and standard deviation of the sample in fuel consumption'''
        mg = np.nanmean([h.report.gallons_per_ft for h in self.houses if (h.name not in excludeHouses) & (h.report is not None)])
        std= np.nanstd([h.report.gallons_per_ft for h in self.houses if (h.name not in excludeHouses) & (h.report is not None)])
        return mg,std
    def getMeanMonthlyGPFByYear(self,excludeHouses):
        '''Generate pandas series of mean and standard deviation in gallons per month per area
        for each year of data for all houses in the neightborhood combined'''
        mg = pd.concat([h.report.getMeanGallonsPerMonthPerAreaByYear() for h in self.houses if (h.name not in excludeHouses) & (h.report is not None)])
        mgy = mg.groupby(pd.Grouper(freq="Y")).mean()
        std = mg.groupby(pd.Grouper(freq="Y")).std()
        mgy.name = 'meanfuelPerMonthPerArea'
        std.name = 'stdfuelPerMonthPerArea'
        return mgy,std

