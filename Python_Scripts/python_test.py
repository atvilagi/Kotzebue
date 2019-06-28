from netCDF4 import Dataset
import multiprocessing as mp
import os
import pumapy as puma
import numpy as np
import csv
import matplotlib.pyplot as plt
from scipy import io as sio
#
#def Pt(a,b,c):
#    print(a,b,c)
#
#print(puma.indoorT(0))
#dirname = os.path.abspath(os.path.dirname(__file__))
#filename = os.path.join(dirname,'../Data/puma_unified_data.nc')
#print(filename)
#os.chdir('..')
#print(filename)
#
#a = Dataset(filename,'r')
#c = a['FBK001']['outdoor_temp'][:]
#if __name__ == '__main__':
#
#    test = [0,1,2,3,4,5,6,7,8,9]
#    pool = mp.Pool(mp.cpu_count())
#    for i in test:
#        pool.apply_async(Pt,args=(i,i,i))
##    pool.map_async(Pt,test)
#    pool.close()
#    pool.join()
#
#print(mp.cpu_count())
#
#b = (np.nan, 0, 1, 2)
#
#print(np.nan not in b)
#print(b)
#print(np.isnan(b))
#print(not True in np.isnan(b))
#print(True in np.isnan(c))

#with open('eggs.csv', 'w', newline='') as csvfile:
#    spamwriter = csv.writer(csvfile, dialect='excel')
#    spamwriter.writerow(['Spam'] * 5 + ['Baked Beans'])
#    spamwriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])

#os.chdir('../Data')
#file = Dataset('puma_unified_data.nc','r')

#clicks = file['FBK000']['clicks'][:]
#state = file['FBK000']['state'][:]
#
#for i in range(len(state)):
#    if state[i] != -1:
#        print(state[i],clicks[i])

#os.chdir('../Matlab/UnitOps')
#
#u1 = sio.loadmat('UBM719.mat')
#u2 = sio.loadmat('UXM719.mat')