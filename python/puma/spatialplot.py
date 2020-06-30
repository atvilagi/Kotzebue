# Projet: fuelmeter-tools
# Created by: T.Morgan # Created on: 4/16/2020
# Purpose :  SpatialPlot

#import numpy as np

#import shapefile as shp
import matplotlib.pyplot as plt

import matplotlib.colors as mcolors
import matplotlib.cm as cm
import pandas as pd
import numpy as np
from seaborn import kdeplot
from seaborn import color_palette
import shapely.geometry
import pyproj
import yaml
import os
# import sklearn.neighbors as skn
# import sklearn.metrics as skm
# import sys
import csv
file_path = os.path.abspath(os.path.dirname(__file__))
#sys.path.append(os.path.join(file_path, '..'))


def makeGridValues(boundingBox):
    # Set up projections
    p_mt = pyproj.Proj(init='epsg:3338')  # out projection, metric Alaska Albers
    p_ll = pyproj.Proj(init='epsg:4326')  # in projection
    # Create corners of rectangle to be transformed to a grid
    nw = shapely.geometry.Point((boundingBox[2],boundingBox[3]))
    se = shapely.geometry.Point((boundingBox[0],boundingBox[1]))

    stepsize = 5000 # 5 km grid step size

    # Project corners to target projection
    s = pyproj.transform(p_ll, p_mt, nw.x, nw.y) # Transform NW point to 3338
    e = pyproj.transform(p_ll, p_mt, se.x, se.y) # .. same for SE

    s = (s[0] - 0.5* stepsize, s[1] - 0.5 * stepsize)

    # Iterate over 2D area
    gridpoints = []
    x = s[0]
    while x > e[0]:
        y = s[1]
        while y > e[1]:
            p = shapely.geometry.Point(pyproj.transform(p_mt, p_ll, x, y))
            gridpoints.append(p)
            y -= stepsize
        x -= stepsize

    with open('../../data/spatial/grid.csv', 'w+') as of:
        of.write('lon;lat\n')
        for p in gridpoints:
            of.write('{:f};{:f}\n'.format(p.x, p.y))
    return gridpoints

def makeGallons(startdf):

    p_aa = pyproj.CRS.from_epsg(3338).to_proj4()
    p_ll = pyproj.CRS.from_epsg(4326).to_proj4()
    # p_aa = pyproj.Proj(init='epsg:3338')  # out projection, metric Alaska Albers
    # p_ll = pyproj.Proj(init='epsg:4326')  # in projection
    newdf = pd.DataFrame(data=None, columns=['y', 'x'])
    for i in range(len(startdf)):
        fuel = startdf.loc[i,'fuel']
        for f in range(int(round(fuel * 100, 0))):
            points = pyproj.transform(p_ll, p_aa, startdf.loc[i, 'long'], startdf.loc[i, 'lat'])
            newdf = newdf.append({'y': points[1], 'x': points[0]}, ignore_index=True)
    return newdf

def plot_shape(id, sf, s=None):
    """ PLOTS A SINGLE SHAPE """
    p_aa = pyproj.CRS.from_epsg(3338).to_proj4()
    p_ll = pyproj.CRS.from_epsg(4326).to_proj4()
    shape_ex = sf.shape(id)
    x_lon = np.zeros((len(shape_ex.points),1))
    y_lat = np.zeros((len(shape_ex.points),1))
    for ip in range(len(shape_ex.points)):
        shape_ex.points[ip] = pyproj.transform(p_aa, p_ll, shape_ex.points[ip][0], shape_ex.points[ip][1])
        x_lon[ip] = shape_ex.points[ip][0]
        y_lat[ip] = shape_ex.points[ip][1]


    return x_lon,y_lat

def plot_map(sf, x_lim=None, y_lim=None, figsize=(11, 9)):
    '''
    Plot map with lim coordinates
    '''
    plt.figure(figsize=figsize)
    id = 0
    for shape in sf.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        plt.plot(x, y, 'k')

        if (x_lim == None) & (y_lim == None):
            x0 = np.mean(x)
            y0 = np.mean(y)
            plt.text(x0, y0, id, fontsize=10)
        id = id + 1

    if (x_lim != None) & (y_lim != None):
        plt.xlim(x_lim)
        plt.ylim(y_lim)
    plt.show()
    return

def writeHouseCSV(houses):
    '''writes a list of house tuples to a csv with specified colums'''
    path = os.path.join(file_path, '..', '..', 'data', 'text', 'puma-house_locations.csv')
    with open(path, 'w+', newline="") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['house','lat','long','fuel'])
        for t in houses:
            csv_writer.writerow([t[0],t[2][0],t[2][1],np.random.uniform(0.001, 0.2)])

