#Signal Processing Functions for PuMA

import scipy.stats as stats
import numpy as np
from netCDF4 import Dataset

def moving_median(f,N):
    
    mm = np.zeros(f.size)
    
    for i in range(f.size):
        if i < N:
            m = []
            for j in range(i+N+1):
                if np.isfinite(f[j]):
                    m.append(f[j])
            m = np.array(m)
            mm[i] = np.median(m)
        elif i+N > f.size-1:
            m = []
            for j in range(i-N,f.size):
                if np.isfinite(f[j]):
                    m.append(f[j])
            m = np.array(m)
            mm[i] = np.median(m)
        else:
            mm[i] = np.median(f[i-N:i+N+1][np.where(np.isfinite(f[i-N:i+N+1]))[0]])
        
    return mm

def linear_regression2line(x,y):
    
    linreg = stats.linregress(x,y)
    
    def line(linreg,x):
        return linreg[0]*x + linreg[1]
    
    x_line = np.array([np.nanmin(x),np.nanmax(x)])        
    y_line = np.array([line(linreg,x_line[0]),line(linreg,x_line[1])])
    slope = linreg[0]
    intercept = linreg[1]
    rvalue = linreg[2]
    
    return x_line, y_line, slope, intercept, rvalue