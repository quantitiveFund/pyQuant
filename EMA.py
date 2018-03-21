# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 15:18:02 2018

@author: Pikari
"""

import pandas as pd
import matplotlib.pyplot as plt

#指数移动平均

def EMA(code, day):
    close = pd.read_csv(code + '.csv', encoding='gbk', index_col='date', usecols=[0,4])
    close.index = pd.to_datetime(close.index)
    ema = close
    
    #效率略低
    for i in range(1, len(close)):
        ema.iloc[i] = close.iloc[i] * 2 / (day+1) + ema.iloc[i-1] * (day-1) / (day+1)
    
    plt.plot(ema)
    
    return ema

twelve_ema = EMA('000002', 12)
