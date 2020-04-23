# -*- coding: utf-8 -*-
"""Core Genetic Algorithm classes.

Contents
--------

Various glitch shapes. Each chromosome in the initial population will randomly
choose one of these shapes to start with

"""
from math import ceil, floor, sin, pi


basic_shapes = ("rect", "v", "sine")


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
    shape = [[0, 0] for _ in range(0, N)]  # (time, value)
    
    shape[0] = [t_res, high]
    shape[N - 1] = [t_res * (N), high]
    
    for n in range(1, N - 1):
        shape[n] = [t_res * (n + 1), low]
    
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
    shape = [[0, 0] for _ in range(0, N)]  # (time, value)
   
    center_point = floor(N / 2.0)
    
    
    if N % 2 == 0:
        center_point -= 1
    
        # y = ax + b
        a = (high - low) / (0 - center_point)   # negative gradient
        b = high
        for n in range(0, center_point):
            shape[n] = [t_res * (n + 1), (a * n) + b]
        
        # y = a(x - N/2) + b
        a = -1 * a  # same gradient as before but positive 
        b = low
        for n in range(center_point, N - 1):
            shape[n] = [t_res * (n + 1), (a * (n - center_point) + b)]
        
        shape[-1] = [length, high]  # set the final point to be same as previous
    
    else:
        # y = ax + b
        a = (low - high) / (center_point - 0)   # negative gradient
        b = high
        for n in range(0, center_point):
            shape[n] = [t_res * (n + 1), (a * n) + b]
        
        # y = a(x - N/2) + b
        a = -1 * a  # same gradient as before but positive 
        b = low
        for n in range(center_point, N):
            shape[n] = [t_res * (n + 1), (a * (n - center_point) + b)]
        
        
    return shape


def sine_shape(length, N, high, low):
    """
    single cycle sine
   
      * *  high
    *     *
   *-------*-------*----- VCC idle
            *     *
              * *  
            
   <--- length --->  single cycle

         timing of glitch from t=0
         glitch length (in ns)
         N shape points
         
    """
    
    t_res = length / N
    shape = [(0, 0) for _ in range(0, N)]  # (time, value)
    
    # simple sin
    # for n in range(0, N):
    #         shape[n] = t_res * (n + 1), high * sin((n + 1) * phase)
    # return shape   
        
    center_point = floor(N / 2.0)
    phase = 2*pi / N
  
    # y = high*sin(x)
    for n in range(0, center_point):
        shape[n] = t_res * (n + 1), high * round(sin((n + 1) * phase), 3)
    
    # shape[center_point] = t_res * (center_point + 1), 0  # phase = pi
    
    # y = low*sin(x)
    for n in range(center_point, N):
        shape[n] = t_res * (n + 1), low * round(sin((n + 1) * phase), 3)

    # round the values to 3 digits after decimal point
    return shape
    


def choose_shape(shape=str, *args):
    """
    executes a function from the above based on a chosen shape
    from the tuple: basic_shapes

    Parameters
    ----------
    shape : TYPE, optional
        Name of a chosen shape
    *args : TYPE
        length, N, high, low
    """
    print("Chossen shape: %s" % shape)
    print("N sample points: %d" % args[1])
    if shape == "rect":
        return rect_pulse_shape(*args)
    elif shape == "v":
        return v_pulse_shape(*args)
    elif shape == "sine":
        return sine_shape(*args)
    else:
        raise ("Specified shape does not exist")



# test code
def test():
    # s = rect_pulse_shape(200, 16, 10, 0)
    # s = v_pulse_shape(200, 13 , 5.5, 3.4)
    s = sine_shape(200, 12, 5.5, 3.4) 
    print(s) 
    t = [s[i][0] for i in range(0, len(s))]
    v = [s[i][1] for i in range(0, len(s))]
    
    import matplotlib.pyplot as plt
    plt.figure()
    plt.plot(t, v)
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    test()



