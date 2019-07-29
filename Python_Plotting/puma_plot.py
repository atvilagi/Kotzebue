#PuMA plotting module

import numpy as np
import matplotlib.pyplot as plt

def time2theta_time(t,t_ind):
    # expecting seconds
    day = 86400 #seconds in a day
    flag = np.where(t<t[t_ind]+day)[0]
        
#    t_theta = t[t_ind:t_ind+i]*2*np.pi/day
    
#    print(i)
#    return t_theta,i    
    return flag
    
def polar_temp():
    pass