from netCDF4 import Dataset
import multiprocessing as mp
import os
import pumapy as puma
import numpy as np

def Pt(a,b,c):
    print(a,b,c)

print(puma.indoorT(0))
dirname = os.path.abspath(os.path.dirname(__file__))
filename = os.path.join(dirname,'../Data/puma_unified_data.nc')
print(filename)
os.chdir('..')
print(filename)

a = Dataset(filename,'r')
c = a['FBK001']['outdoor_temp'][:]
if __name__ == '__main__':

    test = [0,1,2,3,4,5,6,7,8,9]
    pool = mp.Pool(mp.cpu_count())
    for i in test:
        pool.apply_async(Pt,args=(i,i,i))
#    pool.map_async(Pt,test)
    pool.close()
    pool.join()

print(mp.cpu_count())

b = (np.nan, 0, 1, 2)

print(np.nan not in b)
print(b)
print(np.isnan(b))
print(not True in np.isnan(b))
print(True in np.isnan(c))
