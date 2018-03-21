# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 19:27:51 2018

@author: Pikari
"""

import pandas as pd
import matplotlib.pyplot as plt

def VA(code):
    data = pd.read_csv(code + '.csv', encoding='gbk', index_col='date', usecols=[0,2,3,4,5])
    data.index = pd.to_datetime(data.index)
    va = data.volume * ((data.close - data.low) / (data.high - data.close) - 1)
    plt.plot(va)
    return va
    
def OBV(code):
    data = pd.read_csv(code + '.csv', encoding='gbk', index_col='date', usecols=[0,4,5])
    data.index = pd.to_datetime(data.index)
    
    for i in range(1, len(data)):
        if data.close[i] > data.close[i-1]:
            data.volume[i] = data.volume[i-1] + data.volume[i]
        else:
            data.volume[i]= data.volume[i-1] - data.volume[i]
            
    plt.plot(data.volume)
    return data.volume

obv = OBV('000002')
va = VA('000002')