def createHouseLocationCSV():

    houses_file = os.path.join(file_path, '..', '..', 'data', 'yaml', 'puma-houses.yml')
    with open(houses_file) as houses:
        yamh = yaml.load(houses)
        #report houses is a list of tuples with values for each house
        report_houses = [(yamh.get(i)['Stove'], yamh.get(i)['Square Footage'], yamh.get(i)['Location']) for i in yamh]
    writeHouseCSV(report_houses)



def makeGridCells(boundingBox):
    return
def simplifyRoads():

    rd_path = os.path.join(file_path, "../../data/spatial//FBKRoads.shp")
    roads = shp.Reader(rd_path)

    targetRoads = []
    for road in roads.shapeRecords():
        x_lon = []
        y_lat = []
        for ip in range(0,len(road.shape.points),100):
            #road.shape.points[ip] = pyproj.transform(p_mt, p_ll, road.shape.points[ip][0], road.shape.points[ip][1])
            x_lon.append(road.shape.points[ip][0])
            y_lat.append(road.shape.points[ip][1])
        #always include the last point
        # road.shape.points[len(road.shape.points) - 1] = pyproj.transform(p_mt, p_ll, road.shape.points[len(road.shape.points) - 1][0], road.shape.points[len(road.shape.points) - 1][1])
        # x_lon.append(road.shape.points[len(road.shape.points) - 1][0])
        # y_lat.append(road.shape.points[len(road.shape.points) - 1][1])
        targetRoads.append((road.record.Route_Name, np.array(x_lon), np.array(y_lat)))

    return targetRoads
def makeFuelConsumptionMap(housesdf):

    #TODO implement. For now calls temporary plot
    plotKernalDensity()
    return

def plotKernalDensity():
    p_aa = pyproj.CRS.from_epsg(3338).to_proj4()
    p_ll = pyproj.CRS.from_epsg(4326).to_proj4()  # in projection
    house_path = os.path.join(file_path,"../../data/text/puma-house_locations.csv")
    housesdf = pd.read_csv(house_path)
    #shp_path = os.path.join(file_path,"../../data/spatial//tl_2016_02_cousub/tl_2016_02_cousub.shp")
    #sf = shp.Reader(shp_path)

    #FBK = sf.shapes()[15]  # Fairbanks NorthStar Burough
    #x_lon, y_lat = plot_shape(15,sf)
    targetRoads = simplifyRoads()
    plotdf = makeGallons(housesdf)

    f, ax = plt.subplots(1, figsize=(9, 9))
    # ax.plot(x_lon, y_lat)
    for r in targetRoads:
        ax.plot(r[1], r[2],"k")

    d = sns.kdeplot(plotdf['x'], plotdf['y'], shade=True, ax=ax, legend=True,cmap="Blues")

    points = pyproj.transform(p_ll, p_aa, float(housesdf[housesdf.house=='FBK004']['long']), float(housesdf[housesdf.house=='FBK004']['lat']))
    ax.plot(points[0],points[1],"*",color='yellow',markersize=25)
    meanx = np.min(plotdf['x'])
    meany = (np.mean(plotdf['y']) + np.min(plotdf['y'])) /2
    plt.text(meanx,meany,"PLACE HOLDER \nNEIGHBORHOOD \nPLOT",fontsize=60, color='red')
    # use bbox (bounding box) to set plot limits
    plt.xticks([])
    plt.yticks([])
    plt.xlabel("")
    plt.ylabel("")

    plt.xlim(min(plotdf['x']),max(plotdf['x']))
    plt.ylim(min(plotdf['y']),max(plotdf['y']))
    plt.box(False)
    box = ax.get_position()
    #ax.set_position([box.x0 -0.1, box.y0, box.width, box.height])
    ax.set_position([box.x0, box.y0, box.width, box.height])
    b = sns.color_palette("Blues")[2]
    # setup the colorbar
    normalize = mcolors.Normalize(vmin=0, vmax=max(housesdf['fuel']))
    colormap = cm.get_cmap("Blues")
    scalarmappaple = cm.ScalarMappable(norm=normalize, cmap=colormap)
    scalarmappaple.set_array([0,0.7])
    plt.colorbar(scalarmappaple)

    #f.colorbar(leg)
    plt.legend()
    #f.show()
    plt.savefig(os.path.join(file_path,'../../reports/multiyear/FBK004/kde.png'))
    return
plotKernalDensity()
#createHouseLocationCSV()
# plt.plot(centroid).show()