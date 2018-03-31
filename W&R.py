# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 20:34:10 2018

@author: Pikari
"""

import pandas as pd
import matplotlib.pyplot as plt

def WR(code, day):
    data = pd.read_csv(code + '.csv', encoding='gbk', index_col='date', usecols=[0,2,3,4])
    data.index = pd.to_datetime(data.index)
    wr = data.close
    
    for i in range(day, len(data)):
        max_price = max(data.high[i-day:i])
        min_price = min(data.low[i-day:i])
        wr[i] = 100 * (max_price - data.close[i]) / (max_price - min_price)
    
    plt.plot(wr[day:])    
    return wr[day:]
    
wr = WR('000002', 4)
