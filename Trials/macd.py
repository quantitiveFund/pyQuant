# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 14:33:43 2018

@author: Pikari
"""

from EMA import *
import pandas as pd
import matplotlib.pyplot as plt

def MACD(code, day1, day2, day3):
    DIF = EMA(code, day1) - EMA(code, day2)
    DEM = EMA(code, day3)
    for i in range(1, len(DIF)):
        DEM.iloc[i] = DIF.iloc[i] * 2 / (day3+1) + DEM.iloc[i-1] * (day3-1) / (day3+1)
    OSC = (DIF - DEM) * 2
    
    plt.bar(list(OSC.index), list(OSC['close']))
    
    return OSC

macd = MACD('000002', 12, 26, 9)
