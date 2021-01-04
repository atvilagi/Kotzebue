#Fuel Consumption Rate Functions for PuMA

#By T. Morgan
import pandas as pd

def gallons_consumed_per_month(df):
    gpm = df.groupby(df.index.to_period('M')).agg({'gallons': 'sum'})
    return gpm

def gallonsPerHour(fuelConsumption):
    '''
    calculates gallons consumed for each hour monitored
    :param fuelConsumption: A pandas Series with datetime index
    :return: dataframe with 1 column containing gallons per hour with datetime index
    '''
    return fuelConsumption.groupby(pd.Grouper(freq='H')).sum(min_count = 1)

def gallons_consumed_per_area(df,galColumn,area):
    '''calculates total gallons consumed per area
    :param: df is a pandas dataframe including a column representing gallons
    :param: galColumn is a string name of the column containing gallons
    :param: area float or int representing the area
    :return: float value representing the sum of gallons divided by area'''

    return df[galColumn].sum()/area
def gallons_per_hour_per_month_year(fuelConsomption):
    ''':param: fuelConsumption pandas series with datetime index and numeric data'''
    grouped = fuelConsomption.groupby(pd.Grouper(freq="M"))

    gph_my = pd.concat([gallonsPerHour(grouped)])

def gallons_per_day_and_per_month(df, galColumn):
    '''gallons consumed per day per month
     :param: df is a pandas dataframe including a column representing gallons and a datetime index
     :param: galColumn is a string name of the column containing gallons
     :return: pandas.Series of total gallons consumed each data and pandas.series of total gallons per month
    '''
    gpd = df[galColumn].groupby(pd.Grouper(freq='D')).sum(min_count=10) #days with fiewer than 10 fuel click records will by Nan
    gpm = gpd.groupby(pd.Grouper(freq='M')).agg(['mean', 'count'])
    return gpd, gpm

def gallons_per_heating_degree_day(dailydf,galColumn, hddColumn):
    '''Calculates the gallons per hdd for each day
    :param: dailydf is a dataframe with date index (one row for each date) and columns for gallons consumed and hdd
    :param: galColumn is the string name of the column containing fuel consumption in gallons
    :param: hddColumn is the string name of the column containing hdd
    :return: dataframe with date index of gallons per heat degree day'''

    dailydf['gphdd']=dailydf[galColumn]/dailydf[hddColumn]
    return dailydf

def weather_adjusted_gallons_consumed_per_month(df,temperatureData, galColumn):
    '''Weather adjusted gallons per month is the total gallons by day/ divided by the total temperature degree days.
    :param df is a dataframe with temperature and fuel_consumption columns and datetime.index
    :param temperatureCoumn is the string name of the column containing temperature in F
    :param galColumn is the string name of the column containing fuel consumption in gallons'''

    dailyTemp = temperatureData.groupby(pd.Grouper(freq='D')).mean() #daily outside temperature
    dailyGal = df.groupby(pd.Grouper(freq='D'))[galColumn].sum()#daily fuel consumption excluding na only days

    hdd = 65 - dailyTemp#put hdd in the daily dataframe
    hdd.name='hdd'
    dailydf = pd.concat([hdd,dailyGal],axis=1)
    dailydf['gphhd'] = dailydf[galColumn]/dailydf['hdd'] #gallons per hdd

    gphddpm = dailydf.groupby(pd.Grouper(freq='M')).agg({'gphhd': 'mean', 'fuel_consumption': 'count'})#Monthly means
    
    return gphddpm.loc[gphddpm['fuel_consumption'] >= 15, 'gphhd'] #return the series

def run_weather_adjusted_gallons_per_month(df):
    '''calls weather_adjusted_gallons_per_month with appropriate column names'''
    gphddpm = weather_adjusted_gallons_consumed_per_month(df,'outT','fuel_consumption')
    
    return gphddpm

