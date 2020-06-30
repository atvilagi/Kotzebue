# Projet: fuelmeter-tools
# Created by: # Created on: 4/10/2020
# Purpose :  stats

import statsmodels.api as sm #needs to be version 0.10.2 so it can work with numpy 1.13.3 . Any higher version of numpy won't work with netcdf
import statsmodels.formula.api as smf

def getlmm(model,data,groupColumns):
    md = smf.mixedlm(model, data, groups=data[groupColumns])
    mdf = md.fit()
    return mdf

def getGLM(x,y):
    md = sm.GLM(y,x,family=sm.families.Gaussian())
    fitModel = md.fit()
    return fitModel

def getNewY(model,newdata):
   outy =  model.predict(newdata)
   return outy