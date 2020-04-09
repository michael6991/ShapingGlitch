# -*- coding: utf-8 -*-
"""Core Genetic Algorithm classes.

Contents
--------

Various glitch shapes. Each chromosome in the initial population will randomly
choose one of these shapes to start with

"""
from math import ceil, floor



def rect_pulse_shape(length, N, high, low):
    """
    simple rectangular pulse
   _________               _________high
            |             |
            |_____________|low
        <------- length ----->
         
         timing of glitch from t=0
         glitch length (in ns)
         N shape points
         
    """
    
    t_res = length / N
    shape = [(0, 0) for _ in range(0, N)]  # (time, value)
    
    shape[0] = t_res, high
    shape[N - 1] = t_res * (N), high
    
    for n in range(1, N - 1):
        shape[n] = t_res * (n + 1), low
    
    return shape
    
    
    
def v_pulse_shape(length, N, high, low):
    """
    simple V pulse
   _________        _________high
            \      /
             \    /
              \  /
               \/ low
           <--- length --->
         
         timing of glitch from t=0
         glitch length (in ns)
         N shape points
         
    """
    
    t_res = length / N    
    shape = [(0, 0) for _ in range(0, N)]  # (time, value)
   
    center_point = floor(N / 2.0)
    
    
    if N % 2 == 0:
        center_point -= 1
    
        # y = ax + b
        a = (high - low) / (0 - center_point)   # negative gradient
        b = high
        for n in range(0, center_point):
            shape[n] = t_res * (n + 1), (a * n) + b
        
        # y = a(x - N/2)
        a = -1 * a  # same gradient as before but positive 
        for n in range(center_point, N - 1):
            shape[n] = t_res * (n + 1), (a * (n - floor(N / 2) + 1))
        
        shape[-1] = (length, high)  # set the final point to be same as previous
    
    else:
        
        # y = ax + b
        a = (high - low) / (0 - center_point)   # negative gradient
        b = high
        for n in range(0, center_point):
            shape[n] = t_res * (n + 1), (a * n) + b
        
        # y = a(x - N/2)
        a = -1 * a  # same gradient as before but positive 
        for n in range(center_point, N):
            shape[n] = t_res * (n + 1), (a * (n - floor(N / 2)))
        
        
    return shape


# test code
# a = rect_pulse_shape(200, 16, 100, 0)
s = v_pulse_shape(200, 10 , 10, 0)
print(s) 
t = [s[i][0] for i in range(0, len(s))]
v = [s[i][1] for i in range(0, len(s))]

import matplotlib.pyplot as plt
plt.figure()
plt.plot(t, v)
plt.grid(True)
plt.show()




