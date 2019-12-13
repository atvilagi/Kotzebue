#Fuel Consumption Rate Functions for PuMA

#By T. Morgan


def gallons_consumed_per_month(df):
    gpm = df.groupby(df.index.to_period('M')).agg({'gallons': 'sum'})
    return gpm

def gallonsPerHour(fuelConsumption):
    '''
    calculates gallons consumed for each hour monitored
    :param fuelConsumption: A pandas Series with datetime index
    :return: dataframe with 1 column containing gallons per hour with datetime index
    '''
    return fuelConsumption.groupby(fuelConsumption.index.to_period('H')).sum()

def gallons_consumed_per_area(df,galColumn,area):
    '''calculates total gallons consumed per area
    :param: df is a pandas dataframe including a column representing gallons
    :param: galColumn is a string name of the column containing gallons
    :param: area float or int representing the area
    :return: float value representing the sum of gallons divided by area'''

    return df[galColumn].sum()/area

def gallons_per_day_and_per_month(df, galColumn):
    '''gallons consumed per day per month
     :param: df is a pandas dataframe including a column representing gallons and a datetime index
     :param: galColumn is a string name of the column containing gallons
     :return: pandas.Series of total gallons consumed each data and pandas.series of total gallons per month
    '''
    gpd = df.groupby(df.index.to_period('D')).agg({galColumn: 'sum'})
    gpm = gpd.groupby(gpd.index.month).agg({galColumn:'sum'})
    return gpd, gpm

def gallons_per_heating_degree_day(dailydf,galColumn, hddColumn):
    '''Calculates the gallons per hdd for each day
    :param: dailydf is a dataframe with date index (one row for each date) and columns for gallons consumed and hdd
    :param: galColumn is the string name of the column containing fuel consumption in gallons
    :param: hddColumn is the string name of the column containing hdd
    :return: dataframe with date index of gallons per heat degree day'''

    dailydf['gphdd']=dailydf[galColumn]/dailydf[hddColumn]
    return dailydf

def weather_adjusted_gallons_consumed_per_month(df,temperatureColumn, galColumn):
    '''Weather adjusted gallons per month is the total gallons by day/ divided by the total temperature degree days.
    :param df is a dataframe with temperature and fuel_consumption columns
    :param temperatureCoumn is the string name of the column containing temperature in F
    :param galColumn is the string name of the column containing fuel consumption in gallons'''

    dailydf = df.groupby(df.index.to_period('D')).agg({temperatureColumn: 'mean'}) #daily outside temperature
    dailydf[galColumn] = df.groupby(df.index.to_period('D')).agg({galColumn:'sum'}) #daily fuel consumption

    dailydf['hdd'] = 65 - dailydf[temperatureColumn]#put hdd in the daily dataframe
    dailydf['gphhd'] = dailydf[galColumn]/dailydf['hdd'] #gallons per hdd

    gphddpm = dailydf.groupby(dailydf.index.month).agg({'gphhd': 'mean'}) #average by month
    
    return gphddpm['gphhd'] #return the series

def run_weather_adjusted_gallons_per_month(df):
    '''calls weather_adjusted_gallons_per_month with appropriate column names'''
    gphddpm = weather_adjusted_gallons_consumed_per_month(df,'outT','fuel_consumption')
    
    return gphddpm

