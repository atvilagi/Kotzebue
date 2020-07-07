# Projet: fuelmeter-tools
# Created by:T.Morgan # Created on: 12/3/2019
import numpy as np
import pandas as pd
import puma.stats as stats
import os
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
        tg = sum([h.report.total_gallons for h in self.houses if (h.name not in excludeHouses) & (h.report is not None)])
        return tg
    def getTotalArea(self,excludeHouses):
        area = sum([h.report.area for h in self.houses if (h.name not in excludeHouses) & (h.report is not None)])
        return area

    def applyStatsModels(self):
        import subprocess
        #R is used for modeling with gamms and glmms
        self.writeNeigborhoodStatsInput() #write a combined text file for all houses
        processPath = "..\\..\\R"       #path to R scripts
        rscript = "model_data.r"
        rsource = os.path.join(processPath, rscript)
        subprocess.call(["C:\\Program Files\\R\\R-4.0.0\\bin\\x64\\RScript", "--vanilla", rsource], shell=True) #images are placed in report folders

        # generate the glmm spatial pngs
        processPath = "..\\..\\R"
        rscript = "spatial_model.R"
        rsource = os.path.join(processPath, rscript)

        subprocess.call(["C:\\Program Files\\R\\R-4.0.0\\bin\\x64\\RScript", "--vanilla", rsource], shell=True)

        return
    def writeNeigborhoodStatsInput(self):

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
    # def getAveMonthlyPerFtByYear(self,excludeHouses):
    #     df = pd.concat([h.report.gpm/h.report.area for h in self.houses if h.name not in [h.name for h in excludeHouses]],0)
    #     meanByYear = df.groupby(df.index.year).mean()
    #     meanByYear.name = 'fuelPerMonthPerArea'
    #     return meanByYear
    def getUsageTable(self,excludeHouses):
        newdf = pd.DataFrame(data=None, columns=['house', 'lat','long','fuel'])
        houses = [{'house':h.name,'lat':h.location[1],'long':h.location[0], 'fuel':h.report.getMeanGallonsPerMonthPerAreaByYear().mean()} for h in self.houses if (h.name not in excludeHouses) & (h.report is not None)]
        for h in houses:
            newdf = newdf.append(h, ignore_index=True)
        return newdf
    def getMeanGallonsPerFt(self,excludeHouses):
        mg = np.nanmean([h.report.gallons_per_ft for h in self.houses if (h.name not in excludeHouses) & (h.report is not None)])
        std= np.nanstd([h.report.gallons_per_ft for h in self.houses if (h.name not in excludeHouses) & (h.report is not None)])
        #TODO implement confidence intervals -stdev is not meaninful
        return mg,std
    def getMeanMonthlyGPFByYear(self,excludeHouses):
        mg = pd.concat([h.report.getMeanGallonsPerMonthPerAreaByYear() for h in self.houses if (h.name not in excludeHouses) & (h.report is not None)])
        mgy = mg.groupby(pd.Grouper(freq="Y")).mean()
        std = mg.groupby(pd.Grouper(freq="Y")).std()
        mgy.name = 'meanfuelPerMonthPerArea'
        std.name = 'stdfuelPerMonthPerArea'
        return mgy,std
    def calculateSpatialFuelConsumptionModel(self):
        '''Used a generalized linear mixed effects model to calculate the affect of geographic location on monthly fuel consumption
        consumption =~ lat + long | month'''
        def makeSpatialDataframe():
            df = pd.concat([pd.DataFrame({'stove':[h.name]*len(h.report.gpm),'month':h.report.gpm.index.month,'gpmpf':(h.report.gpm / h.report.area),'lat':[h.location[0]] * len(h.report.gpm), 'long':[h.location[1]] * len(h.report.gpm)},index = h.report.gpm.index) for h in self.houses if h.name ], 0)
            df = df[pd.notnull(df.gpmpf)]
            return df #TODO need to aggregate month values

        df = makeSpatialDataframe()
        self.lmm =stats.getlmm("gpmpf ~lat+long",df,['month'])
        #self.gamm =
        return

    def applyModelToRegion(self,model,df):
        df['fuel'] = model.predict(df)
        return df