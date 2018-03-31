# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 19:12:01 2018

@author: Pikari
"""

import pandas as pd
import matplotlib.pyplot as plt

def RSI(code, number):
    close = pd.read_csv(code + '.csv', encoding='gbk', index_col='date', usecols=[0,4])
    close.index = pd.to_datetime(close.index)
    yield_rate = (close - close.shift(1)) / close.shift(1)
    yield_rate.columns = ['yield']
    data = pd.concat([close, yield_rate], axis=1)
    d = []
    
    for i in range(len(close)-number):
        temporary = data.iloc[i:i+number]
        down = sum(temporary[temporary['yield'] < 0]['close'])
        up = sum(temporary[temporary['yield'] > 0]['close'])
        rsi = 100 / (1 + up / down)
        d.append(rsi)
    
    plt.plot(list(close.index[number:]), d)

RSI('000002', 14)
