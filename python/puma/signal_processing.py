"""
Signal Processing Functions for PuMA

By Doug Keller
"""

import scipy.stats as stats
import numpy as np

def moving_median(f,N):
    """
    Returns the moving median array of an array.
    
    Arguments:
        f -- 1D numpy array of numbers
        N -- median filter order
        
    Returns:
        mm -- moving median filtered array
        
    This function is a moving median filter that runs over a window of 2N + 1 elements along an n element long array with the given N order. The window is centered on the n element and the median of the window replaces the n element. The elements within N elements of the end points are treated slightly differently with a reduced window size.
    """
    
    mm = np.zeros(f.size)
    
    for i in range(f.size): #running the median filter window
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
    """
    Returns the linear regression info and line from a given function.
    
    Arguments:
        x -- independent variable array
        y -- dependent variable array
        
    Returns:
        x_line -- beginning and end points of the x array
        y_line -- beginning and end points of the linear regression line based on the y array at the x_line locations
        slope -- slope of the linear regression line
        intercept -- intercept of the linear regression line
        rvalue -- r value of the linear regression line
        
    This function takes the dependent and independent arrays of a function set and produces the components and plot information of the linear regression of the data for easy plotting and labelling.
    """
    
    linreg = stats.linregress(x,y) #linear regression performed
    
    def line(linreg,x): #forming linear regression equation to be applied
        return linreg[0]*x + linreg[1]
    
    x_line = np.array([np.nanmin(x),np.nanmax(x)]) #setting the return values
    y_line = np.array([line(linreg,x_line[0]),line(linreg,x_line[1])])
    slope = linreg[0]
    intercept = linreg[1]
    rvalue = linreg[2]
    
    return x_line, y_line, slope, intercept, rvalue