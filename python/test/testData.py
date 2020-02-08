# Projet: fuelmeter-tools
# Created by: # Created on: 12/1/2019
# Purpose :  testData

from python.puma.PumaData import PumaData
import pandas as pd
import numpy as np


def makeTestData(myData):

    #df 1 is complete dataset no mising timesteps
    date_rng = pd.date_range(start='1/1/2018', end='1/08/2018', freq='H')
    cum_clicks = np.arange(1,len(date_rng) + 1)
    state = np.random.randint(0,4,size=(len(date_rng)))
    thermistor = np.random.randint(60,75, size = (len(date_rng)))
    df1 = pd.DataFrame({'a':date_rng, 'b':cum_clicks, 'c':state, 'd':thermistor})
    df1.columns = ['stove_time', 'state', 'cumulative_clicks', 'thermistor']

    #df 2 has missing timestamps and 3 more clicks per timeinterval than df1
    date_rng = pd.date_range(start='1/1/2018', end='1/08/2018', freq='H')
    cum_clicks = np.arange(1,len(date_rng)*3 + 1,3)
    state = np.random.randint(0,4,size=(len(date_rng)))
    thermistor = np.random.randint(60,75, size = (len(date_rng)))
    df2 = pd.DataFrame({'a':date_rng, 'b':cum_clicks, 'c':state, 'd':thermistor})
    df2.columns = ['stove_time', 'state', 'cumulative_clicks', 'thermistor']
    df2 = df2.drop([10,20,30],axis = 0)

    myData.df_dictionary = {'FBK011':df1,'FBK016':df2}
    return myData

# def test_testMakeData():
#     myData = data()
#     myData = makeTestData(myData)
#     assert(2 == len(myData.df_dictionary.keys()))
#
def test_puma2uni_nc():
    myData = PumaData()
    myData.puma2uni_nc()
