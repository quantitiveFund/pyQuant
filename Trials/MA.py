# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 19:03:12 2018

@author: Pikari
"""

import pandas as pd
import matplotlib.pyplot as plt

#均线函数

def MA(code, day):
    data = pd.read_csv(str(code + '.csv'), encoding='gbk', index_col='date', usecols=[0, 4])
    data.index = pd.to_datetime(data.index)
    madata = data
    
    for i in range(1, day):
        madata = madata + data.shift(i)
    
    ma = madata / day
    plt.plot(ma)
    return ma
    
five_MA = MA('000002', 5)
ten_MA = MA('000002', 10)

#五日均价超过十日均价，第二天开盘价买入，五日均价跌破十日均价，第二天收盘价卖出

open = pd.read_csv('000002.csv', encoding='gbk', index_col='date', usecols=[0, 1])
close = pd.read_csv('000002.csv', encoding='gbk', index_col='date', usecols=[0, 4])
buy = pd.DataFrame(index=['date'], columns=['open'])
sell = pd.DataFrame(index=['date'], columns=['close'])

money = 1000000
position = 1
win = 0 #盈利计数
lose = 0 #亏损计数

for i in range(0, len(open)):
    if five_MA.iloc[i][0] > ten_MA.iloc[i][0]:
        while money > 0:
            cost = open.iloc[i+1][0]
            position = money / open.iloc[i+1][0]
            money = 0
    else:
        while money == 0:
            money = position * close.iloc[i+1][0]
            position = 0
            if close.iloc[i+1][0] > cost:
                win += 1
            else:
                lose += 1
            
print(money)
print(position)
print(win)
print(lose)
print(len(five_MA > ten_MA))
